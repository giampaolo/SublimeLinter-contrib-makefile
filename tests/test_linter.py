import os
import sys
from unittesting import DeferrableTestCase

HERE = os.path.realpath(os.path.abspath(os.path.dirname(__file__)))
ROOT = os.path.realpath(os.path.join(HERE, ".."))
sys.path.append(ROOT)

from linter import Parser


class TestLinter(DeferrableTestCase):
    def test_it(self):
        1 / 0
        print(sys.path)
        print(sys.executable)
