# Shortcuts for various repetitive tasks (UNIX only)

PYTHON = python3

test:  ## Run tests. Requires UnitTesting module.
	subl tests/test_linter.py
	subl --command unit_testing_current_file

black:  ## Run black linter.
	@git ls-files '*.py' | xargs $(PYTHON) -m black --config=pyproject.toml --check --safe

fix-black:  ## Fix black warnings.
	git ls-files '*.py' | xargs $(PYTHON) -m black --config=pyproject.toml

git-tag-release:  ## Git-tag a new release.
	$(eval VER := $(shell grep -oP '^__version__ = "\K[^"]+' linter.py))
	git tag -a $(VER) -m `git rev-list HEAD --count`:`git rev-parse --short HEAD`
	git push --follow-tags

help: ## Display callable targets.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
