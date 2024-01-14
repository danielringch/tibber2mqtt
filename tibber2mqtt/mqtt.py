import struct
import paho.mqtt.client as mqtt
from ssl import CERT_NONE
from helpers import get_recursive_key
from logger import *

class Mqtt():
    def __init__(self, name: str, config: dict):
        self.__name = name

        self.__mqtt = mqtt.Client()
        self.__mqtt.on_connect = self.__on_connect

        ip, port = get_recursive_key(config, 'host').split(':')

        ca = get_recursive_key(config, 'ca', optional=True)
        public_key = get_recursive_key(config, 'public_key', optional=True)
        private_key = get_recursive_key(config, 'private_key', optional=True)
        if ca or public_key or private_key:
            insecure = get_recursive_key(config, 'tls_insecure', optional=True) == True
            self.__mqtt.tls_set(ca_certs=ca, certfile=public_key, keyfile=private_key, cert_reqs=CERT_NONE if insecure else None)

        user = get_recursive_key(config, 'user', optional=True)
        password = get_recursive_key(config, 'password', optional=True)
        if user or password:
            self.__mqtt.username_pw_set(user, password)

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
