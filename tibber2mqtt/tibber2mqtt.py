import argparse, asyncio, logging, sys, yaml
from logging.handlers import TimedRotatingFileHandler
from mqtt import Mqtt
from helpers import *
from tibberlive import Tibberlive
from watchdog import Watchdog

__version__ = "1.2.0"
        

async def main():
    parser = argparse.ArgumentParser(description='Publishes tibber live consumption data from tibber api per MQTT.')
    parser.add_argument('-c', '--config', type=str, required=True, help="Path to config file.")
    args = parser.parse_args()

    try:
        with open(args.config, "r") as stream:
            config = yaml.safe_load(stream)
    except Exception as e:
        logging.critical(f'Failed to load config file {args.config}: {e}')
        exit()

    log_level = get_optional_argument(config, 'log', 'level', varname='T2M_LOG_LEVEL', default='INFO')
    logger = logging.getLogger()
    logger.setLevel(logging.getLevelName(log_level))
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%dT%H:%M:%S')

    class ModuleFilter(logging.Filter):
        def filter(self, record):
            return record.name == 'root'

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    stdout_handler.addFilter(ModuleFilter())
    logger.addHandler(stdout_handler)

    log_file = get_optional_argument(config, 'log', 'path', varname='T2M_LOG_PATH')
    backup_count = get_optional_argument(config, 'log', 'count', varname='T2M_LOG_COUNT', default=0)
    if log_file is not None:
        file_handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1, backupCount=backup_count)
        file_handler.setFormatter(formatter)
        file_handler.addFilter(ModuleFilter())
        logger.addHandler(file_handler)

    logging.info(f'tibberLive2mqtt {__version__}')

    mqtts = []
    for mqttname, mqttconfig in config['mqtt'].items():
        mqtts.append(Mqtt(mqttname, mqttconfig))
    
    tibber = None
    watchdog = Watchdog(config)

    while True:
        if tibber is None:
            tibber = Tibberlive(config.get('tibber', {}), mqtts)
            watchdog.subscription_success(await tibber.start())
        if not watchdog.check(tibber.last_data):
            await tibber.stop()
            tibber = None
        await asyncio.sleep(2)

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()
