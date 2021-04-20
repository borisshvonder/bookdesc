#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import book_model
import fb2_parser
import unittest

class ParseFB2Test(unittest.TestCase):
    def test_parse_fb2_sample(self):
        book = None

        with open("fb2-sample.fb2", "rb") as sample:
            book = fb2_parser.parse(sample)

        self.assertEqual("Тестовый платный документ FictionBook 2.1",
            book.name)
        self.assertEqual(2004, book.year)
        self.assertEqual(["Дмитрий Петрович Грибов"], book.authors)
        self.assertTrue(len(book.annotation) > 10)
        self.assertTrue(len(book.metatext) > 100)
        self.assertEqual("eb0e0ec44a4f6f7bd6d837b5786ac4ec5d2b3cb9",
            book.file.sha1.hex())
            

class ParseDescriptionTest(unittest.TestCase):

    def test_parse_sample(self):
        sample="""
        <description>
        <title-info>
            <author>
                <first-name>Дмитрий</first-name>
                <middle-name>Петрович</middle-name>
                <last-name>Грибов</last-name>
            </author>
            <book-title>Тестовый платный документ FictionBook 2.1</book-title>
            <annotation>annotation</annotation>
            <date value="2004-11-08">2004</date>
        </title-info>
        <document-info>
            <author>
                <first-name>Дмитрий</first-name>
                <middle-name>Петрович</middle-name>
                <last-name>Грибов</last-name>
                <home-page>http://www.gribuser.ru</home-page>
                <email>grib@gribuser.ru</email>
            </author>
        </document-info>
        </description>
        """
        book = fb2_parser._parse_description(sample)
        self.assertEqual("Тестовый платный документ FictionBook 2.1",
            book.name)
        self.assertEqual(2004, book.year)
        self.assertEqual(["Дмитрий Петрович Грибов"], book.authors)
        self.assertEqual("annotation", book.annotation)
        self.assertTrue(len(book.metatext) > 10)

    def test_will_prefer_book_name_over_book_title(self):
        sample="""
        <description>
        <title-info>
            <book-title>book-title</book-title>
        </title-info>
        <publish-info>
            <book-name>book-name</book-name>
        </publish-info>
        </description>"""
        book = fb2_parser._parse_description(sample)
        self.assertEqual("book-name", book.name)

    def test_will_use_book_title_if_no_book_name(self):
        sample="""
        <description>
        <title-info>
            <book-title>book-title</book-title>
        </title-info>
        </description>"""
        book = fb2_parser._parse_description(sample)
        self.assertEqual("book-title", book.name)

    def test_prefers_year_over_date(self):
        sample="""
        <description>
        <title-info>
            <date>2020</date>
        </title-info>
        <publish-info>
            <year>2010</year>
        </publish-info>
        </description>"""
        book = fb2_parser._parse_description(sample)
        self.assertEqual(2010, book.year)

    def test_year(self):
        sample="""
        <description>
        <publish-info>
            <year>2010</year>
        </publish-info>
        </description>"""
        book = fb2_parser._parse_description(sample)
        self.assertEqual(2010, book.year)

    def test_will_use_date_if_no_year(self):
        sample="""
        <description>
        <title-info>
            <date>2020</date>
        </title-info>
        </description>"""
        book = fb2_parser._parse_description(sample)
        self.assertEqual(2020, book.year)

    def test_isbn(self):
        sample="""
        <description>
        <publish-info>
            <isbn>123-456</isbn>
        </publish-info>
        </description>"""
        book = fb2_parser._parse_description(sample)
        self.assertEqual("123-456", book.isbn)

    def test_will_prefer_title_authors_over_document_info(self):
        sample="""
        <description>
        <title-info>
            <author>
                <first-name>title-first</first-name>
                <middle-name>title-middle</middle-name>
                <last-name>title-last</last-name>
            </author>
        </title-info>
        <document-info>
            <author>
                <first-name>document-first</first-name>
                <middle-name>document-middle</middle-name>
                <last-name>document-last</last-name>
            </author>
        </document-info>
        </description>"""
        book = fb2_parser._parse_description(sample)
        self.assertEqual(["title-first title-middle title-last"], book.authors)

    def test_will_use_authors_from_document_info(self):
        sample="""
        <description>
        <document-info>
            <author>
                <first-name>document-first</first-name>
                <middle-name>document-middle</middle-name>
                <last-name>document-last</last-name>
            </author>
        </document-info>
        </description>"""
        book = fb2_parser._parse_description(sample)
        self.assertEqual(["document-first document-middle document-last"], 
            book.authors)

    def test_annotation(self):
        sample="""
        <description>
        <title-info>
            <annotation>annotation</annotation>
        </title-info>
        </description>"""
        book = fb2_parser._parse_description(sample)
        self.assertEqual("annotation", book.annotation)

    def test_will_survive_stupid_namespaces(self):
        sample="""
        <description>
            <ns1:tag>tag</ns1:tag>
        </description>"""
        fb2_parser._parse_description(sample)

if __name__ == '__main__':
    unittest.main()

