#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import book_model
import index_test
import io
import csv_parser
import csv_manager
import unittest

class ManagerTest(unittest.TestCase):
    def setUp(self):
        self.dbs = {}
        self.virtualfiles = {} # in-memory filesystem
        self.manager = csv_manager.Manager(path="/",
            csvopen = self.csvopen,
            idxopen = self.idxopen,
            rename = self.rename)
        self.book1 = book_model.Book()
        self.book1.name = "book1"
        self.book1.authors = ["First Author"]
        self.book1.file = book_model.File()
        self.book1.file.sha1 = b'0102'

    def tearDown(self):
        self.manager.close()

    def rename(self, old_name, new_name):
        old = self.virtualfiles[old_name]
        self.virtualfiles[new_name] = old
        del self.virtualfiles[old_name]

    def csvopen(self, path, mode):
        if mode.startswith("r"):
            existing = self.virtualfiles.get(path)
            if existing: return existing
        new_file = VirtualFile()
        self.virtualfiles[path] = new_file
        return new_file

    def idxopen(self, path, mode):
        result = self.dbs.get(path)
        if not result:
            result = index_test.InMemoryDb()
            self.dbs[path] = result
        return result

    def test_put_one_book(self):
        self.manager.put(self.book1)
        self.manager.build_all_csvs()
        vcsv = self.virtualfiles["/af.csv.gz"]
        lines = vcsv.getvalue().split("\r\n")
        self.assertTrue(len(lines)>=2)
        self.assertEqual(','.join(csv_parser.CSV_HEADER), lines[0])
        self.assertEqual('book1,First Author,,,30313032,,,,', lines[1])
        self.assertEqual(1, len(self.dbs["/af.idx"].db))
        self.assertEqual(self.book1, self.dbs["/af.idx"][self.book1.file.sha1])

        
class VirtualFile(io.StringIO):
    def close(self): pass # do not empty buffer like StringIO does

if __name__ == '__main__':
    unittest.main()

