import aiohttp, datetime, asyncio

from gql import gql, Client
from gql.transport.websockets import WebsocketsTransport

from helpers import get_argument
from mqtt import Mqtt
from logger import *

class Tibberlive:
    def __init__(self, config: dict, mqtts: list):

        home = get_argument(config, 'home', varname="T2M_TIBBER_HOME")
        self.__token = get_argument(config, 'token', varname="T2M_TIBBER_TOKEN")

        self.__available_request = {
            'query': '{ viewer { home(id: "%s") { features { realTimeConsumptionEnabled } } websocketSubscriptionUrl } }' % home
        }
        self.__subscription_request = gql('subscription{ liveMeasurement( homeId:"%s" ) { timestamp power } }' % home)

        self.__client = None
        self.__task = None

        self.__mqtts = mqtts

        self.__last_timestamp = datetime.datetime.fromtimestamp(0)

    async def start(self):
        logger.log(f'Subscribing to tibber live data.')
        async with aiohttp.ClientSession() as session:
            try:
                response_json = await self.__post(session, self.__available_request)
            except Exception as e:
                logger.log(f'Subscription to tibber live data failed: {e}')
                return False
            available = response_json['data']['viewer']['home']['features']['realTimeConsumptionEnabled']
            subscription_url = response_json['data']['viewer']['websocketSubscriptionUrl']
            if not available:
                logger.log('No tibber live data available .')
                return False
            
            transport = WebsocketsTransport(
                url=subscription_url,
                init_payload={'token': self.__token},
                headers={'User-Agent': 'HomeAssistant/2023.2'})

            self.__client = Client(transport=transport)
            await self.__client.connect_async(reconnecting=True)

            self.__task = asyncio.create_task(self.__run())
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
            logger.log(f'Receiving live data failed: {e}')

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

    