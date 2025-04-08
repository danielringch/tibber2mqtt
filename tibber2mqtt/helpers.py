import logging, os

def get_optional_argument(config: dict, *keys: str, varname: str = None, default = None): # type: ignore
    if varname is not None:
        try:
            return os.environ[varname]
        except:
            pass

    sub_config = config
    try:
        for key in keys:
            sub_config = sub_config[key]
        return sub_config
    except:
        return default

def get_argument(config: dict, *keys: str, varname: str = None): # type: ignore
    raw_value = get_optional_argument(config, *keys, varname=varname)
    if raw_value is None:
        logging.critical(f'Missing config entry or environment variable for {".".join(keys)}.')
        exit()
    else:
        return raw_value
