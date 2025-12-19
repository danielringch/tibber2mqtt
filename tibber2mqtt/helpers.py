import logging, os

def get_optional_argument(config: dict, *keys: str, varname: str | None = None, default: bool | str | int | float | None = None):
    if varname is not None:
        try:
            return os.environ[varname]
        except:
            pass

    sub_config = config
    try:
        for key in keys:
            sub_config = sub_config[key]
        if not isinstance(sub_config, (bool, str, int, float)):
            logging.critical(f'Found unexpected data type at {".".join(keys)}.')
            exit()
        return sub_config
    except:
        return default

def get_argument(config: dict, *keys: str, varname: str | None = None): # type: ignore
    raw_value = get_optional_argument(config, *keys, varname=varname)
    if raw_value is None:
        logging.critical(f'Missing config entry or environment variable for {".".join(keys)}.')
        exit()
    else:
        return raw_value
    
def walk_tree(dict, *keys):
    for key in keys:
        try:
            dict = dict[key]
        except:
            logging.debug(f'Key tree {"->".join(keys)} ended prematurely, key {key} not found')
            return None
    return dict
