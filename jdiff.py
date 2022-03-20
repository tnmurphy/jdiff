#!/usr/bin/env python3
""" jdiff is a program for finding the difference between 2 json structures. 

The MIT License (MIT)
Copyright (c) 2021 Timothy Norman Murphy <tnmurphy@gmail.com>
Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions: The
above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.  THE SOFTWARE IS PROVIDED
"AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

It's not perfect!  It detects differences between maps/dictionaries but
not between lists.  e.g. if the top level items to compare are [ 1, 2,
3 ] and [ 1, 2, 5 ] then it will see that they are not equal but not be
able to show that 3 should be removed and 5 added to - i.e. it cannot
gernerate diffs on lists.

Additionally this diff is only for viewing - there's no mechanism for 
"applying it" and because the format is somewhat unstable
"""

import sys,os
import json
import re
from collections import deque


class DiffOps:
    """ diff operations """
    def __init__(self, indent):
        self.indent = indent
        self.ops = deque()

    def __len__(self):
        return len(self.ops)

    def op_l2r(self, key, value):
        self.ops.append(('<', self.indent, key, value))

    def op_r2l(self, key, value):
        self.ops.append(('>', self.indent, key, value))

    def add_sub_ops(self, key: str, subops: deque()):
        self.ops.append(('D', self.indent, key, subops.ops))

    @staticmethod
    def ops_to_file(f, ops):

        for op, indent, key, value in ops:
            # Only show a label and the diff if there really is a diff
            path_indent=" " * indent
            if op == "<" or op == ">":
                f.write(f"{op} {path_indent}{key}: {value}\n")
            elif op == "D":
                f.write(f"{op} {path_indent}{key}:\n")
                DiffOps.ops_to_file(f, value)
                
    def to_file(self, f):
        self.ops_to_file(f, self.ops)


def dict_diff(jsona: dict, jsonb: dict, indent: int = 0) -> DiffOps:
    """ recursively find differences between two dictionaries"""
    a_keys = set(jsona.keys())
    b_keys = set(jsonb.keys())

    diffops = DiffOps(indent) 
    a_diff_keys = sorted(a_keys.difference(b_keys))
    if len(a_diff_keys) > 0:
        for k in a_diff_keys:
            diffops.op_l2r(k, jsona[k])

    b_diff_keys = sorted(b_keys.difference(a_keys))
    if len(b_diff_keys) > 0:
        for k in b_diff_keys:
            diffops.op_r2l(k, jsonb[k])


    intersection_keys = sorted(a_keys.intersection(b_keys))
    for k in intersection_keys:
        t = type(jsona[k])
        if isinstance(jsona[k], dict):
            subops = dict_diff(jsona[k], jsonb[k], indent+4)
            if len(subops) > 0:
                diffops.add_sub_ops(k, subops)

        elif jsona[k] != jsonb[k]:
            diffops.op_l2r((k, jsona[k]))
            diffops.op_r2l((k, jsonb[k]))

    return diffops

    
def stdout_diff(jsona: dict, jsonb: dict):
    ops = dict_diff(jsona, jsonb)

    ops.to_file(sys.stdout)

def file_diff(files):
    """Diff json files - takes a list of filenames as the parameter"""

    json_items = []
    for f in files:
        with open(f, "r") as fa:
            try:
                json_items.append(json.load(fa))
            except json.decoder.JSONDecodeError as e:
                sys.stderr.write(f"Error processing {f}: {e}\n")
                sys.exit(1)

    for fileb in json_items[1:]:
        stdout_diff(json_items[0],fileb)

def line_diff():
    """Find first bit of json in one line, diff all successive ones to it"""
    jsre = re.compile(".*?({.*}).*?")
    js=[]
    jsona_s=None
    for l in sys.stdin:
        m = jsre.match(l)
        if m is not None:
            print(f"Groups={m.groups()}")
            if jsona_s is None:
                jsona_s = m.groups()[0]
            else:
                jsonb_s = m.groups()[0]

                jsona = json.loads(jsona_s)
                jsonb = json.loads(jsonb_s)
                stdout_diff(jsona, jsonb)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="compare files containing JSON")
    parser.add_argument("files", metavar="Files", nargs='*', 
             help="list of files to compare. Changes listed from the first file to each of the others")
    parser.add_argument("-l", action="store_true", 
             help="line mode - look for the first 2 complete json strings in the standard input and compare them")
    args = parser.parse_args()

    if args.l:
        line_diff()
    elif len(args.files) < 3:
        file_diff(args.files)
    else:
        sys.stderr.write("jdiff either needs 2 files or the -l option for line mode\n")
        sys.exit(1)

