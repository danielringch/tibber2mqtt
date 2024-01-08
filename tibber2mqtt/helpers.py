import os
from functools import reduce

def get_argument(config: dict, keys: list, varname: str, optional=False):
    try:
        return os.environ[varname]
    except:
        try:
            for key in keys:
                dict = dict[key]
            return str(dict)
        except:
            if optional:
                return None
            print(f'Error: Missing config entry or environment variable {varname}.')
            exit()

def get_recursive_key(dict, *keys, optional=False):
    final_key = keys[-1]
    for key in keys[:-1]:
        dict = dict.get(key, {})
    value = dict.get(final_key, None)
    if optional or value:
        return value
    else:
        print(f'Key {".".join(keys)} not found in configuration.')
        exit()