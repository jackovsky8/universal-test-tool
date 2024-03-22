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

|  Parameter  |  Default  |                                Description                                |
| :---------: | :-------: | :-----------------------------------------------------------------------: |
|     cmd     |   None    |                            The command to run.                            |
|   timeout   |   None    |                       The timeout for the command.                        |
|    save     |   None    |                         Save the result to value.                         |
|    text     |   True    |                     Interpret the in/output as text.                      |
|    shell    |   True    |                        Run the program in a shell.                        |
|   program   | /bin/bash | The program to run the command with ('/bin/bash', '/bin/sh', '/bin/zsh'). |
| return_code |   None    |              The expected return code of the command 'cmd'.               |

Parameters for save:

| Parameter | Default |                     Description                      |
| :-------: | :-----: | :--------------------------------------------------: |
|   name    |  None   |   The name for the variable to save the result in.   |
|   type    |  None   | The type for how to treat the result (STRING, JSON). |