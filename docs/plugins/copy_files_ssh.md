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

|  Parameter  |         Default         |                                       Description                                        |
| :---------: | :---------------------: | :--------------------------------------------------------------------------------------: |
|    user     |   {{REMOTE_CMD_USER}}   |                             The user for the ssh connection.                             |
|  password   | {{REMOTE_CMD_PASSWORD}} |                           The password for the ssh connection.                           |
|    host     |   {{REMOTE_CMD_HOST}}   |                             The host for the ssh connection.                             |
| local_path  |          None           |                        The local file or folder for the transfer.                        |
| remote_path |          None           |                       The remote file or folder for the transfer.                        |
|  download   |          False          | If this flag is set to true, the file transfer is a download, otherwise it is an upload. |