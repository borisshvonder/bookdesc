# -*- coding: UTF-8 -*-
"""On-disk index for books.
Implemented as simple on-disk key-value DB that provides simple functions like:
1) Look up books by title
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

    def get(self, title):
        "Get list of matching books by title"
        key = self._hash_title(title.encode())
        by_title = self._db[key]
        if by_title:
            by_sha1 = by_title[title]
            if by_sha1: 
                return by_sha1.values()
        return []

    def put(self, book):
        "Put book into the index"
        title = book.title
        sha1 = book.file.sha1
        key = self._hash_title(title.encode())
        by_title = self._db[key]

        if by_title is None: 
            by_title = {}

        by_sha1 = by_title.get(title)
        if by_sha1 is None: 
            by_sha1 = {}
            by_title[title] = by_sha1

        by_sha1[sha1] = book
        
        self._db[key] = by_title

    def list(self):
        "Return a generator which will iterate over all books in the index"
        for by_title in self._db.values():
            for by_sha1 in by_title.values():
                for book in by_sha1.values():
                    yield book

    def __enter__(self):
        self._db = self._db_impl(self._filepath, 'c')

    def __exit__(self, type, value, traceback):
        self._db.close()

    def _hash_title(self, title):
        "Hash the book title into more compact form"
        # of course, murmurhash will be more effective, but it is another
        # dependency so I have dismissed it
        h = hashlib.new('md5')
        h.update(title)
        return h.digest()


