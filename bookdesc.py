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

    def generate(self, inputs, output):
        "Parse inputs(generator of strings), generate CSVs to output"
        pass
