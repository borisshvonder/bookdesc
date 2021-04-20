# -*- coding: UTF-8 -*-
"""Parses .fb2 files into Book models"""

import book_model
import hashlib
import codecs
import re
import logging
import xml.etree.ElementTree as ET
import io

_LOGGER = logging.getLogger("bookdesc.fb2_parser")

_MEGABYTE = 1024*1024

def parse(binary_stream, buffer=None):
    """Parse contents from fb2 binary stream. Returns None if stream does not 
    contain any books (for ex, is empty)"""
    book = None
    if not buffer: buffer = bytearray(_MEGABYTE)
    if len(buffer) < _MEGABYTE: 
        raise ValueError("parse_fb2 requires at least 1Mb buffer, you gave "+\
            str(len(buffer))+" bytes")
    checksummer = _ChecksumStream(binary_stream, buffer, "sha1")
    size = checksummer.read()
    if not size: return None
    encoding = _determine_encoding(buffer, size)
    description_bytes = _find_description(buffer, size, encoding)
    if description_bytes:
        xml = codecs.decode(description_bytes, encoding, errors="ignore")
        book = _parse_description(xml)
    else:
        _LOGGER.info("""Haven't found <description in the first chunk. Will 
continue looking for the <description tag, but unlikely will find it""")
    while size:
        if not book:
            description_bytes = _find_description(buffer, size, encoding)
            if description_bytes:
                _LOGGER.info("Finally, found <description")
                xml = codecs.decode(description_bytes, encoding, errors="ignore")
                book = _parse_description(xml)
        size = checksummer.read()
    if book:
        book.file = book_model.File()
        book.file.sha1 = checksummer.digest("sha1")
    return book

def _find_description(buffer, size, encoding):
    start_tag = "<description".encode(encoding)
    start = buffer.find(start_tag, 0, size)
    if start < 0: return None
    end_tag = "</description>".encode(encoding)
    end = buffer.find(end_tag, start+1, size)
    if end <0:
        log.warn("""Could not find </description> tag, assuming entire buffer is 
the description""")
        end = len(view)
    else:
        end += len(end_tag)
    return memoryview(buffer)[start:end]

_EXTRACT_ENCODING1=re.compile('encoding="(.*?)"')
_EXTRACT_ENCODING2=re.compile("encoding='(.*?)'")

def _determine_encoding(buffer, size):
    ret = None
    if size >= 4:
        if buffer.startswith(codecs.BOM_UTF8):
            ret = 'utf-8-sig'
        elif buffer.startswith(codecs.BOM_UTF16_LE):
            ret = 'UTF-16-LE'
        elif buffer.startswith(codecs.BOM_UTF16_BE):
            ret = 'UTF-16-BE'
        elif buffer.startswith(codecs.BOM_UTF32_LE):
            ret = 'UTF-32-LE'
        elif buffer.startswith(codecs.BOM_UTF32_LE):
            ret = 'UTF-32-LE'

    if not ret:
        first_newline = buffer.find(b'\n', 0, size)
        if first_newline > 0:
            view = memoryview(buffer)
            first_line = codecs.decode(view[:first_newline], "utf-8", 
                errors="ignore")
            encoding = _EXTRACT_ENCODING1.search(first_line)
            if not encoding:
                encoding = _EXTRACT_ENCODING2.search(first_line)
            if encoding:
                ret = encoding.group(1)
                if ret.lower().startswith('windows-'): 
                    ret = "cp"+ret[len('windows-'):]
    if ret:
        _LOGGER.info("Encoding is %s", ret)
        return ret
    else:
       _LOGGER.info("Could not determine the encoding, assuming UTF-8")
       return "UTF-8"

def _parse_description(xml):
    """Interesting parts of FB2 to look at (root is <description>):
    publish-info/book-name <- original book name
    publish-info/year <- year of publication
    publish-info/isbn
    title-info/*author/{first-name, middle-name, last-name}
    title-info/book-title <- use in case no book name
    title-info/date <- use in case no year
    title-info/annotation
    document-info/*author/{...} <- use only if no authors
    """
    xml = _remove_namespaces(xml)
    book = book_model.Book()

    desc = ET.fromstring(xml)
    publish_info = desc.find("publish-info")
    book.name = _first_text(publish_info, "book-name")
    book.year = _first_int(publish_info, "year", "date")
    book.isbn = _first_text(publish_info, "isbn")

    title_info = desc.find("title-info")
    book.authors = _parse_authors(title_info)
    if not book.name:
        book.name = _first_text(title_info, "book-title")
    if not book.year:
        book.year = _first_int(title_info, "date")
    annotation = None if title_info is None else title_info.find("annotation")
    book.annotation = _dump_text(annotation)
    if not book.authors:
        document_info = desc.find("document-info")
        book.authors = _parse_authors(document_info)
    book.metatext = _dump_text(desc)

    return book

_LOOKS_LIKE_TAG=re.compile("<[^>]*?>", re.MULTILINE)
_COLON=re.compile("[:]")

def _remove_namespaces(xml):
    """Since we are parsing just the <description> part of the FB2, the 
    namespaces will not be resolved. Therefore, we have to either:
    1) use lxml which can withstand undeclared namespaces,
    2) or use regexp'es/custom code parsing,
    3) or remove namespaces prior to parsing

    For practical reasons 3rd option was selected since it does not bring
    additional dependencies (lxml) and is easier to support.

    Even if this approach isn't technically 100% correct, it is practical
    for realworld FB2 files"""
    result = io.StringIO()
    pos = 0
    m = _LOOKS_LIKE_TAG.search(xml, pos)
    while m:
        result.write(xml[pos:m.start()])
        no_colons = _replace_namespaces_in_tag(m.group())
        result.write(no_colons)
        pos = m.end()
        m = _LOOKS_LIKE_TAG.search(xml, pos)

    result.write(xml[pos:])
    return result.getvalue()

def _replace_namespaces_in_tag(s):
    result = io.StringIO()
    pos = 0
    colon = s.find(':', pos)
    while colon>=0:
        token_start = colon
        while token_start > 0 and s[token_start-1] not in " <'\"":
            token_start -=1
        result.write(s[token_start:colon])
        pos = colon + 1
        colon = s.find(':', pos)

    result.write(s[pos:])
    return result.getvalue()

def _parse_authors(parent):
    author_nodes = [] if parent is None else parent.findall("author")
    names = [ (a.find("first-name"), 
               a.find("middle-name"),
               a.find("last-name")) for a in author_nodes]
    return [_join(ns) for ns in names]

def _join(xml_elements):
    texts = [e.text for e in xml_elements]
    not_empty = [text for text in texts if text != None and text != ""]
    return " ".join(not_empty)

def _first_text(root, *tags):
    if root is None: return None
    for tag in tags:
        for node in root.findall(tag):
            text = _strip(node.text)
            if text: return text
    return None
        
def _first_int(root, *tags):
    if root is None: return None
    for tag in tags:
        for node in root.findall(tag):
            text = _strip(node.text)
            if text:
                try:
                    return int(text)
                except:
                    _LOGGER.info("Can't parse book year:'%s'", text)
    return None

def _dump_text(root):
    acc = io.StringIO()
    empty = True
    def _dump(node):
        nonlocal acc
        nonlocal empty
        if node is None: return None
        text = _strip(node.text)
        if text:
            if empty:
                empty = False
            else:
                acc.write(' ')
            acc.write(text)
        for child in node:
            _dump(child)
    _dump(root)
    return acc.getvalue()

def _strip(text):
    if text:
        text = text.strip()
        return text if text != "" else None
    else:
        return None

class _ChecksumStream:
    def __init__(self, stream, buffer, *digests):
        self._buffer = buffer
        self._view = memoryview(buffer)
        self._stream = stream
        self._digests = {}
        for digest in digests:
            self._digests[digest] = hashlib.new(digest)

    def read(self):
        """Read as much as possible into buffer and return number of bytes
           read. Returns 0 or None when EOF"""
        read = self._stream.readinto(self._buffer)
        if read > 0: 
            result = self._view[:read]
            for digest in self._digests.values():
                digest.update(result)
        return read

    def at_eof(self): return self._eof

    def digest(self, name):
        "Return current digest value for digest"
        return self._digests[name].digest()

