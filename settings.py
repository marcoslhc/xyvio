import sys
import ConfigParser

config = ConfigParser.ConfigParser()
config.read('xyvio.ini')

sys.path = [config.get('xyvio', 'application'),
            config.get('xyvio', 'project'),
            config.get('xyvio', 'bin'),
            ] + sys.path
