PYTHON = python3
ARGS =

test:
	subl tests/test_linter.py
	subl --command unit_testing_current_file

black:  ## Run black linter.
	@git ls-files '*.py' | xargs $(PYTHON) -m black --config=pyproject.toml --check --safe

fix-black:
	git ls-files '*.py' | xargs $(PYTHON) -m black --config=pyproject.toml

help: ## Display callable targets.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
