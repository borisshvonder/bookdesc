# -*- coding: UTF-8 -*-
"""Provides access to best k-v store available"""

_BACKENDS = {}
try:
    import lmdb  

    class LMDB:
        def __init__(self, path):
            self._env = lmdb.Environment(path, subdir=False, readonly=False,
                metasync=False, sync=False, create=True, readahead=False,
                writemap=True, meminit=True, map_async=True)

        def __setitem__(self, key, value):
            with self._env.begin() as txn:
                txn.put(key, value)
                txn.commit()

        def __getitem__(self, key):
            with self._env.begin() as txn:
                result = txn.get(key)
                txn.commit()
                return result

        def items(self):
            with self._env.begin() as txn:
                cursor = txn.cursor()
                if cursor.first():
                    yield cursor.key(), cursor.value()
                while cursor.next():
                    yield cursor.key(), cursor.value()

        def close(self):
            self._env.close()

        def __enter__(self): return self
        def __exit__(self, type, value, traceback): self.close()

    backends["lmdb"] = LMDB

except ImportError:
    lmdb = None

import dbm.dumb # ndbm has serious problems with large number od keys

class InMemoryDb:
    def __init__(self, path):
        self.path = path
        self.db = {}
        self.closed = False

    def __setitem__(self, key, value):
        assert type(key) == type(b'')
        self.db[key] = value

    def __getitem__(self, key):
        return self.db.get(key)

    def items(self):
        return self.db.items()

    def close(self):
        self._db = {}
        self.closed = True
 
    def __enter__(self): return self
    def __exit__(self, type, value, traceback): self.close()

class DumbDb:
    def __init__(self, path):
        self._db = dbm.dumb.open(path, 'c')

    def __setitem__(self, key, value):
        self._db[key] = value

    def __getitem__(self, key):
        return self._db[key]

    def items(self):
        for key in self._db.keys():
            yield key, self._db[key]

    def close(self):
        self._db.close()
 
    def __enter__(self): return self
    def __exit__(self, type, value, traceback): self.close()

_BACKENDS["memory"]=InMemoryDb
_BACKENDS["dumb"]=DumbDb

def open(path, backend=None):
    if backend:
        bak = _BACKENDS.get(backend)
        if not bak: raise ValueError("Backend " + backend + " is unavaliable")
        return bak(path)
    else:
        if lmdb: 
            return LMDB(path)
        else:
            return DumbDb(path)

def backends(): return list(_BACKENDS.keys())
