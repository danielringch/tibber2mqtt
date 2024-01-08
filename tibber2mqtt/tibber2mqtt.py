import argparse, asyncio, os, yaml
from mqtt import Mqtt
from helpers import get_argument
from tibberlive import Tibberlive
from watchdog import Watchdog
from logger import Logger, logger

__version__ = "0.1.0"
        

async def main():
    parser = argparse.ArgumentParser(description='Publishes tibber live consumption data from tibber api per MQTT.')
    parser.add_argument('-c', '--config', type=str, required=True, help="Path to config file.")
    args = parser.parse_args()

    print(f'tibberLive2mqtt {__version__}')

    try:
        with open(args.config, "r") as stream:
            config = yaml.safe_load(stream)
    except Exception as e:
        print(f'Failed to load config file {args.config}: {e}')
        exit()

    try:
        log_file = get_argument(config, ('log', 'path'), 'T2M_LOG_PATH', optional=True)
        logger.add_file(log_file)
    except Exception as e:
        print(f'Failed to open log file {log_file}: {e}')
        exit()

    mqtts = []
    for mqttname, mqttconfig in config['mqtt'].items():
        mqtts.append(Mqtt(mqttname, mqttconfig))
    
    tibber = None
    watchdog = Watchdog()

    while True:
        if tibber is None:
            tibber = Tibberlive(config.get('tibber', {}), mqtts)
            watchdog.subscription_success(await tibber.start())
        if not watchdog.check(tibber.last_data):
            tibber.stop()
            tibber = None
        await asyncio.sleep(2)

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()
