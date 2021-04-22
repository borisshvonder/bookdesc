#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Book descriptions CSV generator.

h1. History and Why
This is a continuation on jabot project https://github.com/borisshvonder/jabot.
I have no time to properly support the project and it does not seem to be easy
for new developers to pick up since the project was primarilly written as
retrospecive on what I have learned in a few previous years. It was not built
for people to pick up easilly since it contains some uncommon features which
might not be easy to grasp. It also wasn't easy to operate since it required
Apache Solr and running retroshare node.

The bookdesc project, on the other hand, is supposed to be much simplier, 
easilly understood and operate. Thus:

* Python was chosen as the implementation language.
* bookdesc will NOT generate fulltext index.
* In fact, bookdesc will not have any indexing support whatsoever.
* Instead, it will simply generate CSV file which will contain books metadata
  (book name, ISBN, authors AND SHA1/MD5 book checksums).
* There will be no extra dependencies required whatsoever.

h1. Goals
* Ability to parse fb2 files directly or inside .zip archives.
* Incremental collection (should not scan already scanned files).
* Ability to split CSV files into sizeable chunks (perhaps, by author first 
  letter).
* It should be possible to use the bookdesc module as a library in other
  python projects.
* Simple to support code, minimal number of dependencies

h1. Non-goals
* No fulltext seach.
* In fact, no search at all.
* No import from existing databases and/or CSVs.
"""

import csv_manager
import sources
import logging
import fb2_parser
import argparse
import os.path

_LOGGER = logging.getLogger("bookdesc")

class BookDesc:
    "Frontend class for the entire library"
    
    def __init__(self, outpath):
        self._manager = csv_manager.Manager(outpath)
        _LOGGER.debug("Initialized Manager at %s", outpath)
        self._parse_buffer = bytearray(1024*1024)

    def close(self):
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
        _LOGGER.info("Parsing %s", src_or_srcs)
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
        with fb2_src.open("rb") as stream:
            book = None
            try:
                book = fb2_parser.parse(stream, buffer=self._parse_buffer)
            except:
                _LOGGER.exception("FB2 '%s' could not be parsed", fb2_src)
                book = None
            if book: 
                _LOGGER.info("Found book '%s'", book.name)
                self._manager.put(book)
            else:
                _LOGGER.warning("Couldn't parse book %s", fb2_src)

    def build_all_csvs(self):
        _LOGGER.debug("Rebuilding CSVs")
        self._manager.build_all_csvs()
        _LOGGER.info("CSVs rebuilt")

def main():
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser(description='Parse .fb2 files into CSVs')
    parser.add_argument('out', metavar='OUT', type=str, nargs=1,
                        help='an output file to put CSVs to')
    parser.add_argument('inputs', metavar='INPUT', type=str, nargs='+',
                        help='An input (file or folder) to parse .fb2 from')
    args = parser.parse_args()
    with BookDesc(args.out[0]) as desc:
        desc.parse_inputs(*args.inputs)
        desc.build_all_csvs()

if __name__ == '__main__':
    main()

