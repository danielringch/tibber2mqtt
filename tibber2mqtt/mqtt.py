import struct
import paho.mqtt.client as mqtt
from helpers import get_recursive_key
from logger import *

class Mqtt():
    def __init__(self, name: str, config: dict):
        self.__name = name

        self.__mqtt = mqtt.Client()
        self.__mqtt.on_connect = self.__on_connect

        ip, port = get_recursive_key(config, 'host').split(':')

        self.__topic = get_recursive_key(config, 'topic')

        self.__mqtt.connect(ip, int(port), 60)
        self.__mqtt.loop_start()

    def __del__(self):
        self.__mqtt.loop_stop()

    def send(self, value):
        self.__mqtt.publish(self.__topic, struct.pack('!H', int(value)), qos=0, retain=False)
        logger.log(f'[{self.__name}] Sent {value} to {self.__topic}')

    def __on_connect(self, client, userdata, flags, rc):
        logger.log(f'[{self.__name}] MQTT connected with code {rc}.')
