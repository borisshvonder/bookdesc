# -*- coding: UTF-8 -*-
"""On-disk index for books.
Implemented as simple on-disk key-value DB that provides very simple functions:
1) save/update the book in the index
2) List all books in the index
3) put/get additional metadata objects (they MUST be pickleable)
"""

import shelve
import hashlib

_META_PREFIX=b'meta_'

class Index:
    def __init__(self, filepath, db_impl=shelve.open):
        "Open/create a new index backed by file at filepath"
        self._filepath = filepath
        self._db = db_impl(self._filepath, 'c')
        
    def close(self):
        "Close the index. MUST be called after use, but only once"
        self._db.close()

    def __enter__(self): return self
    def __exit__(self, type, value, traceback): self.close()

    def save(self, book):
        "Put book into the index"
        sha1 = book.file.sha1
        self._db[sha1] = book

    def list(self):
        "Return a generator which will iterate over all books in the index"
        for key, maybe_book in self._db.items():
            if not key.startswith(_META_PREFIX):
                definetly_book = maybe_book
                yield definetly_book

    def set(self, key, pickleable_value):
        "Set pickleable metadata value. Key should be a string"
        fullkey = self._fullkey(key)
        self._db[fullkey] = pickleable_value

    def get(self, key):
        "Get pickled metadata value. Key must be a string"
        fullkey = self._fullkey(key)
        return self._db[fullkey]

    def _fullkey(self, key): 
        if type(key) != type(""): raise ValueError("key " + key(key) + \
            " is not a string (type(key)==" + str(type(key)) + ")")

        # ensure we never overlap those keys with sha1 book keys
        b = bytearray(_META_PREFIX)
        b.extend(key.encode('utf-8'))
        return bytes(b)
