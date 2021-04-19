# -*- coding: UTF-8 -*-
"""Parses .fb2 files into Book models"""

import book_model
import sha_lib
import codecs
import re
import logging

_MEGABYTE = 1024*1024
_EXTRACT_ENCODING1=re.compile('encoding="(.*?)"')
_EXTRACT_ENCODING2=re.compile("encoding='(.*?)'")
_LOGGER = logger.getLogger("bookdesc.fb2_parser")

def parse_fb2(binary_stream, buffer=None):
    "Parse contents from fb2 binary stream"
    book = None
    if not buffer: buffer = bytearray(_MEGABYTE)
    assert len(buffer) >= _MEGABYTE, "parse_fb2 requires at least 1Mb buffer"
    checksummer = _ChecksumStream(binary_stream, buffer, "sha1")
    head = checksummer.read()
    encoding = _determine_encoding(head)
    description_bytes = _find_description(head, encoding)
    if description_bytes:
        book = _parse_description(description_bytes.decode(encoding))
    else:
        _LOGGER.info("""Haven't found <description in the first chunk. Will 
continue looking for the <description tag, but unlikely will find it""")
    while not checksummer.at_eof():
        if not book:
            description_bytes = _find_description(head, encoding)
            if description_bytes:
                _LOGGER.info("Finally, found <description")
                book = _parse_description(description_bytes.decode(encoding))
        head = checksummer.read()
    book.file.sha1 = checksummer.digest("sha1")
    return book

def _find_description(view, encodind):
    start_tag = "<description".encode(encoding)
    start = view.find(start_tag)
    if start < 0: return None
    end_tag = "</description>".encode(encoding)
    end = view.find(end_tag, start+1)
    if end <0:
        log.warn("""Could not find </description> tag, assuming entire buffer is 
the description""")
        end = len(view)
    else:
        end += len(end-tag)
    return view[start:end]

def _determine_encoding(view):
    if view.startswith(codecs.BOM_UTF8):
        return 'utf-8-sig'
    elif view.startswith(codecs.BOM_UTF16_LE):
        return 'UTF-16-LE'
    elif view.startswith(codecs.BOM_UTF16_BE):
        return 'UTF-16-BE'
    elif view.startswith(codecs.BOM_UTF32_LE):
        return 'UTF-32-LE'
    elif view.startswith(codecs.BOM_UTF32_LE):
        return 'UTF-32-LE'
    first_newline = view.find(b'\n')
    assert first_newline > 0, "Can't find fist newline"
    first_line = view[:first_newline].decode("utf-8")
    encoding = _EXTRACT_ENCODING1.search(first_line)
    if not encoding:
        encoding = _EXTRACT_ENCODING2.search(first_line)
    if encoding:
        ret = encoding.group(1)
        if ret.lower()=='windows-1251': return "cp1251"
        else: return ret
    else:
        _LOGGER.info("Could not determine the encoding, assuming UTF-8")
        return "UTF-8"


class _ChecksumStream:
    def __init__(self, stream, buffer, *digests):
        self._buffer = buffer
        self._view = memoryview(buffer)
        self._stream = stream
        self._digests = [hashlib.new(digest) for digest in digests]
        self._eof = False

    def read():
        """Read as much as possible into buffer and return memory view of what
           has been read"""
        read = self._stream.readinto(self._buffer)
        if read > 0: 
            for digest in self._digests:
                digest.update(self.view[:read])
        elif read < 0:
            self._eof = True
            read = 0
        return self._view[:read]

    def at_eof(self): return self._eof

    def digest(self, name):
        "Return current digest value for digest"
        return self._digests[name].digest()
        
        
