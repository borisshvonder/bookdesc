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
        self.book1.file.sha1 = b'0101'
        self.book2 = book_model.Book()
        self.book2.name = "book2"
        self.book2.authors = ["Second Author"]
        self.book2.file = book_model.File()
        self.book2.file.sha1 = b'0202'

    def tearDown(self):
        self.manager.close()

    def rename(self, old_name, new_name):
        old = self.virtualfiles[old_name]
        self.virtualfiles[new_name] = old
        del self.virtualfiles[old_name]

    def csvopen(self, path, mode):
        vfile = self.virtualfiles.get(path)
        if not vfile:
            vfile = VirtualFile(path)
            self.virtualfiles[path] = vfile
        return vfile.open()

    def idxopen(self, path, mode):
        result = self.dbs.get(path)
        if not result:
            result = index_test.InMemoryDb()
            self.dbs[path] = result
        return result

    def test_put_one_book(self):
        self.manager.put(self.book1)
        self.manager.build_all_csvs()
        self.assert_single_book1()
        self.assertEqual(self.book1, self.dbs["/a.idx"][self.book1.file.sha1])

    def assert_single_book1(self):
        vcsv = self.virtualfiles["/a.csv.gz"]
        lines = vcsv.contents.split('\r\n')
        self.assertTrue(len(lines)>=2)
        self.assertEqual(','.join(csv_parser.CSV_HEADER), lines[0])
        self.assertTrue(lines[1].startswith('book1,First Author'))

    def test_read_csv(self):
        with self.csvopen("/a.csv.gz", "wb") as csv_file:
            csv_file.write(','.join(csv_parser.CSV_HEADER))
            csv_file.write('\r\n')
            csv_file.write('book1,First Author,,,30313032,,,,')
            csv_file.write('\r\n')
        self.assert_single_book1()
        self.manager.put(self.book2)
        self.manager.build_all_csvs()
        vcsv = self.virtualfiles["/a.csv.gz"]
        lines = vcsv.contents.split("\r\n")
        lines.sort()
        self.assertEqual('', lines[0])
        self.assertEqual(','.join(csv_parser.CSV_HEADER), lines[1])
        self.assertTrue(lines[2].startswith('book1,First Author'))
        self.assertTrue(lines[3].startswith('book2,Second Author'))
        

class VirtualFile:
    def __init__(self, path):
        self.path = path
        self.contents = ""

    def open(self): return VirtualStream(self)

    def __str__(self): return self.path

        
class VirtualStream(io.StringIO):
    def __init__(self, vfile):
        io.StringIO.__init__(self, vfile.contents)
        self.vfile = vfile

    def close(self): 
        io.StringIO.flush(self)
        self.vfile.contents = self.getvalue()
        #print(str(self.vfile) + "->" + self.vfile.contents)

if __name__ == '__main__':
    unittest.main()

