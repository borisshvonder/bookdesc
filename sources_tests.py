#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os.path
import sources
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
        sources = list(self.ds.sources())
        self.assertEqual(os.path.join(self.ds.path(), "file"), 
            sources[0].path())
        self.assertEqual(1, len(sources))

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
        sources = list(self.ds.sources())
        self.assertEqual(os.path.join(self.ds.path(), "dir"), 
            sources[0].path())
        self.assertTrue(isinstance(source[0], Sources))
        self.assertEqual(os.path.join(self.ds.path(), "file"), 
            sources[1].path())
        self.assertEqual(2, len(sources))

    def simple_isfile(self, path):
        return path[-1] not in "/!"

    def simple_isdir(self, path):
        return path[-1] == "/"
    

if __name__ == '__main__':
    unittest.main()
