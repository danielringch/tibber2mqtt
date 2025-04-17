import aiohttp, asyncio, datetime, logging

from gql import gql, Client
from gql.transport.websockets import WebsocketsTransport

from helpers import get_argument, get_optional_argument, walk_tree

_TIMESTAMP_DISCONNECTED = datetime.datetime.min

class Tibberlive:
    def __init__(self, config: dict, mqtts: list):

        home = get_argument(config, 'home', varname="T2M_TIBBER_HOME")
        self.__token = get_argument(config, 'token', varname="T2M_TIBBER_TOKEN")
        self.__api_timeout = int(get_optional_argument(config, 'api_timeout', default=5))
        self.__websocket_timeout = int(get_optional_argument(config, 'websocket_timeout', default=30))

        self.__available_request = {
            'query': '{ viewer { home(id: "%s") { features { realTimeConsumptionEnabled } } websocketSubscriptionUrl } }' % home
        }
        self.__subscription_request = gql('subscription{ liveMeasurement( homeId:"%s" ) { timestamp power } }' % home)

        self.__client = None
        self.__task = None

        self.__mqtts = mqtts

        self.__last_timestamp = _TIMESTAMP_DISCONNECTED

    async def start(self):
        logging.info(f'Subscribing to tibber live data')
        async with aiohttp.ClientSession() as session:
            try:
                async with asyncio.timeout(self.__api_timeout):
                    response_json = await self.__post(session, self.__available_request)
            except asyncio.TimeoutError:
                logging.error(f'Subscription to tibber live data failed: available request timeout')
                return False
            except Exception as e:
                logging.error(f'Subscription to tibber live data failed: {e}')
                return False
            available = walk_tree(response_json, 'data', 'viewer', 'home', 'features', 'realTimeConsumptionEnabled')
            subscription_url = walk_tree(response_json, 'data', 'viewer', 'websocketSubscriptionUrl')
            if not (available and subscription_url):
                logging.error('No tibber live data available')
                return False
            logging.debug(f'Live data available at url {subscription_url}')
            
            transport = WebsocketsTransport(
                url=subscription_url,
                init_payload={'token': self.__token},
                headers={'User-Agent': 'HomeAssistant/2023.2'})

            self.__client = Client(transport=transport)
            try:
                async with asyncio.timeout(self.__websocket_timeout):
                    await self.__client.connect_async(reconnecting=True)
            except asyncio.TimeoutError:
                logging.error(f'Subscription to tibber live data failed: websocket timeout')
                await self.__client.close_async()
                return False

            self.__task = asyncio.create_task(self.__run())
            logging.debug('Receive loop started')
            self.__last_timestamp = datetime.datetime.now()
        return True

    async def stop(self):
        if self.__task is not None:
            self.__task.cancel()
            self.__task = None
        if self.__client is not None:
            await self.__client.close_async()
            self.__client = None

    @property
    def connected(self):
        return self.__last_timestamp > _TIMESTAMP_DISCONNECTED

    @property
    def last_data(self):
        return self.__last_timestamp
    
    async def __run(self):
        try:
            async for response in self.__client.session.subscribe(self.__subscription_request):
                self.__last_timestamp = datetime.datetime.now()
                power = response['liveMeasurement']['power']
                for mqtt in self.__mqtts:
                    mqtt.send(round(power + 0.5))
        except Exception as e:
            logging.error(f'Receiving live data failed: {e}')
            self.__last_timestamp = _TIMESTAMP_DISCONNECTED

    async def __post(self, session, query):
        headers = {
            'Authorization': f'Bearer {self.__token}',
            'Content-Type': 'application/json'
        }
        async with session.post('https://api.tibber.com/v1-beta/gql', json=query, headers=headers) as response:
            response_json = await response.json()
            status = response.status
        if not (status >= 200 and status <= 299):
            raise Exception(status)
        return response_json

    