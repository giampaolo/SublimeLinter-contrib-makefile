[![tests](https://github.com/giampaolo/SublimeLinter-makefile/actions/workflows/tests.yml/badge.svg)](https://github.com/giampaolo/SublimeLinter-makefile/actions/workflows/tests.yml)

About
-----

A plugin for [SublimeLinter](https://github.com/SublimeLinter/SublimeLinter)
which provides linting for Makefiles.

Checkers
--------

This plugin is able to detect the following error conditions:

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
