import datetime

class Logger:
    def __init__(self):
        self.__handle = None

    def __del__(self):
        if self.__handle:
            self.__handle.close()

    def add_file(self, path):
        if not path:
            return
        self.__handle = open(path, 'a')

    def log(self, message):
        message = f'[{datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}] {message}\n'
        print(message, end='')
        if self.__handle:
            self.__handle.write(message)
            self.__handle.flush()

logger = Logger()
