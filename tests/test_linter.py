import shutil
import textwrap
import os
import sys

import sublime
from unittesting import DeferrableTestCase

HERE = os.path.realpath(os.path.abspath(os.path.dirname(__file__)))
ROOT = os.path.realpath(os.path.join(HERE, ".."))
TEST_FILE = "/tmp/SublimeLinter-makefile-test/Makefile"
sys.path.append(ROOT)

from linter import Parser  # noqa
from linter import target_names  # noqa
from linter import global_vars  # noqa
from linter import phony_names  # noqa
from linter import referenced_vars  # noqa


class TestCase(DeferrableTestCase):
    def setUp(self):
        super().setUp()
        os.makedirs(os.path.dirname(TEST_FILE), exist_ok=True)

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(os.path.dirname(TEST_FILE))

    def write_makefile(self, content):
        content = textwrap.dedent(content)
        with open(TEST_FILE, "w") as f:
            f.write(content)
        view = yield from self.await_open_file(TEST_FILE)
        return view

    def await_focus_view(self, view):
        view.window.focus_view(view)
        yield lambda: view.window.active_view() == view

    def await_content_in_view(self, view, content):
        yield lambda: view.substr(sublime.Region(0, view.size())) == content

    def _await_view_ready(self, view, content=""):
        yield lambda: not view.is_loading()
        yield lambda: self.await_focus_view(view)
        if content:
            yield from self.await_content_in_view(view, content)

    def await_open_file(self, path, window=None, flags=0):
        window = window or sublime.active_window()
        with open(path) as f:
            content = f.read()
        view = window.open_file(path, flags=flags)
        self.addCleanup(self.await_close_view, view)
        yield from self._await_view_ready(view, content)
        return view

    def await_close_view(self, view):
        window = view.window()
        view.set_scratch(True)
        yield lambda: view.close() is False


class TestUtils(TestCase):
    def test_target_names(self):
        view = yield from self.write_makefile(
            """
            hello1:
            \techo 1

            hello_1:
            \techo 1

            _hello1:
            \techo 1

            _hello-1:
            \techo 1

            1hello:  # valid
            \techo 1
            """
        )
        self.assertEqual(
            target_names(view),
            {"hello1", "hello_1", "_hello1", "_hello-1", "1hello"},
        )

    def test_global_vars(self):
        view = yield from self.write_makefile(
            """
            FOO = 1
            BAR = 1
            """
        )
        self.assertEqual(global_vars(view), {"FOO", "BAR"})

    def test_phony_names(self):
        view = yield from self.write_makefile(
            """
            .PHONY: hello1
            hello1:
            \techo 1

            hello_1:
            \techo 1

            .PHONY: _hello1
            _hello1:
            \techo 1
            """
        )
        self.assertEqual(phony_names(view), {"hello1", "_hello1"})

    def test_referenced_vars(self):
        view = yield from self.write_makefile(
            """
            .PHONY: hello1
            hello1:
            \techo $(FOO)
            \techo ${BAR}
            """
        )
        self.assertEqual(
            {view.substr(x) for x in referenced_vars(view)}, {"FOO", "BAR"}
        )


class TestParser(TestCase):
    def test_undefined_name(self):
        view = yield from self.write_makefile(
            """
            hello:
            \techo $(FOO)
            """
        )

        p = Parser(view)
        p.run()
        self.assertEqual(len(p.matches), 1)
        d = dict(p.matches[0])
        self.assertEqual(d["message"], "undefined name `FOO`")
        self.assertEqual(d["line"], 2)
        self.assertEqual(d["col"], 8)

    def test_undefined_fun_call(self):
        view = yield from self.write_makefile(
            """
            fix-all:
            \t${MAKE} fix-black
            """
        )

        p = Parser(view)
        p.run()
        self.assertEqual(len(p.matches), 1)
        d = dict(p.matches[0])
        self.assertEqual(d["message"], "undefined target `fix-black`")

    def test_space(self):
        view = yield from self.write_makefile(
            """
            fix-all:
                echo 1
            """
        )

        p = Parser(view)
        p.run()
        self.assertEqual(len(p.matches), 1)
        d = dict(p.matches[0])
        self.assertEqual(d["message"], "line should start with tab, not space")

    def test_phony(self):
        os.mkdir(os.path.join(os.path.dirname(TEST_FILE), "dirname"))
        view = yield from self.write_makefile(
            """
            dirname:
            \techo 1
            """
        )

        p = Parser(view)
        p.run()
        self.assertEqual(len(p.matches), 1)
        d = dict(p.matches[0])
        self.assertEqual(d["message"], "missing .PHONY declaration")

    def test_duplicated_target(self):
        view = yield from self.write_makefile(
            """
            test:
            \techo 1

            test:
            \techo 1
            """
        )

        p = Parser(view)
        p.run()
        self.assertEqual(len(p.matches), 1)
        d = dict(p.matches[0])
        self.assertEqual(
            d["message"], "a target with the same name already exists"
        )
