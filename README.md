# universal-test-tool

![GitHub License](https://img.shields.io/github/license/jackovsky8/universal-test-tool)
[![codecov](https://codecov.io/gh/jackovsky8/universal-test-tool/branch/main/graph/badge.svg?token=universal-test-tool_token_here)](https://codecov.io/gh/jackovsky8/universal-test-tool)
[![CI](https://github.com/jackovsky8/universal-test-tool/actions/workflows/main.yml/badge.svg)](https://github.com/jackovsky8/universal-test-tool/actions/workflows/main.yml)
![PyPI - Version](https://img.shields.io/pypi/v/universal-test-tool)
![PyPI - Downloads](https://img.shields.io/pypi/dm/universal-test-tool)

Awesome universal-test-tool to make tests configurable with a yaml file.

## Install the repository

```bash
pip install universal-test-tool
```

## Run the tests

```bash
test-tool

# This programm is a tool for running tests.

# options:
#   -h, --help            show this help message and exit
#   -p PROJECT, --project PROJECT
#                         The path to the project.
#   -ca CALLS, --calls CALLS
#                         The filename of the calls configuration.
#   -d DATA, --data DATA  The filename of the data configuration.
#   -X, --debug           Activate debugging.
```

### Calls File

Per default a file `calls.yaml` is searched in the project folder, which is by default the current working directory.

It is a list where every entry is one step to test.

#### Available plugins

The tests are done in the following available plugins:

- [Assert (test_tool_assert_plugin)](docs/plugins/assert.md)
- [Copy Files SSH (test_tool_copy_files_ssh_plugin)](docs/plugins/copy_files_ssh.md)
- [jdbc SQL (test_tool_jdbc_sql_plugin)](docs/plugins/jdbc_sql.md)
- [Python (test_tool_python_plugin)](docs/plugins/python.md)
- [Read Jar Manifest (test_tool_read_jar_manifest_plugin)](docs/plugins/read_jar_manifest.md)
- [Rest (test_tool_rest_plugin)](docs/plugins/rest.md)
- [Run Process (test_tool_run_process_plugin)](docs/plugins/run_process.md)
- [Selenium (test_tool_selenium_plugin)](docs/plugins/selenium.md)
- [SQL Plus (test_tool_sql_plus_plugin)](docs/plugins/sql_plus.md)
- [SSH Cmd (test_tool_ssh_cmd_plugin)](docs/plugins/ssh_cmd.md)

#### Not officially supported plugins

[Read here](docs/plugins/other.md)

## Development

Read the [CONTRIBUTING.md](CONTRIBUTING.md) file.
