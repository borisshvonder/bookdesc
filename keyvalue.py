# -*- coding: UTF-8 -*-
"""Provides access to best k-v store available"""

import log
import dbm.dumb # ndbm has serious problems with large number od keys
import bplustreebranded
from bplustreebranded import serializer

_BACKENDS = {}

class BytesSerializer(serializer.Serializer):
    def serialize(self, obj : bytes , key_size: int) -> bytes:
        assert len(obj) <= key_size
        return obj

    def deserialize(self, data: bytes) -> bytes:
        return data

def _bplustree(path):
    return bplustreebranded.BPlusTree(path, 
        serializer=BytesSerializer(),
        key_size=20,
        page_size=4096*4)

_BACKENDS["b+tree"] = _bplustree

class InMemoryDb:
    def __init__(self, path):
        self.path = path
        self.db = {}
        self.closed = False

    def __setitem__(self, key, value):
        assert type(key) == type(b'')
        self.db[key] = value

    def __getitem__(self, key):
        return self.db[key]

    def get(self, key):
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

    def get(self, key):
        if key in self._db:
            return self._db[key]
        else:
            return None

    def items(self):
        for key in self._db.keys():
            yield key, self._db[key]

    def close(self):
        self._db.close()
 
    def __enter__(self): return self
    def __exit__(self, type, value, traceback): self.close()

_BACKENDS["memory"]=InMemoryDb
_BACKENDS["dumb"]=DumbDb

DEFAULT_BACKEND="dumb"

def open(path, backend=DEFAULT_BACKEND):
    bak = _BACKENDS.get(backend)
    if not bak: raise ValueError("Backend " + backend + " is unavaliable")
    return bak(path)

def backends(): return list(_BACKENDS.keys())
