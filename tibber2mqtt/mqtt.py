import logging, struct
import paho.mqtt.client as mqtt
from ssl import CERT_NONE
from config import get_config_key, get_optional_config_key

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

        self.__encoder = _ENCODERS[get_optional_config_key(config, str, 'int32', None, 'format')]

        self.__mqtt = mqtt.Client()
        self.__mqtt.on_connect = self.__on_connect

        ip, port = get_config_key(config, lambda x: str(x).split(':'), _HOST_VAR_NAME.format(self.__name), 'host')

        ca_path = get_optional_config_key(config, str, None, None, 'ca')
        public_key_path = get_optional_config_key(config, str, None, None, 'public_key')
        private_key_path = get_optional_config_key(config, str, None, None, 'private_key')
        is_tls_insecure = get_optional_config_key(config, bool, False, None, 'tls_insecure')
        if ca_path or is_tls_insecure or public_key_path or private_key_path:
            self.__mqtt.tls_set(ca_certs=ca_path, certfile=public_key_path, keyfile=private_key_path, cert_reqs=CERT_NONE if is_tls_insecure else None)

        user = get_optional_config_key(config, str, None, _USER_VAR_NAME.format(self.__name), 'user')
        password = get_optional_config_key(config, str, None, _PASS_VAR_NAME.format(self.__name), 'password')
        if user or password:
            self.__mqtt.username_pw_set(user, password)

        self.__topic = get_config_key(config, str, None, 'topic')

        self.__mqtt.connect(ip, int(port), 60)
        self.__mqtt.loop_start()

    def __del__(self):
        self.__mqtt.loop_stop()

    def send(self, value):
        self.__mqtt.publish(self.__topic, self.__encoder(value), qos=0, retain=False)
        logging.debug(f'[{self.__name}] Sent {value} to {self.__topic}')

    def __on_connect(self, client, userdata, flags, rc):
        logging.info(f'[{self.__name}] MQTT connected with code {rc}.')
