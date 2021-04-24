# -*- coding: UTF-8 -*-
"""CSV marshaler/parser for Boor model.
This implementation intentionally does not wortk with full CSV strings,
only with values (lists). That is because the complexity of quoting and
unquoting CSVs should be solved at one layer above - perhaps using standard
"csv" python module """

CSV_HEADER = ("SHA1", "MD5", "Name", "Authors", "Year", "ISBN", "Path", 
             "Size", "ModTime", "MetaText")

import datetime
import book_model
import binascii

def to_row(book):
    "Return a list of column values representing a book"
    file = book.file if book.file else book_model.File()
    iso8601 = _iso_8601(file.mod_time)
    authors = book.authors if book.authors else []
    authors = ";".join(book.authors)
    sha1 = file.sha1 if file.sha1 else b''
    md5  = file.md5 if file.md5 else b''
    name = book.name if book.name else ""
    isbn = book.isbn if book.isbn else ""
    path = file.path if file.path else ""
    year = str(book.year) if book.year else ""
    size = str(file.size) if file.size else ""
    meta = book.metatext if book.metatext else ""
    return (sha1.hex(), md5.hex(), name, authors, year, isbn, path, size, 
        iso8601, meta)

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

    def parse_header(self, header_row):
        "Parse CSV header and determine column order"
        self._cols=[]
        for val in header_row:
            v = val.strip().lower()
            func = None
            if v == "sha1": func = _parse_sha1
            elif v == "md5": func = _parse_md5
            elif v == "name": func = _parse_name
            elif v == "authors": func = _parse_authors
            elif v == "year": func = _parse_year
            elif v == "isbn": func = _parse_isbn
            elif v == "path": func = _parse_path
            elif v == "size": func = _parse_size
            elif v == "modtime": func = _parse_modtime
            elif v == "metatext": func = _parse_metatext
            self._cols.append(func)

    def parse_row(self, values):
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

def _parse_sha1(book, v): book.file.sha1 = binascii.a2b_hex(v)
def _parse_md5(book, v): book.file.md5 = binascii.a2b_hex(v)
def _parse_name(book, v): book.name = v
def _parse_year(book, v): book.year = _safe_int(v)
def _parse_isbn(book, v): book.isbn = v
def _parse_path(book, v): book.file.path = v
def _parse_size(book, v): book.file.size = _safe_int(v)
def _parse_metatext(book, v): book.metatext = v

def _safe_int(v):
    return int(v) if v else None





