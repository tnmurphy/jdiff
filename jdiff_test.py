import unittest
import jdiff as jd
import sys

from collections import deque



diff = {"<": ["blah", "mah"], ">": {"blah": [1,2,3], "gah": {"dah": 2}}}

class TestZeroDepthDicts(unittest.TestCase):

    def test_base(self):
        jsona = {"one": 1}
        jsonb = {"one": 1, "two": 2}


        diff = jd.dict_diff(jsona, jsonb)
        sys.stdout.write("\n")
        diff.to_file(sys.stdout)
        sys.stdout.write("\n")
        self.assertEqual(len(diff), 1)
        self.assertEqual(diff.ops, deque([('>', 0, 'two', 2)]))

    def test_base_2(self):
        jsona = {"one": 1}
        jsonb = {"one": 1, "two": 2, "three": 3}


        diff = jd.dict_diff(jsona, jsonb)
        sys.stdout.write("\n")
        diff.to_file(sys.stdout)
        self.assertEqual(len(diff), 2)
        self.assertEqual(diff.ops, deque([
            ('>', 0, 'three', 3),
            ('>', 0, 'two', 2)
            ]))

    def test_subops_1(self):
        jsona = {"one": 1}
        jsonb = {"one": 1, "two": 2, "three": { "four": 4}}


        diff = jd.dict_diff(jsona, jsonb)
        sys.stdout.write("\n")
        diff.to_file(sys.stdout)
        self.assertEqual(len(diff), 2)
        self.assertEqual(diff.ops, deque([
            ('>', 0, 'three', {'four': 4}), 
            ('>', 0, 'two', 2)
            ]))

    def test_subops_1(self):
        jsona = {"one": 1, "two": 2, "three": { "four": 4}}
        jsonb = {"one": 1, "two": 2, "three": { "four": 4, "five": 5}}


        diff = jd.dict_diff(jsona, jsonb)
        sys.stdout.write("\n")
        diff.to_file(sys.stdout)
        self.assertEqual(diff.ops, deque([
            ('D', 0, 'three', deque([('>', 4, 'five',  5)])), 
            ]))


    def test_subtree_to_scalar(self):
        jsona = {"one": 1, "two": 2, "three": { "four": 4}}
        jsonb = {"one": 1, "two": 2, "three": 5}


        diff = jd.dict_diff(jsona, jsonb)
        sys.stdout.write("\n")
        diff.to_file(sys.stdout)
        self.assertEqual(diff.ops, deque([
            ('<', 0, 'three', {'four': 4}), ('>', 0, 'three', 5)
            ]))

    def test_scalar_to_subtreer(self):
        jsona = {"one": 1, "two": 2, "three": 5}
        jsonb = {"one": 1, "two": 2, "three": { "four": 4}}


        diff = jd.dict_diff(jsona, jsonb)
        sys.stdout.write("\n")
        diff.to_file(sys.stdout)
        self.assertEqual(diff.ops, deque([
            ('<', 0, 'three', 5), 
            ('>', 0, 'three', {'four': 4})
            ]))

if __name__ == '__main__':
    unittest.main()
