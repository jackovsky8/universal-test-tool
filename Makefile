.ONESHELL:
ENV_PREFIX=$(shell python3 -c "if __import__('pathlib').Path('.venv/bin/pip').exists(): print('.venv/bin/')")

.PHONY: help
help:             ## Show the help.
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@fgrep "##" Makefile | fgrep -v fgrep


.PHONY: show
show:             ## Show the current environment.
	@echo "Running using $(ENV_PREFIX)"
	@$(ENV_PREFIX)python3 -V
	@$(ENV_PREFIX)python3 -m site

.PHONY: install
install:          ## Install the project in dev mode.
	@echo "Don't forget to run 'make virtualenv' if you got errors."
	$(ENV_PREFIX)pip install -e .[test]

.PHONY: fmt
fmt:              ## Format code using black & isort.
	$(ENV_PREFIX)isort test_tool/
	$(ENV_PREFIX)black -l 79 test_tool/
	$(ENV_PREFIX)isort test_tool_assert_plugin/
	$(ENV_PREFIX)black -l 79 test_tool_assert_plugin/
	# $(ENV_PREFIX)isort test_tool_copy_files_ssh_plugin/
	# $(ENV_PREFIX)black -l 79 test_tool_copy_files_ssh_plugin/
	# $(ENV_PREFIX)isort test_tool_jdbc_sql_plugin/
	# $(ENV_PREFIX)black -l 79 test_tool_jdbc_sql_plugin/
	$(ENV_PREFIX)isort test_tool_python_plugin/
	$(ENV_PREFIX)black -l 79 test_tool_python_plugin/
	# $(ENV_PREFIX)isort test_tool_read_jar_manifest_plugin/
	# $(ENV_PREFIX)black -l 79 test_tool_read_jar_manifest_plugin/
	# $(ENV_PREFIX)isort test_tool_rest_plugin/
	# $(ENV_PREFIX)black -l 79 test_tool_rest_plugin/
	# $(ENV_PREFIX)isort test_tool_run_process_plugin/
	# $(ENV_PREFIX)black -l 79 test_tool_run_process_plugin/
	# $(ENV_PREFIX)isort test_tool_selenium_plugin/
	# $(ENV_PREFIX)black -l 79 test_tool_selenium_plugin/
	# $(ENV_PREFIX)isort test_tool_sql_plus_plugin/
	# $(ENV_PREFIX)black -l 79 test_tool_sql_plus_plugin/
	# $(ENV_PREFIX)isort test_tool_ssh_cmd_plugin/
	# $(ENV_PREFIX)black -l 79 test_tool_ssh_cmd_plugin/
	$(ENV_PREFIX)black -l 79 tests/

.PHONY: lint
lint:             ## Run pep8, black, mypy linters.
	$(ENV_PREFIX)flake8 test_tool/
	$(ENV_PREFIX)black -l 79 --check test_tool/
	$(ENV_PREFIX)flake8 test_tool_assert_plugin/
	$(ENV_PREFIX)black -l 79 --check test_tool_assert_plugin/
	# $(ENV_PREFIX)flake8 test_tool_copy_files_ssh_plugin/
	# $(ENV_PREFIX)black -l 79 --check test_tool_copy_files_ssh_plugin/
	# $(ENV_PREFIX)flake8 test_tool_jdbc_sql_plugin/
	# $(ENV_PREFIX)black -l 79 --check test_tool_jdbc_sql_plugin/
	$(ENV_PREFIX)flake8 test_tool_python_plugin/
	$(ENV_PREFIX)black -l 79 --check test_tool_python_plugin/
	# $(ENV_PREFIX)flake8 test_tool_read_jar_manifest_plugin/
	# $(ENV_PREFIX)black -l 79 --check test_tool_read_jar_manifest_plugin/
	# $(ENV_PREFIX)flake8 test_tool_rest_plugin/
	# $(ENV_PREFIX)black -l 79 --check test_tool_rest_plugin/
	# $(ENV_PREFIX)flake8 test_tool_run_process_plugin/
	# $(ENV_PREFIX)black -l 79 --check test_tool_run_process_plugin/
	# $(ENV_PREFIX)flake8 test_tool_selenium_plugin/
	# $(ENV_PREFIX)black -l 79 --check test_tool_selenium_plugin/
	# $(ENV_PREFIX)flake8 test_tool_sql_plus_plugin/
	# $(ENV_PREFIX)black -l 79 --check test_tool_sql_plus_plugin/
	# $(ENV_PREFIX)flake8 test_tool_ssh_cmd_plugin/
	# $(ENV_PREFIX)black -l 79 --check test_tool_ssh_cmd_plugin/
	$(ENV_PREFIX)black -l 79 --check tests/
	$(ENV_PREFIX)mypy --ignore-missing-imports test_tool/
	$(ENV_PREFIX)mypy --ignore-missing-imports test_tool_assert_plugin/
	# $(ENV_PREFIX)mypy --ignore-missing-imports test_tool_copy_files_ssh_plugin/
	# $(ENV_PREFIX)mypy --ignore-missing-imports test_tool_jdbc_sql_plugin/
	$(ENV_PREFIX)mypy --ignore-missing-imports test_tool_python_plugin/
	# $(ENV_PREFIX)mypy --ignore-missing-imports test_tool_read_jar_manifest_plugin/
	# $(ENV_PREFIX)mypy --ignore-missing-imports test_tool_rest_plugin/
	# $(ENV_PREFIX)mypy --ignore-missing-imports test_tool_run_process_plugin/
	# $(ENV_PREFIX)mypy --ignore-missing-imports test_tool_selenium_plugin/
	# $(ENV_PREFIX)mypy --ignore-missing-imports test_tool_sql_plus_plugin/
	# $(ENV_PREFIX)mypy --ignore-missing-imports test_tool_ssh_cmd_plugin/

.PHONY: lint
test: lint        ## Run tests and generate coverage report.
	$(ENV_PREFIX)pytest -v --cov-config .coveragerc --cov=test_tool -l --tb=short --maxfail=1 tests/
	$(ENV_PREFIX)coverage xml
	$(ENV_PREFIX)coverage html

.PHONY: watch
watch:            ## Run tests on every change.
	ls **/**.py | entr $(ENV_PREFIX)pytest -s -vvv -l --tb=long --maxfail=1 tests/

.PHONY: clean
clean:            ## Clean unused files.
	@find ./ -name '*.pyc' -exec rm -f {} \;
	@find ./ -name '__pycache__' -exec rm -rf {} \;
	@find ./ -name 'Thumbs.db' -exec rm -f {} \;
	@find ./ -name '*~' -exec rm -f {} \;
	@rm -rf .cache
	@rm -rf .pytest_cache
	@rm -rf .mypy_cache
	@rm -rf build
	@rm -rf dist
	@rm -rf *.egg-info
	@rm -rf htmlcov
	@rm -rf .tox/
	@rm -rf docs/_build

.PHONY: virtualenv
virtualenv:       ## Create a virtual environment.
	@echo "creating virtualenv ..."
	@rm -rf .venv
	@python3 -m venv .venv
	@./.venv/bin/pip install -U pip
	@./.venv/bin/pip install -e .[test]
	@echo
	@echo "!!! Please run 'source .venv/bin/activate' to enable the environment !!!"

.PHONY: release
release:          ## Create a new tag for release.
	@echo "WARNING: This operation will create s version tag and push to github"
	@read -p "Version? (provide the next x.y.z semver) : " TAG
	@echo "$${TAG}" > test_tool/VERSION
	@$(ENV_PREFIX)gitchangelog > HISTORY.md
	@git add test_tool/VERSION HISTORY.md
	@git commit -m "release: version $${TAG} 🚀"
	@echo "creating git tag : $${TAG}"
	@git tag $${TAG}
	@git push -u origin HEAD --tags
	@echo "Github Actions will detect the new tag and release the new version."

.PHONY: docs
docs:             ## Build the documentation.
	@echo "building documentation ..."
	@$(ENV_PREFIX)mkdocs build
	URL="site/index.html"; xdg-open $$URL || sensible-browser $$URL || x-www-browser $$URL || gnome-open $$URL || open $$URL

.PHONY: init
init:             ## Initialize the project based on an application template.
	@./.github/init.sh
