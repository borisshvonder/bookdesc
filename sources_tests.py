#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sources

import io
import os.path
import zipfile
import unittest

class FileSourceTest(unittest.TestCase):
    def setUp(self):
        self.fs = sources.FileSource("/some/path")

    def test_path(self):
        self.assertEqual("/some/path", self.fs.path())

    def test_open(self):
        self.fs._open = lambda path, mode: path+':'+mode
        self.assertEqual("/some/path:wb", self.fs.open("wb"))

class DirectorySourcesTest(unittest.TestCase):
    def setUp(self):
        self.ds = sources.DirectorySources("/some/path/")

    def tearDown(self):
        self.ds.close()

    def test_path(self):
        self.assertEqual("/some/path/", self.ds.path())

    def test_sources_non_recursive(self):
        self.ds._recursive = False
        self.ds._listdir = lambda path: ["dir/", "file", "notfile!"]
        self.ds._isfile = self.simple_isfile
        self.ds._isdir = self.simple_isdir
        self.ds._source_at = lambda path, recursive: sources.FileSource(path)
        srcs = list(self.ds.sources())
        self.assertEqual(os.path.join(self.ds.path(), "file"), srcs[0].path())
        self.assertEqual(1, len(srcs))

    def test_sources_recursive(self):
        def listdir(path):
            nonlocal self
            if path == self.ds.path():
                return ["dir/", "file", "notfile!"]
            elif path == os.path.join(self.ds.path(), "dir/"):
                return ["morefiles"]
            else:
                return []
        self.ds._listdir = listdir
        self.ds._isfile = self.simple_isfile
        self.ds._isdir = self.simple_isdir
        self.ds._source_at = lambda path, recursive: sources.FileSource(path)
        srcs = list(self.ds.sources())
        self.assertEqual(os.path.join(self.ds.path(), "dir/"), srcs[0].path())
        self.assertTrue(isinstance(srcs[0], sources.Sources))
        self.assertEqual(os.path.join(self.ds.path(), "file"), srcs[1].path())
        self.assertEqual(2, len(srcs))

    def simple_isfile(self, path):
        return path[-1] not in "/!"

    def simple_isdir(self, path):
        return path[-1] == "/"

class ZipTest(unittest.TestCase):

    def test_regular_file(self):
        inmem = io.BytesIO()
        with zipfile.ZipFile(inmem, "w") as file1:
            with file1.open("file2.txt", "w") as stream2:
                 stream2.write(b"some text")

        with zipfile.ZipFile(io.BytesIO(inmem.getbuffer())) as zip1:
            with sources.ZipFileListing("file1.zip", zip1) as file1:
                srcs = list(file1.sources())
                self.assertEqual(1, len(srcs))
                file2 = srcs[0]
                print(repr(file2))
                self.assertTrue(isinstance(file2, sources.ZipFileSource))
                self.assertEqual("file1.zip!/file2.txt", file2.path())
                self.assertEqual(b'some text', file2.open("r").read())

if __name__ == '__main__':
    unittest.main()
