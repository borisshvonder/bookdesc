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

class BookDesc:
    "Frontend class for the entire library, also has main() method"
    
    def __init__(self): pass

    def parse_inputs(self, inputs, outpath):
        "Parse inputs(sequence of strings), generate CSVs to output folder"
        with self.new_output_cache(outpath) as cache:
            for input in inputs:
                with self.open_input(input) as sources:
                    for file_source in sources:
                        self.parse_input(cache, file_source)

    def new_output_cache(self, outpath):
        "Create new instance of the output cache"

    def open_input(self, input_path):
        """Take input path and return a sequence of FileSources in that path.
           Single file, folder with subfolders, .zip files are supported"""

    def parse_input(self, output_cache, file_source):
        "Parse single FileSource and put it to output_cache"

class FileSources:
    "A sequence of FileSource's that MUST be closed once it is no longer used"

    def __enter__(self): pass

    def __exit__(self, type, value, traceback): pass

class FileSource:
    "Represents single file which contains a Book"

    def path(self):
        "Returns a path at which this file is located (might be inside .zip)"

    def open(self):
        "Open file and return raw bytes"
