import re

import sublime

from SublimeLinter.lint import Linter
from SublimeLinter.lint.linter import LintMatch


# https://www.gnu.org/software/make/manual/html_node/Special-Variables.html
SPECIAL_VARS = {
    "MAKE",
    "MAKEFILE_LIST",
}

REGEX_FUN_CALL = re.compile(
    r"""
    ^\t\$[{|\(]\s*  # open parenthesis
    MAKE
    \s*[}|\)]  # close parenthesis
    \s+
    ([A-Za-z0-9_\-]+)
    """,
    re.VERBOSE,
)


def global_vars(view):
    # the `VARIABLE`s declared in the global namespace
    regions = view.find_by_selector("variable.other.makefile")
    return set([view.substr(x) for x in regions])


def function_names(view):
    # the functions / targets
    regions = view.find_by_selector("entity.name.function")
    return set([view.substr(x) for x in regions])


def referenced_vars(view):
    regions = view.find_by_selector("variable.parameter.makefile")
    return regions


def region_position(view, region):
    x, y = view.rowcol(region.begin())
    z = y + (region.end() - region.begin())
    return (x, y, z)


def readlines(view):
    region = sublime.Region(0, view.size())
    return [view.substr(x) for x in view.lines(region)]



class Parser:
    def __init__(self):
        self.view = sublime.active_window().active_view()
        self.matches = []

    def run(self):
        self.find_undefined_names()
        self.find_undefined_fun_calls()
        return self.matches

    def add(self, pos, msg, type="error"):
        lineno, col, end_col = pos
        lm = LintMatch(
            filename=self.view.file_name(),
            line=lineno,
            col=col,
            end_col=end_col,
            message=msg,
            error_type=type
        )
        self.matches.append(lm)

    def find_undefined_names(self):
        # Find all undefined names, e.g. FOO does not exist:
        #
        # some-target:
        #     echo $(FOO)
        view = self.view
        gvars = global_vars(view)
        for region in referenced_vars(view):
            name = view.substr(region)
            if name not in gvars and name not in SPECIAL_VARS:
                pos = region_position(view, region)
                self.add(pos, "undefined name `%s`" % name)

    def find_undefined_fun_calls(self):
        # Find all undefined names, e.g. unknown-target does not exist):
        #
        # some-target:
        #     ${MAKE} unknown-target
        fnames = function_names(self.view)
        for idx, line in enumerate(readlines(self.view)):
            m = re.match(REGEX_FUN_CALL, line)
            if m:
                fun_name = m.group(1)
                if fun_name not in fnames:
                    pos = idx, 1, len(line)
                    self.add(pos, "undefined target `%s`" % fun_name)




class Makefile(Linter):
    cmd = None
    regex = "stub"
    defaults = {"selector": "source.makefile"}

    def run(self, _cmd, _code):
        return "stub"  # just to trigger find_errors()

    def find_errors(self, _output):
        return Parser().run()
