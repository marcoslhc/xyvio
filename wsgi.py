# -*- coding: utf-8 -*-
import sys
import uwsgi


sys.path = [uwsgi.opt['application'],
            uwsgi.opt['project'],
            uwsgi.opt['bin'],
            ] + sys.path

from xyvio import create_app


app_config = {
    'redis_host': uwsgi.opt['redis_host'],
    'redis_port': uwsgi.opt['redis_port']
}

app = create_app(**app_config)
