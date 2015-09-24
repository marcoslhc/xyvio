from xyvio.datastore import DataStore


class TestDataStore(DataStore):
    store = []

    def __init__(self, *args, **kwargs):
        pass

    def __get(self, key):
        value = [v for k, v in self.store if k == key]
        return value[0], self.store.index((key, value[0]))

    def get(self, key):
        try:
            value = self.__get(key)
        except (IndexError, ValueError) as e:
            value = [None]
        return value[0]

    def set(self, key, value):
        self.store.append((key, value))
        return 1

    def incr(self, key):
        try:
            val, idx = self.__get(key)
            self.store[idx] = key, val + 1
        except (IndexError, ValueError) as e:
            self.set(key, 1)
        return self.get(key)
