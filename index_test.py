#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import book_model
import index
import unittest

class InMemoryDb:
    def __init__(self):
        self.db = {}
        self.closed = False

    def __setitem__(self, key, value):
        assert type(key) == type(b'')
        self.db[key] = value

    def __getitem__(self, key):
        return self.db.get(key)

    def values(self):
        return self.db.values()

    def close(self):
        self.closed = True
        

class IndexTest(unittest.TestCase):
    def setUp(self):
        self.book1 = book_model.Book()
        self.book1.name = "A book"
        self.book1.file = book_model.File()
        self.book1.file.sha1 = b'01'
        self.db = InMemoryDb()
        self.fixture = index.Index("file", db_impl=lambda f,c: self.db)
        self.fixture.__enter__()

    def tearDown(self):
        self.fixture.__exit__(None, None, None)
        self.assertTrue(self.db.closed)

    def test_put_one_book(self):
        book = self.book1
        self.fixture.put(book)
        name = book.name
        got = list(self.fixture.get(name))
        self.assertEqual(1, len(got))
        self.assertEqual(name, got[0].name)

    def test_dedup_by_sha(self):
        book = self.book1
        self.fixture.put(book)
        self.fixture.put(book)
        all = list(self.fixture.list())
        self.assertEqual(1, len(all))
        self.assertEqual(book.name, all[0].name)

    def test_two_books_with_same_name(self):
        book1 = self.book1
        book2 = book_model.Book()
        book2.name = book1.name
        book2.file = book_model.File()
        book2.file.sha1 = b'020202'
        self.fixture.put(book1)
        self.fixture.put(book2)
        books = self.fixture.get(book1.name)
        shas = [book.file.sha1 for book in books]
        self.assertTrue(book1.file.sha1 in shas)
        self.assertTrue(book2.file.sha1 in shas)


if __name__ == '__main__':
    unittest.main()
    
