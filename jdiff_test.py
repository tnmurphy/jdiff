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
        diff.to_file(sys.stdout)
        self.assertEqual(len(diff), 1)
        self.assertEqual(diff.ops, deque([('>', 0, 'two', 2)]))


if __name__ == '__main__':
    unittest.main()
