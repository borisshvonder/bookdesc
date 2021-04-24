# -*- coding: UTF-8 -*-
"""Book data model"""

class Book:
    def __init__(self):
        self.file = None
        self.name = None
        self.authors = []
        self.year = None
        self.isbn = None
        self.metatext = None

class File:
    def __init__(self):
        self.path = None
        self.sha1 = None
        self.md5 = None
        self.size = None
        self.mod_time = 0 # Unix seconds
