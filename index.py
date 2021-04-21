# -*- coding: UTF-8 -*-
"""On-disk index for books.
Implemented as simple on-disk key-value DB that provides simple functions like:
1) Look up books by name
2) Add new book
3) List all books in the index
"""

import shelve
import hashlib

class Index:
    def __init__(self, filepath, db_impl=shelve.open):
        "Open/create a new index backed by file at filepath"
        self._filepath = filepath
        self._db_impl = db_impl
        
    def open(self):
        "Open the index. MUST be called prior to use, but only once"
        self._db = self._db_impl(self._filepath, 'c')

    def close(self):
        "Close the index. MUST be called after use, but only once"
        self._db.close()

    def __enter__(self): self.open()
    def __exit__(self, type, value, traceback): self.close()

    def get(self, name):
        "Get list of matching books by name"
        key = self._hash_name(name.encode())
        by_name = self._db[key]
        if by_name:
            by_sha1 = by_name[name]
            if by_sha1: 
                return by_sha1.values()
        return []

    def put(self, book):
        "Put book into the index"
        name = book.name
        sha1 = book.file.sha1
        key = self._hash_name(name.encode())
        by_name = self._db[key]

        if by_name is None: 
            by_name = {}

        by_sha1 = by_name.get(name)
        if by_sha1 is None: 
            by_sha1 = {}
            by_name[name] = by_sha1

        by_sha1[sha1] = book
        
        self._db[key] = by_name

    def list(self):
        "Return a generator which will iterate over all books in the index"
        for by_name in self._db.values():
            for by_sha1 in by_name.values():
                for book in by_sha1.values():
                    yield book

    def _hash_name(self, name):
        "Hash the book name into more compact form"
        # of course, murmurhash will be more effective, but it is another
        # dependency so I have dismissed it
        h = hashlib.new('md5')
        h.update(name)
        return h.digest()


