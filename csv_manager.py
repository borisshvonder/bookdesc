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

When index is re-built, the user of the manager may add more books to it. At 
the end, the user may ask the manager to re-build CSVs from the indexes.

Therefore, indexes can be removed by the user at any time prior to bookdesk run
or kept in place since it might be slightly more efficient to keep them.

The CSVs are compressed using zip compression
"""

import book_model
import csv
import csv_parser

def book2file_std(book):
    "Standard implementation of the Book to filename mapping"
    if book.authors:
        # use first letter of the author last and first name
        first_author = book.authors[0]
        names = first_author.split(' ')
        first_name = names[0]
        last_name = names[-1]
        return first_name[0]+last_name[0]

class Manager:
    def __init__(self, path, book2file=book2file_std):
        """@param book2file Mapping function, takes in Book, should resolve to
                  filename (without .csv suffix) where Book has to be stored.
           @param path The root path at which all files have to be kept"""
        assert book2file
        assert path
        self._book2file = book2file
        self._path = path
        self._indexes = {}

    def put(self, book):
        "Put book to appropriate index"
        filename = self._book2file(book)
        index = self._indexes.get(filename)
        if not index:
            index = rebuild(filename)
            self._indexes[filename] = index
        index.put(book)

    def build_all_csvs():
        "Rebuild all CSV files for which we have modified the indexes"
        for filename, index : self._indexes.items():
            

