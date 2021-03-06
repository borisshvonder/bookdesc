# -*- coding: UTF-8 -*-
"""Parses .fb2 files into Book models"""

import book_model
import hashlib
import codecs
import re
import log
import xml.etree.ElementTree as ET
import io

_LOGGER = log.get("bookdesc.fb2_parser")

_MEGABYTE = 1024*1024
_MAX_ANNOTATION_LEN=1024
_MAX_METATEXT_LEN=4096

def parse(binary_stream, buffer=None):
    """Parse contents from fb2 binary stream. Returns None if stream does not 
    contain any books (for ex, is empty)"""
    book = None
    if not buffer: buffer = bytearray(_MEGABYTE)
    if len(buffer) < _MEGABYTE: 
        raise ValueError("parse_fb2 requires at least 1Mb buffer, you gave "+\
            str(len(buffer))+" bytes")
    checksummer = _ChecksumStream(binary_stream, buffer, "sha1", "md5")
    size = checksummer.read()
    if not size: return None
    encoding = _determine_encoding(buffer, size)
    description_bytes, full_desc = _find_description(buffer, size, encoding)
    if description_bytes:
        xml = codecs.decode(description_bytes, encoding, errors="ignore")
        book = _parse_description(xml, full_desc)
    else:
        _LOGGER.info("""Haven't found <description in the first chunk. Will 
continue looking for the <description tag, but unlikely will find it""")
    while size:
        if not book:
            description_bytes, full_desc = _find_description(buffer, size, 
                encoding)
            if description_bytes:
                _LOGGER.info("Finally, found <description")
                xml = codecs.decode(description_bytes, encoding, errors="ignore")
                book = _parse_description(xml, full_desc)
        size = checksummer.read()
    if book:
        book.file = book_model.File()
        book.file.sha1 = checksummer.digest("sha1")
        book.file.md5 = checksummer.digest("md5")
    return book

def _find_description(buffer, size, encoding):
    start_tag = "<description".encode(encoding)
    start = buffer.find(start_tag, 0, size)
    if start < 0: return None
    end_tag = "</description>".encode(encoding)
    end = buffer.find(end_tag, start+1, size)
    if end <0:
        _LOGGER.info("Could not find </description> tag, assuming entire " + 
                        "buffer is the description")
        return memoryview(buffer)[start:size], False
    else:
        end += len(end_tag)
    return memoryview(buffer)[start:end], True

_EXTRACT_ENCODING1=re.compile('encoding="(.*?)"')
_EXTRACT_ENCODING2=re.compile("encoding='(.*?)'")

def _determine_encoding(buffer, size):
    ret = None
    if size >= 4:
        if buffer.startswith(codecs.BOM_UTF8):
            ret = 'UTF-8'
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

def _parse_description(xml, full_desc):
    book = None
    if full_desc:
        book = _parse_description_via_xml(xml)
    if not book:
        _LOGGER.info("Attempting regexp-based parsing")
        book = _parse_description_via_regexpes(xml)
        if not full_desc:
            if not book.title: 
                _LOGGER.debug(xml)
                _LOGGER.warn("Haven't found title in garbled xml")
    return book

_COMPACT_WHITESPACES = re.compile(r"\s+")
def _compact_whitespaces(text):
    return _COMPACT_WHITESPACES.sub(' ', text.strip())

def _parse_description_via_xml(xml):
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

    desc = None
    try:
        desc = ET.fromstring(xml)
    except ET.ParseError as ex:
        _LOGGER.debug(xml)
        _LOGGER.info("Can't parse xml: %s", ex)
        return None
    publish_info = desc.find("publish-info")
    book.name = _first_text(publish_info, "book-name")
    book.year = _first_year(publish_info, "year", "date")
    book.isbn = _first_text(publish_info, "isbn")

    title_info = desc.find("title-info")
    book.authors = _parse_authors(title_info)
    if not book.name:
        book.name = _first_text(title_info, "book-title")
    if not book.year:
        book.year = _first_year(title_info, "date")
    annotation = None if title_info is None else title_info.find("annotation")
    book.annotation = _dump_text(annotation, _MAX_ANNOTATION_LEN)
    if not book.authors:
        document_info = desc.find("document-info")
        book.authors = _parse_authors(document_info)
    book.metatext = _compact_whitespaces(_dump_text(desc, _MAX_METATEXT_LEN))

    return book

_COLON=re.compile("[:]")

_LOOKS_LIKE_TAG=re.compile("<[^>]*?>", re.MULTILINE)
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
        while token_start > 0 and s[token_start-1] not in " </'\"\r\n\f\t\v":
            token_start -= 1
        result.write(s[pos:token_start])
        pos = colon + 1
        colon = s.find(':', pos)

    result.write(s[pos:])
    tag = result.getvalue()
    return tag

def _parse_authors(parent):
    author_nodes = [] if parent is None else parent.findall("author")
    names = [ (a.find("first-name"), 
               a.find("middle-name"),
               a.find("last-name")) for a in author_nodes]
    joined = [_join(ns) for ns in names]
    return [a for a in joined if a and not a in _BAN_AUTHORS]

_BAN_AUTHORS=(
    "author unknown",
    "?????????? ????????????????????",
    "?????????????????? ??????????",
    "???????????????????? ??????????",
    "?????????????????????????????? ??????????",
    "?????? ????????????",
    "retroshare retroshare",    # he has mass-generated fb2 books
    "vitmaier",                 # some fb2 books producer
    "andrey ch",                # another book builder
    "consul",                   # another retroshare "entusiast"
    "ddd hhh",                  # someone was veeeery lazy while building fb2
)

def _join(xml_elements):
    texts = [e.text for e in xml_elements if e is not None]
    not_none = [text.strip() for text in texts if text != None]
    not_empty = [text for text in not_none if text]
    return " ".join(not_empty)

def _first_text(root, *tags):
    if root is None: return None
    for tag in tags:
        for node in root.findall(tag):
            text = _strip(node.text)
            if text: return text
    return None

_STR_2_YEAR=re.compile(r"\d\d\d\d")

def _string_to_year(s):
    try:
        return int(s)
    except ValueError:
        m = _STR_2_YEAR.search(s)
        if m:
            year = int(m.group(0))
            _LOGGER.info("Could not convert '%s' to int, assuming it is %s",
                s, year)
        else:
            _LOGGER.info("Could not parse '%s' as year", s)

def _first_year(root, conversion=int, *tags):
    return _first_int(root, _string_to_year, *tags)
    
def _first_int(root, conversion, *tags):
    if root is None: return None
    for tag in tags:
        for node in root.findall(tag):
            text = _strip(node.text)
            if text:
                try:
                    return conversion(text)
                except ValueError as ex:
                    _LOGGER.info("Can't parse int: '%s' due to %s", 
                        text, ex)
    return None

def _dump_text(root, max_len):
    acc = BoundStringIO(max_len)
    written = 0
    empty = True
    def _dump(node):
        nonlocal acc
        nonlocal empty
        if acc.full() or node is None: return
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

def _make_tag_regexp(tag): 
    return re.compile("<"+tag+"[ >](.*?)</"+tag+">", re.DOTALL)
_BOOK_NAME_RE =_make_tag_regexp("book-name")
_BOOK_TITLE_RE = _make_tag_regexp("book-title")
_BOOK_YEAR_RE = _make_tag_regexp("year")
_ISBN_YEAR_RE = _make_tag_regexp("isbn")
_AUTHORS_RE = _make_tag_regexp("author")
_DATE_RE = _make_tag_regexp("date")
_ANNOTATION_RE = _make_tag_regexp("annotation")

def _parse_description_via_regexpes(xml):
    book = book_model.Book()
    book.title = _find_first_tag_text(xml, _BOOK_NAME_RE)
    book.authors = _find_all_tag_texts(xml, _AUTHORS_RE)
    if not book.title: book.title = _find_first_tag_text(xml, _BOOK_TITLE_RE)
    book.year = _find_first_tag_int(xml, _BOOK_YEAR_RE)
    if not book.year: book.year =_find_first_tag_int(xml, _DATE_RE)
    book.annotation = _find_first_tag_text(xml, _ANNOTATION_RE)
    if book.annotation and len(book.annotation) > _MAX_ANNOTATION_LEN:
        book.annotation = book.annotation[:_MAX_ANNOTATION_LEN]
    book.metatext = _remove_all_tags(xml)
    if book.metatext and len(book.metatext) > _MAX_METATEXT_LEN:
        book.metatext = book.metatext[:_MAX_METATEXT_LEN:]
    return book

def _find_all_tag_texts(xml, regexp):
    result = []
    pos = 0
    match = regexp.search(xml, pos)
    while match:
        text = _remove_all_tags(match.group())
        if text: result.append(text)
        pos = match.end()
        match = regexp.search(xml, pos)
    return result


def _find_first_tag_int(xml, regexp):
    pos = 0
    match = regexp.search(xml, pos)
    while match:
        text = _remove_all_tags(match.group())
        if text: 
            try:
                return int(text)
            except ValueError: pass
        pos = match.end()
        match = regexp.search(xml, pos)

def _find_first_tag_text(xml, regexp):
    pos = 0
    match = regexp.search(xml, pos)
    while match:
        text = _remove_all_tags(match.group())
        if text: return text
        pos = match.end()
        match = regexp.search(xml, pos)

def _remove_all_tags(text):
    result = io.StringIO()
    pos = 0
    match = _LOOKS_LIKE_TAG.search(text, pos)
    while match:
        result.write(text[pos:match.start()])
        pos = match.end()
        match = _LOOKS_LIKE_TAG.search(text, pos)
    end = len(text)
    result.write(text[pos:])
    return _compact_whitespaces(result.getvalue())

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

class BoundStringIO:
    "StringIO, but with a limited size"

    def __init__(self, max_len):
        self._len = 0
        self._max_len = max_len
        self._io = io.StringIO()

    def write(self, sequence):
        if self.full(): return
        new_len = self._len + len(sequence)
        if new_len > self._max_len:
            to_write = self._max_len - self._len
            self._io.write(sequence[:to_write])
            self._len = self._max_len
        else:
            self._io.write(sequence)
            self._len = new_len

    def full(self): return self._len == self._max_len

    def getvalue(self): return self._io.getvalue()
