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
Per default a file ```calls.yaml``` is searched in the project folder, which is by default the current working directory.

It is a list where every entry is one step to test.

The tests are done in the following available plugins:
- Assert (test_tool_assert_plugin)
- Copy Files SSH (test_tool_copy_files_ssh_plugin)
- JDBC SQL (test_tool_jdbc_sql_plugin)
- Python (test_tool_python_plugin)
- Read Jar Manifest (test_tool_read_jar_manifest_plugin)
- Rest (test_tool_rest_plugin)
- Run Process (test_tool_run_process_plugin)
- Selenium (test_tool_selenium_plugin)
- SQL Plus (test_tool_sql_plus_plugin)
- SSH Cmd (test_tool_ssh_cmd_plugin)

#### Assert (test_tool_assert_plugin)
Make an assertion.

##### Call:
```yaml
- type: ASSERT
    call:
        value: None
        expected: None
        operator: ==
        error_msg: The value is not as expected.
```

##### Parameters:
| Parameter | Default | Description |
|:---------:|:--------:|:--------:|
|   value   |   None   |   The given value.   |
|   expected   |   None   |   The expected value.   |
|   operator   |   ==   |   One of the supported operations (==, !=, <, <=, >, >=).   |
|   error_msg   |   The value is not as expected.   |   The error message for the logs.   |

#### Copy Files SSH (test_tool_copy_files_ssh_plugin)
Copies files and folders between local machine and remote machine via ssh.

##### Call:
```yaml
- type: COPY_FILES_SSH
    call:
        user: "{{REMOTE_CMD_USER}}"
        password: "{{REMOTE_CMD_PASSWORD}}"
        host: "{{REMOTE_CMD_HOST}}"
        local_path: None
        remote_path: None
        download: False
```
##### Parameters:
| Parameter | Default | Description |
|:---------:|:--------:|:--------:|
|   user   |   {{REMOTE_CMD_USER}}   |   The user for the ssh connection.   |
|   password   |   {{REMOTE_CMD_PASSWORD}}   |   The password for the ssh connection.   |
|   host   |   {{REMOTE_CMD_HOST}}   |   The host for the ssh connection.   |
|   local_path   |   None   |   The local file or folder for the transfer.   |
|   remote_path   |   None   |   The remote file or folder for the transfer.   |
|   download   |   False   |   If this flag is set to true, the file transfer is a download, otherwise it is an upload.   |

#### JDBC SQL (test_tool_jdbc_sql_plugin)
Runs SQL Statements with [JayDeBeApi](https://pypi.org/project/JayDeBeApi/).

##### Call:
```yaml
- type: JDBC_SQL
    call:
        query: None
        save: []
        validate: []
        driver: "{{DB_DRIVER}}"
        driver_path: "{{DB_DRIVER_PATH}}"
        url: "{{DB_URL}}"
        username: "{{DB_USERNAME}}"
        password: "{{DB_PASSWORD}}"
```
Object for save:
```yaml
save:
    raw: None
    column: None
    name: None
```
Object for validate:
```yaml
save:
    raw: None
    column: None
    value: None
```
##### Parameters:
| Parameter | Default | Description |
|:---------:|:--------:|:--------:|
|   query   |   None   |   The SQL statement to run   |
|   save   |   []   |   Save a entry of a cell to a variable   |
|   vaidate   |   []   |   Validate the entry of a cell   |
|   driver   |   {{DB_DRIVER}}   |   The Class of the driver   |
|   driver_path   |   {{DB_DRIVER_PATH}}   |   The Path of the jar file   |
|   url   |   {{DB_URL}}   |   The jdbc connection string   |
|   username   |   {{DB_USERNAME}}   |   The username of the db   |
|   password   |   {{DB_PASSWORD}}   |   The password of the db   |

#### Python (test_tool_python_plugin)
Run python code from calls.yaml

##### Call:
```yaml
- type: PYTHON
    call:
        run: val='Hello World!'\nprint(val)
```

##### Parameters:
| Parameter | Default | Description |
|:---------:|:--------:|:--------:|
|   run   |   val='Hello World!'\nprint(val)   |   The code to run.   |

#### Read Jar Manifest (test_tool_read_jar_manifest_plugin)
Unpacks a jar file and parses and prints the manifest file to the logger. It also optionally saves a value.

##### Call:
```yaml
- type: READ_JAR_MANIFEST
    call:
        jar_path: "{{PATH_JAR_FILE}}"
        manifest_path: META-INF/MANIFEST.MF
        save: []
```


Object for save:
```yaml
save:
    name: None
    key: None
```

##### Parameters:
| Parameter | Default | Description |
|:---------:|:--------:|:--------:|
|   jar_path   |   {{PATH_JAR_FILE}}   |   The absolute or relative path to the jar file.   |
|   manifest_path   |   META-INF/MANIFEST.MF   |   The path within the jar file to the manifest.   |
|   save   |   None   |   Save values of the result to a variable with the given name.   |


Parameters for save:
| Parameter | Default | Description |
|:---------:|:--------:|:--------:|
|   name   |   None   |   The name for the variable to save the result in.   |
|   key   |   None   |   The key of the parsed manifest.   |

#### Rest (test_tool_rest_plugin)
Tests REST endpoints.

##### Call:
```yaml
- type: REST
    call:
        base_url: "{{REST_BASE_URL}}"
        path: "{{REST_PATH}}"
        url: None
        method: GET
        data: None
        files: None
        payload: None
        headers: {}
        response_type: JSON
        assertion: None
        hide_logs: False
        status_codes: [200]
```
##### Parameters:
| Parameter | Default | Description |
|:---------:|:--------:|:--------:|
|   base_url   |   {{REST_BASE_URL}}   |   The base url of the service to test.   |
|   path   |   {{REST_PATH}}   |   The path of the endpoint to test.   |
|   url   |  None   |   The url value is built dynamically from {{base_url}}/{{path}} if not set. Otherwiese the other values are ignored.   |
|   method   |   GET   |   The method of the call. (GET, POST, DELETE, PUT)   |
|   data   |   None   |   The data of the http call, an object is used as json.   |
|   files   |   None   |   Path of files to send.   |
|   payload   |   None   |   Payload for multipart request.   |
|   header   |   {}   |   Headers to use for request.   |
|   response_type   |  JSON   |   How to pasrse the response. (JSON, XML, TEXT)   |
|   assertion   |   NONE   |   The assertion how the response should look like   |
|   hide_log   |   False   |   Don't print the reply in the logs.   |
|   status_codes   |   [200]   |   The status codes to accept.   |


#### Run Process (test_tool_run_process_plugin)
Start a subprocess on the local machine.

##### Call:
```yaml
- type: RUN_PROCESS
    call:
        cmd: None
        timeout: None
        save: None
        shell: True
        text: True
        program: '/bin/bash'
        return_code: None
```


Object for save:
```yaml
save:
    name: None
    type: None
```

##### Parameters:
| Parameter | Default | Description |
|:---------:|:--------:|:--------:|
|   cmd   |   None   |   The command to run.   |
|   timeout   |   None   |   The timeout for the command.   |
|   save   |   None   |   Save the result to value.   |
|   text   |   True   |   Interpret the in/output as text.   |
|   shell   |   True   |   Run the program in a shell.   |
|   program   |   /bin/bash   |   The program to run the command with ('/bin/bash', '/bin/sh', '/bin/zsh').   |
|   return_code   |   None   |   The expected return code of the command 'cmd'.   |


Parameters for save:
| Parameter | Default | Description |
|:---------:|:--------:|:--------:|
|   name   |   None   |   The name for the variable to save the result in.   |
|   type   |   None   |   The type for how to treat the result (STRING, JSON).   |


#### Selenium (test_tool_selenium_plugin)
Start a webbrowser and run tests via [selenium](https://selenium-python.readthedocs.io/).

##### Call:
```yaml
- type: SELENIUM
    call:
        actions: []
        base_url: "{{GUI_BASE_URL}}"
        path: '"{{GUI_PATH}}"
        url: None
        webdriver: ['chrome']
```


Object for action:
```yaml
action: None
args: None
actions: None
log: None
```

##### Parameters:
| Parameter | Default | Description |
|:---------:|:--------:|:--------:|
|   actions   |   None   |   The actions to run on the website.   |
|   base_url   |   {{REST_BASE_URL}}   |   The base url of the website to test.   |
|   path   |   {{REST_PATH}}   |   The path of the website to test.   |
|   url   |  None   |   The url value is built dynamically from {{base_url}}/{{path}} if not set. Otherwiese the other values are ignored.   |
|   webdriver   |   True   |   A list of webdrivers to test with [chrome, gecko, chromium-edge].   |


Parameters for action:
| Parameter | Default | Description |
|:---------:|:--------:|:--------:|
|   action   |   None   |   The action to run on the driver/element.   |
|   args   |   None   |   The arguments for the action.   |
|   actions   |   None   |   Followup actions.   |
|   log   |   None   |   A log to print if the action is started.   |


#### SQL Plus (test_tool_sql_plus_plugin)
Runs a sql file with sqlplus.

##### Call:
```yaml
- type: SQL_PLUS
    call:
        file: None
        command: sqlplus
        connection: "{{DB_CONNECTION}}"
        username: "{{DB_USERNAME}}"
        password: "{{DB_PASSWORD}}"
```

##### Parameters:
| Parameter | Default | Description |
|:---------:|:--------:|:--------:|
|   file   |   None   |   The file to execute.   |
|   commane   |   sqlplus   |   The command to execute.   |
|   connection   |   {{DB_CONNECTION}}   |   The connection string to the database.  |
|   username   |   {{DB_USERNAME}}   |   The username of the database.   |
|   password   |   {{DB_PASSWORD}}   |   The password of the database.   |


#### SSH Cmd (test_tool_ssh_cmd_plugin)
Runs a command on a remote machine via ssh.

##### Call:
```yaml
- type: SSH_CMD
    call:
        user: "{{REMOTE_CMD_USER}}"
        password: "{{REMOTE_CMD_PASSWORD}}"
        host: "{{REMOTE_CMD_HOST}}"
        cmd: None
        return_code: 0
```
##### Parameters:
| Parameter | Default | Description |
|:---------:|:--------:|:--------:|
|   user   |   {{REMOTE_CMD_USER}}   |   The user for the ssh connection.   |
|   password   |   {{REMOTE_CMD_PASSWORD}}   |   The password for the ssh connection.   |
|   host   |   {{REMOTE_CMD_HOST}}   |   The host for the ssh connection.   |
|   cmd   |   None   |   The command to run.   |
|   return_code   |   None   |   The expected return code of the command 'cmd'.   |

#### Other available plugins:

This project can handle any other plugins as well. There just need to be a installed module following a naming convention.
E.g. if you define a test in the calls.yaml like:

```yaml
- type: EXAMPLE_CALL
  call:
    value1: Lorem
    value2: Ipsum
```

This tool then searches for a plugin called test_tool_example_name_plugin with the following required methods:

```python
# The default values of the plugin
default_example_name_call: Dict[str, Any] = {
  'key1': 'value1',
  'key2': 'value2'
}

# Change the values before the tests are run
def augment_example_name_call(call: Dict[str, Any], data: Dict[str, Any], path: Path) -> None:
  # Do your stuff here
  # call is a merged object from default_example_name_call and the object from the calls.yaml file.
  # data is the data from the data.yaml file modified in test steps.
  # The path of the folder where the test is.
  pass

# Make the call
def make_example_name_call(call: Dict[str, Any], data: Dict[str, Any]) -> None:
  # Do your stuff here
  # call is a merged object from default_example_name_call and the object from the calls.yaml file.
  # data is the data from the data.yaml file modified in test steps.
  pass
```

If this module is found it is used to process the test case. In an case of an error, there should be thrown an ```AssertionError```.

## Development

Read the [CONTRIBUTING.md](CONTRIBUTING.md) file.
