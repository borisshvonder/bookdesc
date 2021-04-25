#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import io

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
        self.assertEqual("42a7319a2fb45842de56cc7336f63fca",
            book.file.md5.hex())


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

    def test_will_not_pick_up_author_without_names(self):
        sample="""
        <description>
        <document-info>
            <author>
                <first-name>  </first-name>
                <middle-name></middle-name>
                <last-name>
                </last-name>
            </author>
        </document-info>
        </description>"""
        book = fb2_parser._parse_description(sample)
        self.assertEqual([], book.authors)

    def test_will_not_pick_up_known_bad_names(self):
        sample="""
        <description>
        <document-info>
            <author>
                <first-name>author</first-name>
                <middle-name></middle-name>
                <last-name>unknown</last-name>
            </author>
        </document-info>
        </description>"""
        book = fb2_parser._parse_description(sample)
        self.assertEqual([], book.authors)

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

    def test_will_correctly_trim_ns_from_attr(self):
        sample="""<description>
        <title-info>
            <annotation><p><a l:href="http://kats/">http://kats/</a></p></annotation>
        </title-info>
        </description>"""
        book = fb2_parser._parse_description(sample)
        self.assertEqual('http://kats/', book.annotation)


    def test_malformed(self):
        sample="""<description>
  <title-info>
   <genre>poetry</genre>
   <genre>love_erotica</genre>
   <author>
    <first-name>Peter</first-name>
    <last-name>Peneter</last-name>
   </author>
   <book-title>Sekretaj sonetoj</book-title>
<annotation><p>La temo de la «Sekretaj sonetoj»estas eterna kiel la vivo mem: la amo. Klasika, senriproĉa formo el 52 sonetoj, 2 rondeloj kaj balado-epilogo (la virtuozan poezian teknikon de la aŭtoro konas ĉiu leganto!) prezentas tute eksterordinaran enhavon — «la ardan amon trans ĉemizo».</p>
<p>Verdire, se oni traktas Sekretajn Sonetojn sen antaŭjuĝoj — la ciklo estas tute ĉasta kaj altspirita. Ĝi ne liveras pornografiaĵojn, ne reklamas perversojn, sed traktas la veran amon, ĉar «la vera am’ neniam ja perversas» (<a href="#_22">XXII</a>), «tabuo ne ekzistas por la am’» (<a href="#_30">XXX</a>).</p>
<p>Ĝenerale, por legi la libron oni bezonas ne nur libere posedi esperanton kaj esti ne surda al poezio, sed ankaŭ — havi krom ĉio cetera bonan senton de humuro. Preskaŭ ĉie en la versoj de Kalocsay ĉeestas milda ironio, kaj tio donas al atentema leganto apartan plezuron.</p>
<p>La «Komplezaj klarigoj» estas duonŝerca glosaro de kelkaj raraj vortoj kaj neologismoj, inter kiuj enkondukitaj de la aŭtoro (ekzemple pugo). Tradicia parto de multaj esperantaj libroj, la glosaro, ĉi tie estas senriproĉe versita per kvinjamboj (kvankam senrime), kaj havas apartan artan valoron. Laŭ la diro de la aŭtoro,</p>
<poem><stanza>
<v>ĝi vin ne sole distras, sed instruas</v>
<v>vin ankaŭ uzi pli vortriĉan stilon:</v>
<v>kunligos vi plezuron kaj utilon.</v></stanza>
<text-author>(Laŭ recenzo de V. Melnikov en LOdE №10/11)</text-author></poem>

</annotation>
   <date>1932</date>
   <coverpage><image href="#cover.png"/></coverpage>
<//www.esperanto-buecher.de/Peneter-Sekretaj-sonetoj
HEA 1989, ISBN 9635713142 -->
  <lang>eo</lang>
  </title-info>
  <document-info>
   <author>
    <nickname>NN</nickname>
   </author>
   <date value="2018-11-01">2018</date>
   <src-url>https://www.esperanto.mv.ru/Kolekto/Sekretaj_sonetoj.html</src-url>
   <src-url>https://eo.wikisource.org/wiki/Sekretaj_Sonetoj</src-url>
   <id>2018-11-01PP</id>
   <version>1.0</version>
   <history>
    <p>ver. 1.0: Kreo de fb2-libro</p>
   </history>
  </document-info>
</description>"""
        book = fb2_parser._parse_description(sample)
        self.assertEqual("Sekretaj sonetoj", book.title)
        self.assertEqual(["Peter Peneter", "NN"], book.authors)
        self.assertTrue(len(book.annotation) > 10)
        self.assertEqual(1932, book.year)
        self.assertTrue(len(book.metatext) > 100)

    def test_huge_annotations_and_metatext_in_xml(self):
        s = io.StringIO()
        s.write("<description>\n")
        s.write("<title-info>\n")
        s.write("<annotation>\n")
        for i in range(0, fb2_parser._MAX_ANNOTATION_LEN*2):
            s.write('a')
        s.write("</annotation>\n")
        for i in range(0, fb2_parser._MAX_METATEXT_LEN*2):
            s.write('m')
        s.write("</title-info>\n")
        s.write("</description>\n")
        book = fb2_parser._parse_description(s.getvalue())
        self.assertTrue(len(book.annotation) <= fb2_parser._MAX_ANNOTATION_LEN)
        self.assertTrue(len(book.metatext) <= fb2_parser._MAX_METATEXT_LEN)

    def test_huge_annotations_and_metatext_in_malformed(self):
        s = io.StringIO()
        s.write("<description>\n")
        s.write("<title-info>\n")
        s.write("<annotation>\n")
        for i in range(0, fb2_parser._MAX_ANNOTATION_LEN*2):
            s.write('a')
        s.write("</annotation>\n")
        for i in range(0, fb2_parser._MAX_METATEXT_LEN*2):
            s.write('m')
        book = fb2_parser._parse_description(s.getvalue())
        self.assertTrue(len(book.annotation) <= fb2_parser._MAX_ANNOTATION_LEN)
        self.assertTrue(len(book.metatext) <= fb2_parser._MAX_METATEXT_LEN)
if __name__ == '__main__':
    unittest.main()

