*(issue tracker at:
https://github.com/giampaolo/SublimeLinter-contrib-makefile/issues/)*

0.1.3 (unreleased)
------------------

* `.PHONY` was erroneously considered a target name.

0.1.2
-----

* readlines() algorithm is faster
* #3: recognize unnecessary empty lines at EOF.
* #2: recognize trailing spaces at the end of each line.
* #1: constants were not recognized if start with a tab as in:

```
ifneq (,$(shell command -v python3.8 2> /dev/null))
  PYTHON=python3.8
else
  PYTHON=python3
endif
```

0.1.1
-----

* when recognizing unknown target names, highlight the specific name instead of
  the whole line.
* recognize `make` command line args, e.g. `$(make) -k --keep foo` will be an
  error if 'foo' does not exist.

0.1.0
-----

* First release including:
  * undefined vars
  * undefined targets
  * duplicated targets
  * spaces instead of tabs
  * missing .PHONY directive
* PR for SublimeLinter inclusion:
  https://github.com/SublimeLinter/package_control_channel/pull/134
