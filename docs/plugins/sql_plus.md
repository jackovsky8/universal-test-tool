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

| Parameter  |      Default      |              Description               |
| :--------: | :---------------: | :------------------------------------: |
|    file    |       None        |          The file to execute.          |
|  commane   |      sqlplus      |        The command to execute.         |
| connection | {{DB_CONNECTION}} | The connection string to the database. |
|  username  |  {{DB_USERNAME}}  |     The username of the database.      |
|  password  |  {{DB_PASSWORD}}  |     The password of the database.      |