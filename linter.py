import sublime

from SublimeLinter.lint import Linter
from SublimeLinter.lint.linter import LintMatch


# https://www.gnu.org/software/make/manual/html_node/Special-Variables.html
SPECIAL_VARS = {
    "MAKE",
    "MAKEFILE_LIST",
}


def global_vars(view):
    # the `VARIABLE`s declared in the global namespace
    regions = view.find_by_selector("variable.other.makefile")
    return set([view.substr(x) for x in regions])


def functions(view):
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


class Makefile(Linter):
    cmd = None
    regex = "stub"
    defaults = {"selector": "source.makefile"}

    def run(self, _cmd, _code):
        return "stub"  # just to trigger find_errors()

    def find_errors(self, _output):
        def add(pos, msg, type="error"):
            lineno, col, end_col = pos
            lm = LintMatch(
                filename=view.file_name(),
                line=lineno,
                col=col,
                end_col=end_col,
                message=msg,
                error_type=type
            )
            matches.append(lm)

        view = sublime.active_window().active_view()
        matches = []

        # find all undefined names (e.g. undefined `$(FOO)`)
        gvars = global_vars(view)
        for region in referenced_vars(view):
            name = view.substr(region)
            if name not in gvars and name not in SPECIAL_VARS:
                pos = region_position(view, region)
                add(pos, "undefined name `%s`" % name)

        return matches
