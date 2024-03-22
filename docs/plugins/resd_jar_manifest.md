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

|   Parameter   |       Default        |                         Description                          |
| :-----------: | :------------------: | :----------------------------------------------------------: |
|   jar_path    |  {{PATH_JAR_FILE}}   |        The absolute or relative path to the jar file.        |
| manifest_path | META-INF/MANIFEST.MF |        The path within the jar file to the manifest.         |
|     save      |         None         | Save values of the result to a variable with the given name. |

Parameters for save:

| Parameter | Default |                   Description                    |
| :-------: | :-----: | :----------------------------------------------: |
|   name    |  None   | The name for the variable to save the result in. |
|    key    |  None   |         The key of the parsed manifest.          |