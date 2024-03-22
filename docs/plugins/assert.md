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

| Parameter |            Default            |                       Description                       |
| :-------: | :---------------------------: | :-----------------------------------------------------: |
|   value   |             None              |                    The given value.                     |
| expected  |             None              |                   The expected value.                   |
| operator  |              ==               | One of the supported operations (==, !=, <, <=, >, >=). |
| error_msg | The value is not as expected. |             The error message for the logs.             |