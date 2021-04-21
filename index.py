# -*- coding: UTF-8 -*-
"""On-disk index for books.
Implemented as simple on-disk key-value DB that provides very simple functions:
1) Add/update the book in the index
2) List all books in the index
3) Keep track of all changes done to the index as cryptographical signature
"""

import shelve
import hashlib

class Index:
    def __init__(self, filepath, db_impl=shelve.open):
        "Open/create a new index backed by file at filepath"
        self._filepath = filepath
        self._db = db_impl(self._filepath, 'c')
        self._digest = hashlib.new("sha1")
        
    def close(self):
        "Close the index. MUST be called after use, but only once"
        self._db.close()

    def __enter__(self): pass
    def __exit__(self, type, value, traceback): self.close()

    def put(self, book):
        "Put book into the index"
        sha1 = book.file.sha1
        self._db[sha1] = book
        self._digest.update(sha1)

    def list(self):
        "Return a generator which will iterate over all books in the index"
        for book in self._db.values():
            yield book

    def digest(self):
        return self._digest.digest()
