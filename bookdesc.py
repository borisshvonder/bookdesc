#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Book descriptions CSV generator.

h1. History and Why
This is a successor to Jabot project https://github.com/borisshvonder/jabot).
I have no time to properly support the project and it does not seem to be easy
for new developers to pick up since the project was primarilly written as
retrospective on what I have learned in a few previous years. It was not built
for people to pick up easilly since it contains some uncommon features which
might not be easy to grasp. It also wasn't easy to operate since it required
Apache Solr and running retroshare node.

The bookdesc project, on the other hand, is supposed to be much simplier, 
easilly understood and operate. Thus:

* Python was chosen as the implementation language.
* bookdesc will NOT generate fulltext index.
* In fact, bookdesc will not have any indexing support whatsoever.
* Instead, it will simply generate one or more CSV files which will contain 
  books metadata (book name, ISBN, authors AND SHA1/MD5 book checksums). 
  Therefore, the user can search simply using grep.
* There will be no extra dependencies required whatsoever.

h1. Goals
* Ability to parse fb2 files directly or inside .zip archives.
* Incremental CSV updates. It is very much desirable that files will be deduped
  based on their SHA-1 signature.
* Ability to split CSV files into sizeable chunks (perhaps, by author first 
  letter, a.csv, b.csv and so on).
* It should be possible to use the bookdesc module as a library in other
  python projects.
* Simple to support code, minimal number of dependencies

h1. Non-goals
* No fulltext seach.
* In fact, no search at all.
* No import from existing databases and/or CSVs.
"""

VERSION=1.3

import gzip
import csv
import keyvalue
import argparse
import os
import os.path
import sys

import log
import csv_parser
import csv_manager
import sources
import fb2_parser
import i18n

_LOGGER = log.get("bookdesc")

class BookDesc:
    "Frontend class for the entire library"
    
    def __init__(self, outpath, dumb, idx_backend=keyvalue.open):
        self._dumb = dumb
        if self._dumb:
            self._output = gzip.open(outpath, "wt")
            self._writer = csv.writer(self._output, quoting=csv.QUOTE_MINIMAL)
            self._writer.writerow(csv_parser.CSV_HEADER)
            _LOGGER.debug("Created CSV at %s", outpath)
        else:
            self._manager = csv_manager.Manager(outpath, 
                idx_backend=idx_backend)
            _LOGGER.debug("Initialized Manager at %s", outpath)
        self._parse_buffer = bytearray(1024*1024)

    def close(self):
        if self._dumb:
            self._output.close()
        else:
            self._manager.close()

    def __enter__(self): return self
    def __exit__(self, type, value, traceback): self.close()

    def parse_inputs(self, *inputs):
        "Parse inputs(sequence of strings), only parse .fb2 srcs"
        for input in inputs:
            src_or_srcs = sources.source_at(input)
            if src_or_srcs:
                self.parse(src_or_srcs)
            else:
                _LOGGER.warning("Input %s cannot be recognized", input)

    def parse(self, src_or_srcs):
        "Parse all FB2 file from src or srcs"
        _LOGGER.debug("Scanning %s", src_or_srcs)
        if isinstance(src_or_srcs, sources.Sources):
            srcs = src_or_srcs
            _LOGGER.debug("Found Sources %s", srcs)
            try:
                for src in srcs.sources():
                    self.parse(src)
            finally:
                srcs.close()
        elif isinstance(src_or_srcs, sources.Source):
            src = src_or_srcs
            _, ext = os.path.splitext(src.path())
            ext = ext.strip().lower()
            if ext == ".fb2":
                self.parse_fb2(src)
        else: assert src_or_srcs is None, "Got unknown src: "\
                    + str(src_or_srcs)

    def parse_fb2(self, fb2_src):
        "Parse src which MUST be an FB2 file"
        _LOGGER.info("Parsing %s", fb2_src)
        with fb2_src.open("rb") as stream:
            book = None
            try:
                book = fb2_parser.parse(stream, buffer=self._parse_buffer)
                book.file.path = fb2_src.path()
                book.file.mod_time = fb2_src.mtime()
                book.file.size = fb2_src.size()
            except:
                _LOGGER.exception("FB2 '%s' could not be parsed", fb2_src)
                book = None
            if book: 
                _LOGGER.info("Found book '%s'", book.name)
                if self._dumb:
                    row = csv_parser.to_row(book)
                    self._writer.writerow(row)
                else:
                    self._manager.put(book)
            else:
                _LOGGER.warning("Couldn't parse book %s", fb2_src)

    def build_all_csvs(self):
        if not self._dumb:
            _LOGGER.debug("Rebuilding CSVs")
            self._manager.build_all_csvs()
            _LOGGER.info("CSVs rebuilt")

def parse_args():
    parser = argparse.ArgumentParser(description=\
        i18n.translate('BOOKDESC_SHORTDESCRIPTION'))
    parser.add_argument('-I', '--info', action = "store_true",
        help=i18n.translate('Display program infomration (long)'))
    parser.add_argument('out', metavar='OUT', type=str, nargs=1,
        help=i18n.translate('an output file or folder to put CSVs to'))
    parser.add_argument('inputs', metavar='INPUT', type=str, nargs='+',
        help=i18n.translate('an input (file or folder) to parse .fb2 from'))
    parser.add_argument('-d', '--dumb', action = "store_true",
        help=i18n.translate('dumb mode'))
    parser.add_argument('-b', '--backend', type=str, 
        choices = keyvalue.backends(), 
        default = keyvalue.DEFAULT_BACKEND,
        help=i18n.translate('dedup backend (default:') + ' ' + \
            keyvalue.DEFAULT_BACKEND + ")")
    parser.add_argument('-W', '--Werror', action = "store_true", dest="werror",
        help=i18n.translate('COWARD_MODE'))
    parser.add_argument('-l', '--log-level', type=str, default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], 
        help=i18n.translate('logging level'))
    parser.add_argument('-V', '--version', action = "store_true",
        help=i18n.translate('display version and exit'))
    return parser.parse_args()
    

def main():
    if ("-V" in sys.argv or "--version" in sys.argv):
        print("v" + str(VERSION))
        return
    if ("-I" in sys.argv) or ("--info" in sys.argv):
        print(i18n.translate("BOOKDESC_INFO"))
        return
    args = parse_args()
    if args.dumb and os.path.exists(args.out[0]):
        print(args.out[0], " ", 
            i18n.translate("DUMB_MODE_FILE_MUST_NOT_EXIST"), 
            file = sys.stderr)
        return
    log.config(werror=args.werror, log_level=args.log_level)
    backend_func = lambda path: keyvalue.open(path, backend=args.backend)
    if args.backend and args.dumb:
        _LOGGER.warning("--backend ignored for dumb mode")
    with BookDesc(args.out[0], args.dumb, idx_backend=backend_func) as desc:
        desc.parse_inputs(*args.inputs)
        desc.build_all_csvs()

if __name__ == '__main__':
    main()

