__version__ = '0.0.1'

import os
from conf.config_loader import config_data

os.environ['TAVILY_API_KEY'] = config_data['tavily']['key']
