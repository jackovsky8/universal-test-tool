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

|  Parameter  |         Default         |                  Description                   |
| :---------: | :---------------------: | :--------------------------------------------: |
|    user     |   {{REMOTE_CMD_USER}}   |        The user for the ssh connection.        |
|  password   | {{REMOTE_CMD_PASSWORD}} |      The password for the ssh connection.      |
|    host     |   {{REMOTE_CMD_HOST}}   |        The host for the ssh connection.        |
|     cmd     |          None           |              The command to run.               |
| return_code |          None           | The expected return code of the command 'cmd'. |