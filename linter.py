import os
import re

import sublime

if "GITHUB_ACTIONS" not in os.environ:
    from SublimeLinter.lint import Linter
    from SublimeLinter.lint.linter import LintMatch
else:

    class LintMatch(dict):
        pass

    class Linter:
        pass


__version__ = "0.1.2"

# https://www.gnu.org/software/make/manual/html_node/Special-Variables.html
SPECIAL_VARS = {
    ".DEFAULT_GOAL",
    ".EXTRA_PREREQS",
    ".FEATURES",
    ".INCLUDE_DIRS",
    ".RECIPEPREFIX",
    ".VARIABLES",
    "MAKE",
    "MAKE_RESTARTS",
    "MAKE_TERMERR",
    "MAKE_TERMOUT",
    "MAKEFILE_LIST",
}

# e.g.:
# `${MAKE} flake8`
# `$(MAKE) flake8`
# `$(MAKE) -C flake8`
REGEX_TARGET_CALL = re.compile(
    r"""
    ^\t\$[{|\(]\s*  # open parenthesis
    MAKE
    \s*[}|\)]  # close parenthesis
    \s+
    # ignore optional args
    (?:-[a-zA-Z]\s+  # -c, -C
      |--[a-z-]+\s+  # --keep, --keep-going
      |--[a-z-]+=.*?\s+  # --jobs=3
    )*
    ([_A-Za-z0-9][A-Za-z0-9_-]+)  # target name
    """,
    re.VERBOSE,
)

REGEX_PHONY_NAMES = r"\.PHONY:\s*([^\n]+)"


def global_var_names(view):
    # the `VARIABLE`s declared in the global namespace
    regions = view.find_by_selector("variable.other.makefile")
    # strip() of tabs and/or spaces is necessary in case VAR is
    # indented inside an ifeq clause or something
    return set([view.substr(x).strip() for x in regions])


def target_names(view):
    # the function / target names
    regions = view.find_by_selector("entity.name.function")
    return set([view.substr(x) for x in regions if view.substr(x) != ".PHONY"])


def phony_names(text):
    names = set()
    for bits in re.findall(REGEX_PHONY_NAMES, text):
        names.update(bits.split())
    return names


def referenced_vars(view):
    regions = view.find_by_selector("variable.parameter.makefile")
    return [x for x in regions if view.substr(x) != "${*}"]


def region_position(view, region):
    x, y = view.rowcol(region.begin())
    z = y + (region.end() - region.begin())
    return (x, y, z)


class Parser:
    __slots__ = ("view", "matches", "text", "lines")

    def __init__(self, view):
        self.view = view
        self.matches = []
        self.text = None
        self.lines = None

    def run(self):
        if self.view.match_selector(0, "source.makefile"):
            self.text = self.view.substr(sublime.Region(0, self.view.size()))
            self.lines = self.text.splitlines()
            self.find_undefined_vars()
            self.find_undefined_target_calls()
            self.find_spaces()
            self.find_missing_phony()
            self.find_duplicate_targets()
            self.find_trailing_spaces()
            self.find_empty_lines_at_eof()
        return self.matches

    def add(self, pos, msg, type="error"):
        lineno, col, end_col = pos
        lm = LintMatch(
            filename=self.view.file_name(),
            line=lineno,
            col=col,
            end_col=end_col,
            message=msg,
            error_type=type,
        )
        self.matches.append(lm)

    def find_undefined_vars(self):
        """All undefined names, e.g. `FOO` does not exist:

        test:
            echo $(FOO)
        """
        view = self.view
        gvars = global_var_names(view)
        for region in referenced_vars(view):
            name = view.substr(region)
            if name not in gvars and name not in SPECIAL_VARS:
                pos = region_position(view, region)
                self.add(pos, "undefined name `%s`" % name)

    def find_undefined_target_calls(self):
        """All undefined target (function) calls, e.g., `bar` does not
        exist:

        test:
            ${MAKE} bar
        """
        fnames = target_names(self.view)
        for lineno, line in enumerate(self.lines):
            m = re.match(REGEX_TARGET_CALL, line)
            if m:
                target_name = m.group(1)
                if target_name not in fnames:
                    start, end = m.span(1)
                    pos = lineno, start, end
                    self.add(pos, "undefined target `%s`" % target_name)

    def find_spaces(self):
        """Targets body which are indented with spaces instead of tabs.
        This is considered a syntax error and make will crash."""
        for idx, line in enumerate(self.lines):
            if line.startswith(" "):
                leading_spaces = len(line) - len(line.lstrip())
                pos = idx, 0, leading_spaces
                self.add(pos, "line should start with tab, not space")

    def find_missing_phony(self):
        """E.g., something like this + there's a directory 'tests' in
        the same dir as the Makefile, so it requires `.PHONY: tests` on
        top.

        tests:
            pytest
        """
        view = self.view
        fnames = set(os.listdir(os.path.dirname(view.file_name())))
        phonys = phony_names(self.text)
        for region in view.find_by_selector("entity.name.function"):
            tname = view.substr(region)
            if tname in fnames:
                if tname not in phonys:
                    pos = region_position(view, region)
                    self.add(pos, "missing .PHONY declaration")

    def find_duplicate_targets(self):
        """Duplicated target names, e.g.

        tests:
            pytest

        tests:
            pytest
        """
        view = self.view
        collected = set()
        for region in view.find_by_selector("entity.name.function"):
            name = view.substr(region)
            if name in collected:
                pos = region_position(view, region)
                self.add(pos, "a target with the same name already exists")
            collected.add(name)

    def find_trailing_spaces(self):
        for lineno, line in enumerate(self.lines):
            if line.endswith(" "):
                start = len(line.rstrip(" "))
                end = len(line)
                pos = lineno, start, end
                self.add(pos, "trailing spaces")

    def find_empty_lines_at_eof(self):
        blanks = 0
        for line in self.lines[::-1]:
            if not line.strip():
                blanks += 1
            else:
                break
        if blanks:
            for lineno in range(len(self.lines), len(self.lines) + blanks):
                pos = lineno - 2, 1, 1
                self.add(pos, "unnecessary empty line at EOF")


class Makefile(Linter):
    cmd = None
    regex = "stub"
    defaults = {"selector": "source.makefile"}

    def run(self, _cmd, _code):
        return "stub"  # just to trigger find_errors()

    def find_errors(self, _output):
        return Parser(self.view).run()
