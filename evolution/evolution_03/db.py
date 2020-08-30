# -*- coding: utf-8 -*-

import anydbm as dbm
try:
    import cPickle as pickle
except ImportError: # pragma: no cover
    import pickle as pickle
import threading
import warnings


# Open database, creating it if necessary.
db = dbm.open('cache', 'c')

# Record some values
db['www.python.org'] = 'Python Website'
db['www.cnn.com'] = 'Cable News Network'

# Loop through contents.  Other dictionary methods
# such as .keys(), .values() also work.
for k, v in db.iteritems():
    # print(k, '\t', v)
    pass

"""
('www.cnn.com', '\t', 'Cable News Network')
('www.python.org', '\t', 'Python Website')
"""

# Storing a non-string key or value will raise an exception (most
# likely a TypeError).
# db['www.yahoo.com'] = 4

# Close when done.
db.close()


DB_PATH = './'

class BottleBucket(object):
    def __init__(self, name):
        self.__dict__['name'] = name
        self.__dict__['db'] = dbm.open(DB_PATH + '/%s.db' % name, 'c')
        self.__dict__['mmap'] = {}
        # {'mmap': {}, 'db': {}, 'name': 'bb'}

    def __getitem__(self, key):
        print('BottleBucket getitem key: %s' % key)
        if key not in self.mmap:
            self.mmap[key] = pickle.loads(self.db[key])
        return self.mmap[key]

    def __setitem__(self, key, value):
        print('BottleBucket setitem key: %s, value: %s' % (key, value))
        if not isinstance(key, str):
            raise TypeError("Bottle keys must be strings")
        self.mmap[key] = value

    def __delitem__(self, key):
        print('BottleBucket delitem key: %s' % key)
        if key in self.mmap:
            del self.mmap[key]
        del self.db[key]

    def __getattr__(self, key):
        print('BottleBucket getattr key: %s' % key)
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        print('BottleBucket setattr key: %s, value: %s' % (key, value))
        self[key] = value

    def __delattr__(self, key):
        print('BottleBucket delattr key: %s' % key)
        try:
            del self[key]
        except KeyError:
            raise AttributeError(key)

    def __iter__(self):
        return iter(self.ukeys())

    def __contains__(self, key):
        return key in self.ukeys()

    def __len__(self):
        return len(self.ukeys())

    def keys(self):
        return list(self.ukeys())

    def ukeys(self):
      return set(self.db.keys()) | set(self.mmap.keys())

    def save(self):
        self.close()
        self.__init__(self.name)

    def close(self):
        for key in self.mmap:
            pvalue = pickle.dumps(self.mmap[key], pickle.HIGHEST_PROTOCOL)
            if key not in self.db or pvalue != self.db[key]:
                self.db[key] = pvalue
        self.mmap.clear()
        if hasattr(self.db, 'sync'):
            self.db.sync()
        if hasattr(self.db, 'close'):
            self.db.close()

    def clear(self):
        for key in self.db:
            del self.db[key]
        self.mmap.clear()

    def update(self, other):
        self.mmap.update(other)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            if default:
                return default
            raise


class BottleDB(threading.local):
    def __init__(self):
        self.__dict__['open'] = {}

    def __getitem__(self, key):
        print('BottleDB getitem key: %s' % key)
        if key not in self.open and not key.startswith('_'):
            self.open[key] = BottleBucket(key)
        return self.open[key]

    def __setitem__(self, key, value):
        print('BottleDB setitem key: %s, value: %s' % (key, value))
        if isinstance(value, BottleBucket):
            self.open[key] = value
        elif hasattr(value, 'items'):
            if key not in self.open:
                self.open[key] = BottleBucket(key)
            self.open[key].clear()
            for k, v in value.iteritems():
                self.open[key][k] = v
        else:
            raise ValueError("Only dicts and BottleBuckets are allowed.")

    def __delitem__(self, key):
        print('BottleDB delitem key: %s' % key)
        if key not in self.open:
            self.open[key].clear()
            self.open[key].save()
            del self.open[key]

    def __getattr__(self, key):
        print('BottleDB getattr key: %s' % key)
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        print('BottleDB setattr key: %s, value: %s' % (key, value))
        self[key] = value

    def __delattr__(self, key):
        print('BottleDB delattr key: %s' % key)
        try:
            del self[key]
        except KeyError:
            raise AttributeError(key)

    def save(self):
        self.close()
        self.__init__()

    def close(self):
        for db in self.open:
            self.open[db].close()
        self.open.clear()


db = BottleDB()
# print(db)  # <__main__.BottleDB object at 0x7f258ae60bb0>
# print(db.open)  # {}
# print(db.__dict__)  # {'open': {}}
data = [1, 1.5, 'a', 'ä']
# db.db1.value1 = data
db1 = db.db1
print(db1)
print(db.__dict__)
"""
BottleDB getattr key: db1
BottleDB getitem key: db1
<__main__.BottleBucket object at 0x7f46dbeff150>
{'open': {'db1': <__main__.BottleBucket object at 0x7f46dbeff150>}}
"""

db1.value1 = data
"""
BottleBucket setattr key: value1, value: [1, 1.5, 'a', '\xc3\xa4']
BottleBucket setitem key: value1, value: [1, 1.5, 'a', '\xc3\xa4']
"""

db['db2']['value2'] = data
print(db.__dict__)
"""
BottleDB getitem key: db2
BottleBucket setitem key: value2, value: [1, 1.5, 'a', '\xc3\xa4']
{'open': {'db1': <__main__.BottleBucket object at 0x7f1abb5f3fd0>, 'db2': <__main__.BottleBucket object at 0x7f1abb590350>}}
"""

print(db['db1']['value1'])
"""
BottleDB getitem key: db1
BottleBucket getitem key: value1
[1, 1.5, 'a', '\xc3\xa4']
"""

print(db.db2.value2)
"""
BottleDB getattr key: db2
BottleDB getitem key: db2
BottleBucket getattr key: value2
BottleBucket getitem key: value2
[1, 1.5, 'a', '\xc3\xa4']
"""

for bb in db.open:
    print(db.open[bb])
    print(db.open[bb].mmap)
"""
<__main__.BottleBucket object at 0x7f26673c3fd0>
{'value1': [1, 1.5, 'a', '\xc3\xa4']}
<__main__.BottleBucket object at 0x7f266735e350>
{'value2': [1, 1.5, 'a', '\xc3\xa4']}
"""

db.close()
