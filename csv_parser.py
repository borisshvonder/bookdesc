# -*- coding: UTF-8 -*-
"""CSV marshaler/parser for Boor model.
This implementation intentionally does not wortk with full CSV strings,
only with values (lists). That is because the complexity of quoting and
unquoting CSVs should be solved at one layer above - perhaps using standard
"csv" python module """

CSV_HEADER = ("Title", "Authors", "Year", "Edition", "ISBN", "Sha1", "Path", 
             "Size", "ModTime")

import datetime
import book_model
import binascii

def to_values(book):
    "Return a list of column values representing a book"
    file = book.file if book.file else book_model.File()
    iso8601 = _iso_8601(file.mod_time)
    authors = book.authors if book.authors else []
    authors = ";".join(book.authors)
    sha1 = file.sha1 if file.sha1 else b''
    title = book.title if book.title else ""
    edition = book.edition if book.edition else ""
    isbn = book.isbn if book.isbn else ""
    path = file.path if file.path else ""
    year = str(book.year) if book.year else ""
    size = str(file.size) if file.size else ""
    return (title, authors, year, edition, isbn, sha1.hex(), path, size, 
        iso8601)

def _iso_8601(timestamp):
    if timestamp:
        dt = datetime.datetime.fromtimestamp(timestamp)
        return dt.astimezone().isoformat()
    else:
        return ""

class Parser:
    "Parses the CSV files with, perhaps, wrong column order"
    def __init__(self):
        self.parse_header(CSV_HEADER)

    def parse_header(self, header_values):
        "Parse CSV header and determine column order"
        self._cols=[]
        for val in header_values:
            v = val.strip().lower()
            func = None
            if v == "title": func = _parse_title
            elif v == "authors": func = _parse_authors
            elif v == "year": func = _parse_year
            elif v == "edition": func = _parse_edition
            elif v == "isbn": func = _parse_isbn
            elif v == "sha1": func = _parse_sha1
            elif v == "path": func = _parse_path
            elif v == "size": func = _parse_size
            elif v == "modtime": func = _parse_modtime
            self._cols.append(func)

    def parse_values(self, values):
        "Parses the CSV values and returns a Book"
        book = book_model.Book()
        book.file = book_model.File()
        i = 0
        for func in self._cols:
            if i<= len(values):
                value = values[i].strip()
                func(book, value)
            i+=1
        return book

def _parse_authors(book, v): 
    book.authors = [a.strip() for a in v.split(";")]

def _parse_modtime(book, v): 
    if v:
        dt = datetime.datetime.fromisoformat(v)
        book.file.mod_time = int(dt.timestamp())

def _parse_title(book, v): book.title = v
def _parse_year(book, v): book.year = _safe_int(v)
def _parse_edition(book, v): book.edition = v
def _parse_isbn(book, v): book.isbn = v
def _parse_sha1(book, v): book.file.sha1 = binascii.a2b_hex(v)
def _parse_path(book, v): book.file.path = v
def _parse_size(book, v): book.file.size = _safe_int(v)

def _safe_int(v):
    return int(v) if v else None





