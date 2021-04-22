# -*- coding: UTF-8 -*-
"""Abstract view of the files as sources. Eventually will allow 
reading files from .zip and .gz archives
"""

import os
import os.path

def source_at(path, recursive=True):
    """Return either a Source (if path is pointing to a file) or 
       Sources (if path is pointing to a directory or .zip. Or None if
       path does not point to file or directory"""
    if os.path.isfile(path):
        return FileSource(path)
    elif os.path.isdir(path):
        return DirectorySources(path, recursive)


class Sources:
    "An interface which describes the list of sources"

    def path(self):
        "Return path of this object"
        pass

    def sources(self): 
        "Return a generator of Source's"
        pass

    def close(self):
        """The Sources object has to be closed after all its sources
           no longer in use"""
        pass

    def __enter__(self): pass
    def __exit__(self, type, value, traceback): self.close()

class Source:
    "Represents a single file"

    def path(self):
        "Return path of this source"
        pass

    def open(self, mode):
        """Return file-like object that can be read from. It has to be
           closed after it is no longer in use"""
        pass

class DirectorySources(Sources):
    """Represents a directory as a source of files"""

    def __init__(self, path, recursive=True):
        self._path = path
        self._recursive = recursive
        self._listdir = os.listdir
        self._isfile = os.path.isfile
        self._isdir = os.path.isdir

    def path(self): return self._path

    def sources(self): return self._sources(self._path)

    def _sources(self, path):
        for name in self._listdir(path):
            fullname = os.path.join(path, name)
            if self._isfile(fullname):
                yield FileSource(fullname)
            elif self._recursive and self._isdir(fullname):
                for source in self._sources(fullname):
                    yield source

class FileSource(Source):
    def __init__(self, path):
        self._path = path
        self._open = open

    def path(self): return self._path

    def open(self): return self._open(self._path)
