import redis


class DataStore(object):
    def __init__(self, *args, **kwargs):
        pass


class RedisDataStore(DataStore):

    def __init__(self, *args, **kwargs):
        self.store = redis.Redis(kwargs['redis_host'], kwargs['redis_port'])
        super(RedisDataStore, self).__init__(*args, **kwargs)

    def get(self, key):
        return self.store.get(key)

    def incr(self, key):
        return self.store.incr(key)

    def set(self, key, value):
        return self.store.set(key, value)

    def delete(self, key):
        return self.store.delete(key)

    def keys(self, pattern):
        return self.store.keys(pattern)


class DataManager(object):

    def __init__(self, dataStore=None):
        if dataStore is None:
            raise Exception('No data store defined')
        self.dataStore = dataStore
