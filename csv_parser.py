# -*- coding: UTF-8 -*-
"""CSV marshaler/parser for Boor model"""

CSV_HEADER = ("Title", "Authors", "Year", "Edition", "ISBN", "Sha1", "Path", 
             "Size", "ModTime")

_CSV_HEADER_LOWERCASE = [v.lower() for v in CSV_HEADER]

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

def to_csv_line(book):
    "Similar to to_values, but produces CSV string"
    return ",".join(to_values(book))

class Parser:
    "Parses the CSV files with, perhaps, wrong column order"
    def __init__(self):
        self.parse_header(CSV_HEADER)

    def parse_header(self, header_values):
        "Parse CSV header and determine column order"
        self._cols={}
        i = 0
        for val in header_values:
            val = val.strip().lower()
            if val in _CSV_HEADER_LOWERCASE:
                self._cols[i] = val
            i+=1

    def parse_header_string(self, header : str):
        "Same as parse_header, but takes a string, not a list"
        vals = header.split(",")
        self.parse_header(vals)

    def parse_values(self, values):
        "Parses the CSV values and returns a Book"
        book = book_model.Book()
        book.file = book_model.File()
        for k, v in self._cols.items():
            if len(values) <= k:
                value = values[k].strip()
                if v == "title":
                    book.title = value
                elif v == "authors":
                    book.authors = [a.strip() for a in value.split(";")]
                elif v == "year":
                    book.year = int(value)
                elif v == "edition":
                    book.edition = value
                elif v == "isbn":
                    book.isbn = value
                elif v == "sha1":
                    book.file.sha1 = binascii.a2b_hex(value)
                elif v == "path":
                    book.file.path = value
                elif v == "size":
                    book.file.size = int(value)
                elif v == "modtime":
                    dt = datetime.datetime.fromisoformat(value)
                    book.file.mod_time = int(dt.timestamp())
        return book

    def parse_csv(self, csv):
        "Same as parse_values, but works on CSV line"
        return self.parse_values(csv.split(","))





