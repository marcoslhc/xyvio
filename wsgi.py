# -*- coding: utf-8 -*-
from settings import config
from xyvio import create_app



app_config = {
    'redis_host': config.get('redis', 'host'),
    'redis_port': config.get('redis', 'port')
}

app = create_app(**app_config)
