#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import book_model
import csv_parser
import unittest

class ParserTest(unittest.TestCase):
    def setUp(self):
        book1 = book_model.Book()
        book1.title ="A title"
        book1.authors = ["Author1", "Author2"]
        book1.year = 1993
        book1.edition = "2nd"
        book1.isbn = "978-3-16-148410-0"
        book1.file = book_model.File()
        book1.file.sha1 = b'01020304'
        book1.file.path = "/some.fb2"
        book1.file.mod_time = 1618789617
        book1.file.size = 1024
        self.book1 = book1
        self.book1_expected_csv = "A title,Author1;Author2,1993,2nd,"+\
            "978-3-16-148410-0,3031303230333034,/some.fb2,1024,"+\
            "2021-04-18T19:46:57-04:00"
        self.parser = csv_parser.Parser()

    def test_to_csv_line(self):
        self.assertEqual(self.book1_expected_csv,
            self.to_csv_line(self.book1))

    def test_to_csv_line_will_work_on_empty_book(self):
        book2 = book_model.Book()
        self.assertEqual(",,,,,,,,", self.to_csv_line(book2))

    def test_Parser_can_parse_book1(self):
        book = self.parser.parse_values(self.book1_expected_csv.split(','))
        self.assertBooksEqual(self.book1, book)

    def test_Parser_can_parse_empty_book(self):
        book = book_model.Book()
        csv = self.to_csv_line(book)
        self.parser.parse_values(csv.split(","))

    def to_csv_line(self, book):
        return ",".join(csv_parser.to_values(book))

    def assertBooksEqual(self, expected, actual):
        self.assertEqual(expected.title, actual.title)
        self.assertEqual(expected.authors, actual.authors)
        self.assertEqual(expected.year, actual.year)
        self.assertEqual(expected.edition, actual.edition)
        self.assertEqual(expected.isbn, actual.isbn)
        if expected.file:
            self.assertEqual(expected.file.sha1, actual.file.sha1)
            self.assertEqual(expected.file.path, actual.file.path)
            self.assertEqual(expected.file.mod_time, actual.file.mod_time)
            self.assertEqual(expected.file.size, actual.file.size)
        elif actual.file:
            self.fail("Unexpected .file, got " + actual.file)

if __name__ == '__main__':
    unittest.main()

