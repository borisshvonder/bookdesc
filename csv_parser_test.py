#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import book_model
import csv_parser
import unittest

class ParserTest(unittest.TestCase):
    def setUp(self):
        book1 = book_model.Book()
        book1.name ="A name"
        book1.authors = ["Author1", "Author2"]
        book1.year = 1993
        book1.isbn = "978-3-16-148410-0"
        book1.file = book_model.File()
        book1.file.sha1 = b'01020304'
        book1.file.md5 = b'01040506'
        book1.file.path = "/some.fb2"
        book1.file.mod_time = 1618789617
        book1.file.size = 1024
        self.book1 = book1
        self.book1_expected_csv = "3031303230333034,3031303430353036,"+\
            "A name,Author1;Author2,1993,"+\
            "978-3-16-148410-0,/some.fb2,1024,"+\
            "2021-04-18T19:46:57-04:00,tag1 tag2"
        book1.metatext = "tag1 tag2"
        self.parser = csv_parser.Parser()

    def test_to_csv_line(self):
        self.assertEqual(self.book1_expected_csv,
            self.to_csv_line(self.book1))

    def test_to_csv_line_will_work_on_empty_book(self):
        book2 = book_model.Book()
        self.assertEqual(",,,,,,,,,", self.to_csv_line(book2))

    def test_Parser_can_parse_book1(self):
        book = self.parser.parse_row(self.book1_expected_csv.split(','))
        self.assertBooksEqual(self.book1, book)

    def test_Parser_can_parse_empty_book(self):
        book = book_model.Book()
        csv = self.to_csv_line(book)
        self.parser.parse_row(csv.split(","))

    def to_csv_line(self, book):
        return ",".join(csv_parser.to_row(book))

    def assertBooksEqual(self, expected, actual):
        self.assertEqual(expected.name, actual.name)
        self.assertEqual(expected.authors, actual.authors)
        self.assertEqual(expected.year, actual.year)
        self.assertEqual(expected.isbn, actual.isbn)
        if expected.file:
            self.assertEqual(expected.file.sha1, actual.file.sha1)
            self.assertEqual(expected.file.path, actual.file.path)
            self.assertEqual(expected.file.mod_time, actual.file.mod_time)
            self.assertEqual(expected.file.size, actual.file.size)
        elif actual.file:
            self.fail("Unexpected .file, got " + actual.file)
        self.assertEqual(expected.metatext, actual.metatext)

if __name__ == '__main__':
    unittest.main()

