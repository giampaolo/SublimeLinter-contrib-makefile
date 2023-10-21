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
