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

If this module is found it is used to process the test case. In an case of an error, there should be thrown an `AssertionError`.