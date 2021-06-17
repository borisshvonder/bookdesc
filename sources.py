# -*- coding: UTF-8 -*-
"""Abstract view of the files as sources. Eventually will allow 
reading files from .zip and .gz archives
"""

import os
import os.path
import zipfile
import datetime

def source_at(path, recursive=True):
    """Return either a Source (if path is pointing to a file) or 
       Sources (if path is pointing to a directory or .zip. Or None if
       path does not point to file or directory"""
    if os.path.isfile(path):
        if recursive and _looks_like_zip(path):
            stream = open(path, "rb")
            unpacked = _attempt_open_zip(stream)
            if unpacked:
                return ZipFileListing(path, unpacked)
        return FileSource(path)
    elif os.path.isdir(path):
        return DirectorySources(path, recursive)

def _looks_like_zip(path):
    _, ext = os.path.splitext(path)
    return ext.strip().lower() == ".zip"

def _attempt_open_zip(stream):
    """Attempts opening a stream using zip. If attempt fails, the stream
       will be closed"""
    try:
        return zipfile.ZipFile(stream)
    except zipfile.BadZipFile as ex:
        stream.close()
        return None

class Sources:
    "An interface which describes the list of sources"

    def path(self):
        "Return path of this object"
        pass

    def sources(self): 
        "Return a generator of Source and Sources"
        pass

    def close(self):
        """The Sources object has to be closed after all its sources
           no longer in use"""
        pass

    def __str__(self): return self.path()

    def __enter__(self): return self
    def __exit__(self, type, value, traceback): self.close()

class Source:
    "Represents a single file"

    def path(self):
        "Return path of this source"
        pass

    def mtime(self):
        "Returns modification time of this source in seconds"

    def size(self):
        "Returns size of this source in bytes"

    def open(self, mode):
        """Return file-like object that can be read from. It has to be
           closed after it is no longer in use"""
        pass

    def __str__(self): return self.path()

class DirectorySources(Sources):
    """Represents a directory as a source of files"""

    def __init__(self, path, recursive=True):
        self._path = path
        self._recursive = recursive
        self._listdir = os.listdir
        self._isfile = os.path.isfile
        self._isdir = os.path.isdir
        self._source_at = source_at

    def path(self): return self._path

    def sources(self): return self._sources(self._path)

    def _sources(self, path):
        for name in self._listdir(path):
            fullname = os.path.join(path, name)
            if self._isfile(fullname):
                yield self._source_at(fullname, self._recursive)
            elif self._recursive and self._isdir(fullname):
                yield DirectorySources(fullname, True)

class FileSource(Source):
    def __init__(self, path):
        self._path = path
        self._open = open
        self._stat = os.stat(path)

    def path(self): return self._path

    def mtime(self): return self._stat.st_mtime

    def size(self): return self._stat.st_size

    def open(self, mode): return self._open(self._path, mode)


class ZipFileListing(Sources):
    """Represents contents of the .zip file"""

    def __init__(self, path, zip_file):
        self._path = path
        self._zip = zip_file

    def close(self): self._zip.close()

    def path(self): return self._path

    def sources(self):
        for name in self._zip.namelist():
            fullname = _zip_join(self._path, name)
            yield ZipFileSource(fullname, self._zip, name)

def _zip_join(zipname, name): return zipname + "!/" + name

class ZipFileSource(Source):
    """Represents single file inside .zip"""

    def __init__(self, path, zip_file, name):
        self._path = path
        self._zip = zip_file
        self._name = name
        self._info = zip_file.getinfo(name)

    def path(self): return self._path

    def mtime(self): 
        i = [*self._info.date_time]
        i.append(0) # microseconds
        return datetime.datetime(*i).timestamp()

    def size(self): return self._info.file_size

    def open(self, mode):
        if "w" in mode:
            raise ValueError("So far, .zip are treated readonly")
        return self._zip.open(self._name, "r")
        
