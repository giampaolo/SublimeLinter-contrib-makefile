[![tests](https://github.com/giampaolo/SublimeLinter-makefile/actions/workflows/tests.yml/badge.svg)](https://github.com/giampaolo/SublimeLinter-makefile/actions/workflows/tests.yml)

About
-----

A plugin for [SublimeLinter](https://github.com/SublimeLinter/SublimeLinter)
which provides linting for Makefiles.

## Installation

Use [Package Control](https://packagecontrol.io/installation): search for a
package named `SublimeLinter-contrib-makefile` and install it.
SublimeLinter must also be installed.

Checkers
--------

This plugin is able to detect the following mistakes. They will be visually
signaled in the status bar and the left gutter.

#### Undefined global variable names

Correct:

```makefile
FOO = 1

test:
    echo $(FOO)
```

Incorrect:

```makefile
test:
    echo $(FOO)
```

#### Undefined target names

Correct:

```makefile
clean:
    rm -rf build/*

test:
    ${MAKE} clean
    pytest .

```

Incorrect:

```makefile
test:
    ${MAKE} clean
    pytest .
```

#### Duplicated targets

When there's 2 targets with the same name, e.g.:

```makefile
test:
    pytest .

test:
    pytest .
```

#### Use of spaces instead of tabs

Any line starting with a space instead of tab is considered an error, e.g.

```makefile
test1:
    pytest .  # use tab

test2:
  pytest .  # use spaces
````

#### Missing `.PHONY` directive

This will print `missing .PHONY declaration` if there's a file or directory
named "test" in the same directory as the Makefile:

```makefile
test:
    pytest .
```

Motivations
-----------

#### Why not use an existing CLI tool?

As stated in https://github.com/SublimeLinter/package_control_channel/pull/134,
the motivation which led me to write this plugin is because the only Makefile
linter I found is https://github.com/mrtazz/checkmake, which provides a quite
limited set of rules:

```
$ go run github.com/mrtazz/checkmake/cmd/checkmake@latest --list-rules

        NAME                   DESCRIPTION

  maxbodylength       Target bodies should be kept
                      simple and short.
  minphony            Minimum required phony targets
                      must be present
  phonydeclared       Every target without a body
                      needs to be marked PHONY
  timestampexpanded   timestamp variables should be
                      simply expanded
```

I wanted a linter which was able to identify at least undefined variable names,
undefined target names, and the use of spaces instead of tabs. I found none so
I wrote my own.

#### Why not turn this into a generic CLI tool?

Indeed that probably makes a lot more sense. I may (or may not) do this later.
:)
