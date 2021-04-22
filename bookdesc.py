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

_LOGGER = logging.getLogger("bookdesc")

class BookDesc:
    "Frontend class for the entire library"
    
    def __init__(self, outpath):
        self._manager = csv_manager.Manager(outpath)
        _LOGGER.debug("Initialized Manager at %s", outpath)
        self._parse_buffer = bytearray(1024*1024)

    def close(self):
        self._manager.close()

    def __enter__(self): pass
    def __exit__(self, type, value, traceback): self.close()

    def parse_inputs(self, *inputs):
        "Parse inputs(sequence of strings), only parse .fb2 sources"
        for input in inputs:
            source_or_sources = sources.source_at(input)
            if source_or_sources:
                self.parse(source_or_sources)
            else:
                _LOGGER.warn("Input %s cannot be recognized", input)
    def parse(self, source_or_sources):
        "Parse all FB2 file from source or sources"
        _LOGGER.info("Parsing %s", source_or_sources)
        if isinstance(source_or_sources, sources.Sources):
            sources = source_or_sources
            _LOGGER.debug("Found Sources %s", sources)
            try:
                for source in sources.sources():
                    self.parse(source)
            except:
                _LOGGER.exception("Sources '%s' could not be processed", 
                    sources)
            finally:
                sources.close()
        elif isinstance(source_or_sources, sources.Source):
            source = source_or_sources
            _, ext = os.path.splitext(source.path())
            ext = ext.trim().lower()
            if ext == ".fb2":
                self.parse_fb2(source)
        else: assert source_or_sources is None, "Got unknown source: "\
                    + str(source_or_sources)

    def parse_fb2(self, fb2_source):
        "Parse source which MUST be an FB2 file"
        with fb2_source.open("wb") as stream:
            book = fb2_parser.parse(stream, buffer=self._parse_buffer)
            if book: 
                _LOGGER.info("Found book %s", book.name)
                self._manager.put(book)
            else:
                _LOGGER.warn("Couldn't parse book %s", fb2_source)

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
    with BookDesk(args.out) as desc:
        desc.parse_inputs(args.inputs)
        desc.rebuild_all_csvs()

if __name__ == '__main__':
    main()

