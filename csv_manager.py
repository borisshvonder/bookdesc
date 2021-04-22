# -*- coding: UTF-8 -*-
"""CSV manager keeps track of multiple CSV files which contain information 
about books broken down by some arbitrary key (configurable). For example we may
choose to break down books simply by first 4 letters in the book title. In that
case following books will end up:
1) The Joy of Sex: The Ultimate Revised Edition -> thej.csv
2) The Joy of Gay Sex                           -> thej.csv (same)
3) The Love Book                                -> thel.csv

To make its work efficient, the manager also builds CSV indexes in files with
.idx extension (for the above example, this would be thej.idx and thel.idx).

These indexes are rebuilt from the CSVs on first attempt to use the index. This
is done because parsing CSVs is faster than parsing FB2s, and, because FB2s may
not be available already. 

The manager remembers the CSV file length + modification time in the index, so 
if that information matches, there is no need to rebuild the index.

When index is re-built, the user of the manager may add more books to it. At 
the end, the user may ask the manager to re-build CSVs from the indexes.

Therefore, indexes can be removed by the user at any time prior to bookdesk run
or kept in place since it is more efficient to keep them.

The CSV files are compressed using gzip compression by default
"""

import book_model
import csv
import csv_parser
import gzip
import os
import os.path
import shelve
import index

def _book2file_std(book):
    "Standard implementation of the Book to filename mapping"
    if book.authors:
        # use first letter of the author last name
        first_author = book.authors[0]
        names = first_author.split(' ')
        last_name = names[-1]
        return last_name[0].lower()
    else:
        return "noauthor"

def _mtime_os(path):
    "Standard os.stat() implementation for mtime"
    try:
        stat = os.stat(path)
        return (stat.st_mtime, stat.st_size)
    except FileNotFoundError:
        return None

class Manager:
    def __init__(self, path, book2file=_book2file_std, csv_ext=".csv.gz", 
                       idx_ext=".idx"):
        """@param path The root path at which all files have to be kept
           @param book2file Mapping function, takes in Book, should resolve to
                  filename (without .csv suffix) where Book has to be stored."""
        assert book2file
        assert path
        assert csv_ext is not None
        assert idx_ext is not None
        assert csv_ext != idx_ext
        self._path = path
        self._book2file = book2file
        self._csv_ext = csv_ext
        self._idx_ext = idx_ext

        # dependency-injectable (for testing)
        self._csvopen = gzip.open
        self._idxopen = shelve.open
        self._rename = os.rename
        self._mtime = _mtime_os

        self._indexes = {}

    def close(self):
        "Close all indexes opened so far"
        for idx in self._indexes.values():
            idx.close()
        self._indexes = {}

    def __enter__(self): pass
    def __exit__(self, type, value, traceback): self.close()

    def put(self, book):
        "Put book to appropriate index"
        filename = self._book2file(book)
        idx = self._indexes.get(filename)
        if not idx:
            idx = self._rebuild(filename)
            self._indexes[filename] = idx
        idx.save(book)

    def build_all_csvs(self):
        "Rebuild all CSV files for which we have modified the indexes"
        for fname, idx in self._indexes.items():
            old_fname = self._csv_path(fname)
            new_fname = old_fname + "_new"
            with self._csvopen(new_fname, "wb") as csv_stream:
                writer = csv.writer(csv_stream, quoting=csv.QUOTE_MINIMAL)
                writer.writerow(csv_parser.CSV_HEADER)
                for book in idx.list():
                    row = csv_parser.to_row(book)
                    writer.writerow(row)
            idx.set("mtime", self._mtime(new_fname))
            self._rename(new_fname, old_fname)

    def _rebuild(self, filename):
        idx_path = self._idx_path(filename)
        idx = index.Index(idx_path, db_impl=self._idxopen)
        csv_path = self._csv_path(filename)

        current_mtime = self._mtime(csv_path)
        file_does_not_exist = not current_mtime
        if file_does_not_exist: return idx

        index_mtime_matches_current = current_mtime == idx.get("mtime")
        if index_mtime_matches_current: return idx

        parser = csv_parser.Parser()
        with self._csvopen(csv_path, "rb") as csv_file:
            reader = csv.reader(csv_file)
            header = True
            for row in reader:
                if header:
                    parser.parse_header(row)
                    header = False
                else:
                    book = parser.parse_row(row)
                    idx.save(book)
        current_mtime = self._mtime(csv_path)
        idx.set("mtime", current_mtime)
        return idx

    def _csv_path(self, filename):
        return os.path.join(self._path, filename + self._csv_ext)

    def _idx_path(self, filename):
        return os.path.join(self._path, filename + self._idx_ext)
