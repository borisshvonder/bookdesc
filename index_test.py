#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import book_model
import keyvalue
import index
import unittest

       

class IndexTest(unittest.TestCase):
    def setUp(self):
        self.book1 = book_model.Book()
        self.book1.name = "A book"
        self.book1.file = book_model.File()
        self.book1.file.sha1 = b'01'
        self.db = keyvalue.open('', backend="memory")
        self.open_fixture()

    def open_fixture(self):
        self.fixture = index.Index("file", db_impl=lambda f: self.db)

    def tearDown(self):
        self.fixture.__exit__(None, None, None)
        self.assertTrue(self.db.closed)

    def test_put_one_book(self):
        book = self.book1
        self.fixture.save(book)
        name = book.name
        got = list(self.fixture.list())
        self.assertEqual(1, len(got))
    def items(self):
        return self.db.items()

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
        self.db = keyvalue.open('', backend="memory")
        self.open_fixture()

    def open_fixture(self):
        self.fixture = index.Index("file", db_impl=lambda f: self.db)

    def tearDown(self):
        self.fixture.__exit__(None, None, None)
        self.assertTrue(self.db.closed)

    def test_put_one_book(self):
        book = self.book1
        self.fixture.save(book)
        name = book.name
        got = list(self.fixture.list())
        self.assertEqual(1, len(got))
        self.assertEqual(name, got[0].name)

    def test_dedup_by_sha(self):
        book = self.book1
        self.fixture.save(book)
        self.fixture.save(book)
        all = list(self.fixture.list())
        self.assertEqual(1, len(all))
        self.assertEqual(book.name, all[0].name)

    def test_set_put_metadata(self):
        self.fixture.set("key", "value")
        self.assertEqual("value", self.fixture.get("key"))
        self.assertEqual(0, len(list(self.fixture.list())))



if __name__ == '__main__':
    unittest.main()
    
