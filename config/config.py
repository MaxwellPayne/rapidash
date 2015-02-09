import json
import os


with open(os.path.join('config', 'dev.json'), 'r') as config_file:
    _config_dict = json.load(config_file)
    # reformat to ascii
    _config_dict = {str(key): str(_config_dict[key]) for key in _config_dict.keys()}

secret_path = os.path.join('config', '.secret.json')
if os.path.exists(secret_path):
    with open(secret_path, 'r') as secret_config_file:
        # my facebook app info kept secret for development purposes
        _config_dict.update(json.load(secret_config_file))

# coerce json strings to ascii
config_dict = {str(k): (str(v) if isinstance(v, unicode) else v) for k, v in _config_dict.iteritems()}

config = config_dict

__all__ = ['config']
