#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import book_model
import index_test
import io
import csv_parser
import index
import pickle
import csv_manager
import unittest

class ManagerTest(unittest.TestCase):
    def setUp(self):
        self.dbs = {}
        self.virtualfiles = {} # in-memory filesystem
        self.manager = csv_manager.Manager(path="/")
        self.manager._csvopen = self.csvopen
        self.manager._idxopen = self.idxopen
        self.manager._rename = self.rename
        self.manager._mtime = self.mtime

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

    def mtime(self, path): return (0, 0)

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
        pickled = pickle.dumps(self.book1)
        self.assertEqual(pickled, self.dbs["/a.idx"][self.book1.file.sha1])

    def assert_single_book1(self):
        vcsv = self.virtualfiles["/a.csv.gz"]
        lines = vcsv.contents.split('\r\n')
        self.assertTrue(len(lines)>=2)
        self.assertEqual(','.join(csv_parser.CSV_HEADER), lines[0])
        self.assertTrue(lines[1].startswith('book1,First Author'))

    def test_read_csv(self):
        self.write_book_to_vfile("/a.csv.gz", self.book1)
        self.assert_single_book1()
        self.manager.put(self.book2)
        self.manager.build_all_csvs()
        vcsv = self.virtualfiles["/a.csv.gz"]
        lines = vcsv.contents.split("\r\n")
        lines.sort()
        self.assertEqual(4, len(lines))
        self.assertEqual('', lines[0])
        self.assertEqual(','.join(csv_parser.CSV_HEADER), lines[1])
        self.assertTrue(lines[2].startswith('book1,First Author'))
        self.assertTrue(lines[3].startswith('book2,Second Author'))

    def test_will_not_read_csv_if_modtime_matches(self):
        self.write_book_to_vfile("/a.csv.gz", self.book1)
        idx = index.Index("/a.idx", db_impl=self.idxopen)
        idx.set("mtime", self.mtime("/a.csv.gz"))
        idx.close()
        self.assert_single_book1()
        self.manager.put(self.book2)
        self.manager.build_all_csvs()
        vcsv = self.virtualfiles["/a.csv.gz"]
        lines = vcsv.contents.split("\r\n")
        lines.sort()
        self.assertEqual(3, len(lines))
        self.assertEqual('', lines[0])
        self.assertEqual(','.join(csv_parser.CSV_HEADER), lines[1])
        self.assertTrue(lines[2].startswith('book2,Second Author'))

    def write_book_to_vfile(self, path, book):
        with self.csvopen(path, "wb") as csv_file:
            csv_file.write(','.join(csv_parser.CSV_HEADER))
            csv_file.write('\r\n')
            csv_file.write(','.join(csv_parser.to_row(book)))
            csv_file.write('\r\n')
        

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

