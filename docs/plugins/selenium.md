#### Selenium (test_tool_selenium_plugin)

Start a webbrowser and run tests via [selenium](https://selenium-python.readthedocs.io/).

##### Call:

```yaml
- type: SELENIUM
    call:
        actions: []
        base_url: "{{GUI_BASE_URL}}"
        path: "{{GUI_PATH}}"
        url: None
        webdriver: ['chrome']
        option: {}
```

Object for action:

```yaml
action: None
args: None
actions: None
log: None
```

##### Parameters:

| Parameter |      Default      |                                                    Description                                                     |
| :-------: | :---------------: | :----------------------------------------------------------------------------------------------------------------: |
|  actions  |       None        |                                         The actions to run on the website.                                         |
| base_url  | {{REST_BASE_URL}} |                                        The base url of the website to test.                                        |
|   path    |   {{REST_PATH}}   |                                          The path of the website to test.                                          |
|    url    |       None        | The url value is built dynamically from {{base_url}}/{{path}} if not set. Otherwiese the other values are ignored. |
| webdriver |       True        |                         A list of webdrivers to test with [chrome, gecko, chromium-edge].                          |
| webdriver |       True        |                                                      Options                                                       |

Parameters for action:

| Parameter | Default |               Description                |
| :-------: | :-----: | :--------------------------------------: |
|  action   |  None   | The action to run on the driver/element. |
|   args    |  None   |      The arguments for the action.       |
|  actions  |  None   |            Followup actions.             |
|    log    |  None   | A log to print if the action is started. |
