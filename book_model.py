# -*- coding: UTF-8 -*-
"""Book data model"""

class Book:
    def __init__(self):
        self.file = None
        self.title = None
        self.authors = []
        self.year = None
        self.edition = None
        self.isbn = None

class File:
    def __init__(self):
        self.path = None
        self.sha1 = None
        self.size = None
        self.mod_time = 0.0 # Unix seconds
