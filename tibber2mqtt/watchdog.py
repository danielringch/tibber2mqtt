import datetime

from logger import *

class Watchdog:
    def __init__(self):
        self.__tolerance = datetime.timedelta(seconds=10)
        self.__lost_at = None
        self.__timeout = 5

    def check(self, last_timestamp):
        now = datetime.datetime.now()
        if last_timestamp + self.__tolerance < now:
            if self.__lost_at is None:
                logger.log('Lost tibber live data.')
                self.__lost_at = now
            if self.__lost_at + datetime.timedelta(seconds=self.__timeout) < now:
                return False
        else:
            self.__reset_timeout()
            self.__lost_at = None
        return True
            
    def subscription_success(self, success):
        self.__lost_at = datetime.datetime.now()
        if success:
            self.__reset_timeout()
        else:
            self.__timeout = min (self.__timeout * 2, 3600)
            logger.log(f'Reconnect attempt in {self.__timeout} seconds.')

    def __reset_timeout(self):
        self.__timeout = 5