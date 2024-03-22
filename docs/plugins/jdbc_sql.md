# jdbc SQL

This plugin is used to make basic sql statements with the package [JayDeBeApi](https://pypi.org/project/JayDeBeApi/).

## Features

### Run any sql Statement

You can run any sql statement with this plugin.

For exemple you could insert data before you run your tests.

```sql
INSERT INTO test VALUES (1, 'test1')
```

Or you could retrieve data to validate if it got manipulated correctly during the test.

```sql
SELECT * FROM test
```

### Save the retrieved data

You can also save the retrieved data to the **_data-Object_**. This of course only makes sense with **_SELECT_** Statements. For other statements it will produce an error.

### Validate

You can also validate the retrieved data. This of course only makes sense with **_SELECT_** Statements. For other statements it will produce an error. You can validate against all available datatype (available in yaml)

## Calls

The call looks like:

```yaml
- type: JDBC_SQL
    call:
        query: None
        save: []
        validate: []
        driver: "{{DB_DRIVER}}"
        driver_path: "{{DB_DRIVER_PATH}}"
        driver_url: "{{DB_DRIVER_URL}}"
        url: "{{DB_URL}}"
        username: "{{DB_USERNAME}}"
        password: "{{DB_PASSWORD}}"
```

The objects for save look like:

```yaml
save:
  path: "."
  to: None
```

The objects for validate look like:

```yaml
validate:
  path: "."
  expected: None
```

### Parameters

|  Parameter  |      Default       |           Description            |
| :---------: | :----------------: | :------------------------------: |
|    query    |        None        |     The SQL statement to run     |
|    save     |         []         |  Save the result to a variable   |
|   vaidate   |         []         |       Validate the result        |
|   driver    |   {{DB_DRIVER}}    |     The Class of the driver      |
| driver_path | {{DB_DRIVER_PATH}} |     The Path to the jar file     |
| driver_url  | {{DB_DRIVER_URL}}  | The Url to download the jar file |
|     url     |     {{DB_URL}}     |    The jdbc connection string    |
|  username   |  {{DB_USERNAME}}   |      The username of the db      |
|  password   |  {{DB_PASSWORD}}   |      The password of the db      |
