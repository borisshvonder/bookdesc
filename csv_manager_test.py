#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import book_model
import keyvalue
import io
import csv_parser
import index
import pickle
import csv_manager
import unittest

class Book2FileStdTest(unittest.TestCase):
    def setUp(self):
        self.book1 = book_model.Book()
        self.book1.name = "book1"
        self.book1.authors = ["First Author"]
        self.book1.file = book_model.File()

    def test_no_authors(self):
        self.book1.authors = None
        self.assertEqual("noauthor", csv_manager._book2file_std(self.book1))

    def test_first_author_has_no_last_name(self):
        self.book1.authors = [""]
        self.assertEqual("noauthor", csv_manager._book2file_std(self.book1))
        self.book1.authors = ["", "Second Author"]
        self.assertEqual("a", csv_manager._book2file_std(self.book1))

    def test_russian_letters(self):
         self.book1.authors = ["Некто в Чорном"]
         self.assertEqual("ч", csv_manager._book2file_std(self.book1))

    def test_unusuzl_letter(self):
         self.book1.authors = ["&*^ *&^*&^&*"]
         self.assertEqual("0", csv_manager._book2file_std(self.book1))
        
        
class ManagerTest(unittest.TestCase):

    def build_manager(self, at_path):
        manager = csv_manager.Manager(path=at_path, 
            idx_backend=self.idxopen,
            isdir=lambda path: path.endswith('/'))
        manager._csvopen = self.csvopen
        manager._rename = self.rename
        manager._mtime = self.mtime
        return manager
        
    def setUp(self):
        self.dbs = {}
        self.virtualfiles = {} # in-memory filesystem
        self.manager = self.build_manager("/")

        self.book1 = book_model.Book()
        self.book1.name = "book1"
        self.book1.authors = ["First Author"]
        self.book1.file = book_model.File()
        self.book1.file.sha1 = b'0101'
        self.book1.file.md5 = b'0102'
        self.book2 = book_model.Book()
        self.book2.name = "book2"
        self.book2.authors = ["Second Author"]
        self.book2.file = book_model.File()
        self.book2.file.sha1 = b'0202'
        self.book2.file.md5 = b'0203'

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

    def idxopen(self, path):
        result = self.dbs.get(path)
        if not result:
            result = keyvalue.open(path, backend="memory")
            self.dbs[path] = result
        return result

    def test_put_one_book(self):
        self.manager.put(self.book1)
        self.manager.build_all_csvs()
        self.assert_single_book1("/a.csv.gz")
        pickled = pickle.dumps(self.book1)
        self.assertEqual(pickled, self.dbs["/a.idx"][self.book1.file.sha1])

    def assert_single_book1(self, path):
        vcsv = self.virtualfiles[path]
        lines = vcsv.contents.split('\r\n')
        self.assertTrue(len(lines)>=2)
        self.assertEqual(','.join(csv_parser.CSV_HEADER), lines[0])
        self.assertEqual('30313031,30313032,book1,First Author,,,,,,', lines[1])

    def test_read_csv(self):
        self.write_book_to_vfile("/a.csv.gz", self.book1)
        self.assert_single_book1("/a.csv.gz")
        self.manager.put(self.book2)
        self.manager.build_all_csvs()
        vcsv = self.virtualfiles["/a.csv.gz"]
        lines = vcsv.contents.split("\r\n")
        lines.sort()
        self.assertEqual(4, len(lines))
        self.assertEqual('', lines[0])
        self.assertEqual('30313031,30313032,book1,First Author,,,,,,', lines[1])
        self.assertEqual('30323032,30323033,book2,Second Author,,,,,,',
            lines[2])
        self.assertEqual(','.join(csv_parser.CSV_HEADER), lines[3])

    def test_will_not_read_csv_if_modtime_matches(self):
        self.write_book_to_vfile("/a.csv.gz", self.book1)
        idx = index.Index("/a.idx", idx_backend=self.idxopen)
        idx.set("mtime", self.mtime("/a.csv.gz"))
        idx.close()
        self.assert_single_book1("/a.csv.gz")
        self.manager.put(self.book2)
        self.manager.build_all_csvs()
        vcsv = self.virtualfiles["/a.csv.gz"]
        lines = vcsv.contents.split("\r\n")
        lines.sort()
        self.assertEqual(3, len(lines))
        self.assertEqual('', lines[0])
        self.assertEqual('30323032,30323033,book2,Second Author,,,,,,',
            lines[1])
        self.assertEqual(','.join(csv_parser.CSV_HEADER), lines[2])

    def test_single_file_mode(self):
        self.write_book_to_vfile("/file", self.book1)
        self.assert_single_book1("/file")
        self.manager = self.build_manager("/file")
        self.manager.put(self.book2)
        self.manager.build_all_csvs()
        vcsv = self.virtualfiles["/file"]
        lines = vcsv.contents.split("\r\n")
        lines.sort()
        self.assertEqual(4, len(lines))
        self.assertEqual('', lines[0])
        self.assertEqual('30313031,30313032,book1,First Author,,,,,,', lines[1])
        self.assertEqual('30323032,30323033,book2,Second Author,,,,,,',
            lines[2])
        self.assertEqual(','.join(csv_parser.CSV_HEADER), lines[3])

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

