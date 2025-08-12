import logging, struct
import paho.mqtt.client as mqtt
from ssl import CERT_NONE
from helpers import *

class Mqtt():
    def __init__(self, name: str, config: dict):
        self.__name = name

        self.__mqtt = mqtt.Client()
        self.__mqtt.on_connect = self.__on_connect

        ip, port = get_argument(config, 'host').split(':')

        ca = get_optional_argument(config, 'ca')
        public_key = get_optional_argument(config, 'public_key')
        private_key = get_optional_argument(config, 'private_key')
        if ca or public_key or private_key:
            insecure = get_optional_argument(config, 'tls_insecure') == True
            self.__mqtt.tls_set(ca_certs=ca, certfile=public_key, keyfile=private_key, cert_reqs=CERT_NONE if insecure else None)

        user = get_optional_argument(config, 'user')
        password = get_optional_argument(config, 'password')
        if user or password:
            self.__mqtt.username_pw_set(user, password)

        self.__topic = get_argument(config, 'topic')

        self.__mqtt.connect(ip, int(port), 60)
        self.__mqtt.loop_start()

    def __del__(self):
        self.__mqtt.loop_stop()

    def send(self, value):
        self.__mqtt.publish(self.__topic, struct.pack('!h', int(value)), qos=0, retain=False)
        logging.debug(f'[{self.__name}] Sent {value} to {self.__topic}')

    def __on_connect(self, client, userdata, flags, rc):
        logging.info(f'[{self.__name}] MQTT connected with code {rc}.')
