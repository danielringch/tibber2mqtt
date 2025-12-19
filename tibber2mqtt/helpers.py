import logging
    
def walk_tree(dict, *keys):
    for key in keys:
        try:
            dict = dict[key]
        except:
            logging.debug(f'Key tree {"->".join(keys)} ended prematurely, key {key} not found')
            return None
    return dict
