import aiohttp, datetime, tibber, threading, asyncio
from enum import Enum

from helpers import get_argument
from mqtt import Mqtt
from logger import *

class Tibberlive:
    def __init__(self, config: dict, mqtts: list):

        home = get_argument(config, ('home'), "T2M_TIBBER_HOME")
        self.__token = get_argument(config, ('token'), "T2M_TIBBER_TOKEN")

        self.__available_request = {
            'query': '{ viewer { home(id: "%s") { features { realTimeConsumptionEnabled } } } }' % home
        }
        self.__subscription_request = {
            'query': 'subscription{ liveMeasurement( homeId:"%s" ) { timestamp power } }' % home
        }

        self.__home = None

        self.__mqtts = mqtts

        self.__last_timestamp = datetime.datetime.fromtimestamp(0)

    def __del__(self):
        self.stop()

    async def start(self):
        logger.log(f'Subscribing to tibber live data.')
        async with aiohttp.ClientSession() as session:
            try:
                response_json = await self.__post(session, self.__available_request)
            except Exception as e:
                logger.log(f'Subscription to tibber live data failed: {e}')
                return False
            available = response_json['data']['viewer']['home']['features']['realTimeConsumptionEnabled']
            if not available:
                logger.log('No tibber live data available .')
                return False

            tibber_connection = tibber.Tibber(self.__token, websession=session, user_agent="HomeAssistant/2023.2")
            await tibber_connection.update_info()

            self.__home = tibber_connection.get_homes()[0]
            try:
                await self.__home.rt_subscribe(self.__power_callback)
            except Exception as e:
                logger.log(f'Subscription to tibber live data failed: {e}')
                return False
        return True

    def stop(self):
        if self.__home is not None:
            try:
                self.__home.rt_unsubscribe()
            except:
                pass

    @property
    def last_data(self):
        return self.__last_timestamp
    
    def __power_callback(self, data):
        self.__last_timestamp = datetime.datetime.now()
        power = data['data']['liveMeasurement']['power']
        for mqtt in self.__mqtts:
            mqtt.send(round(power + 0.5))

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

    