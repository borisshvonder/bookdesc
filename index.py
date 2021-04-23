# -*- coding: UTF-8 -*-
"""On-disk index for books.
Implemented as simple on-disk key-value DB that provides very simple functions:
1) save/update the book in the index
2) List all books in the index
3) put/get additional metadata objects (they MUST be pickleable)
"""

import hashlib
import pickle
import keyvalue

_META_PREFIX=b'meta_'

class Index:
    def __init__(self, filepath, db_impl=keyvalue.open):
        "Open/create a new index backed by file at filepath"
        self._filepath = filepath
        self._db = db_impl(self._filepath)

    def close(self):
        "Close the index. MUST be called after use, but only once"
        self._db.close()

    def __enter__(self): return self
    def __exit__(self, type, value, traceback): self.close()

    def save(self, book):
        "Put book into the index"
        sha1 = book.file.sha1
        pickled = pickle.dumps(book)
        self._db[sha1] = pickled

    def list(self):
        "Return a generator which will iterate over all books in the index"
        for key, maybe_book in self._db.items():
            if not key.startswith(_META_PREFIX):
                pickled_book = maybe_book
                book = pickle.loads(pickled_book)
                yield book

    def set(self, key, pickleable_value):
        "Set pickleable metadata value. Key should be a string"
        fullkey = self._fullkey(key)
        pickled = pickle.dumps(pickleable_value)
        self._db[fullkey] = pickled

    def get(self, key):
        "Get pickled metadata value. Key must be a string"
        fullkey = self._fullkey(key)
        pickled = self._db[fullkey]
        return pickle.loads(pickled) if pickled else None

    def _fullkey(self, key): 
        if type(key) != type(""): raise ValueError("key " + key(key) + \
            " is not a string (type(key)==" + str(type(key)) + ")")

        # ensure we never overlap those keys with sha1 book keys
        b = bytearray(_META_PREFIX)
        b.extend(key.encode('utf-8'))
        return bytes(b)
