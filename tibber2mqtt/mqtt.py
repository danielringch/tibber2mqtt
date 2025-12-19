import logging, struct
import paho.mqtt.client as mqtt
from ssl import CERT_NONE
from helpers import *

_HOST_VAR_NAME = 'T2M_MQTT_HOST_{}'
_USER_VAR_NAME = 'T2M_MQTT_USER_{}'
_PASS_VAR_NAME = 'T2M_MQTT_PASS_{}'

_ENCODERS = {
    'int32': lambda x: struct.pack('!i', int(x)),
    'int16': lambda x: struct.pack('!h', int(x)),
    'utf8': lambda x: str(int(x))
}

class Mqtt():
    def __init__(self, name: str, config: dict):
        self.__name = name

        self.__encoder = _ENCODERS[str(get_optional_argument(config, 'format', default='int32'))]

        self.__mqtt = mqtt.Client()
        self.__mqtt.on_connect = self.__on_connect

        ip, port = str(get_argument(config, 'host', varname=_HOST_VAR_NAME.format(self.__name))).split(':')

        ca = get_optional_argument(config, 'ca')
        public_key = get_optional_argument(config, 'public_key')
        private_key = get_optional_argument(config, 'private_key')
        tls_insecure = get_optional_argument(config, 'tls_insecure')
        if ca or tls_insecure or public_key or private_key:
            self.__mqtt.tls_set(ca_certs=ca, certfile=public_key, keyfile=private_key, cert_reqs=CERT_NONE if tls_insecure else None)

        user = get_optional_argument(config, 'user', varname=_USER_VAR_NAME.format(self.__name))
        password = get_optional_argument(config, 'password', varname=_PASS_VAR_NAME.format(self.__name))
        if user or password:
            self.__mqtt.username_pw_set(user, password)

        self.__topic = get_argument(config, 'topic')

        self.__mqtt.connect(ip, int(port), 60)
        self.__mqtt.loop_start()

    def __del__(self):
        self.__mqtt.loop_stop()

    def send(self, value):
        self.__mqtt.publish(self.__topic, self.__encoder(value), qos=0, retain=False)
        logging.debug(f'[{self.__name}] Sent {value} to {self.__topic}')

    def __on_connect(self, client, userdata, flags, rc):
        logging.info(f'[{self.__name}] MQTT connected with code {rc}.')
