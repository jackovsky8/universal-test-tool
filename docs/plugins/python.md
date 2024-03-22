#### Python (test_tool_python_plugin)

Run python code from calls.yaml

##### Call:

```yaml
- type: PYTHON
    call:
        run: val='Hello World!'\nprint(val)
```

##### Parameters:

| Parameter |            Default             |   Description    |
| :-------: | :----------------------------: | :--------------: |
|    run    | val='Hello World!'\nprint(val) | The code to run. |