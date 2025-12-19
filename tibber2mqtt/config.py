import os
from typing import Dict, Any, Callable, TypeVar

T = TypeVar('T')

def get_optional_config_key(config: Dict, cast: Callable[[Any], T], default: T, varname: str | None = None, *keys: str) -> T:
    if varname and (env_value := os.environ.get(varname)):
        return __cast_value(env_value, cast, (varname,))
    
    raw = config
    for key in keys:
        try:
            raw = raw.get(key)
        except:
            raise KeyError(f'Key tree {".".join(keys)} ended prematurely.')
        if raw is None:
            return default
        
    return __cast_value(raw, cast, keys)

def get_config_key(config: Dict, cast: Callable[[Any], T], varname: str | None = None, *keys: str):
    raw_value = get_optional_config_key(config, cast, None, varname, *keys)
    if raw_value is None:
        raise KeyError(f'Missing config entry or environment variable for {".".join(keys)}.')
    else:
        return raw_value

def __cast_value(value: Any, cast: Callable[[Any], T], keys: tuple[str, ...]) -> T:
    if not isinstance(value, (bool, str, int, float)):
        raise ValueError(f'Found unexpected data type at {".".join(keys)}.')
    try:
        return cast(value)
    except:
        raise ValueError(f'Found unexpected data type at {".".join(keys)}.')
