#### Rest (test_tool_rest_plugin)

Tests REST endpoints.

##### Call:

```yaml
- type: REST
    call:
        base_url: "{{REST_BASE_URL}}"
        path: "{{REST_PATH}}"
        url: None
        method: GET
        data: None
        files: None
        payload: None
        headers: {}
        response_type: JSON
        assertion: None
        hide_logs: False
        status_codes: [200]
```

##### Parameters:

|   Parameter   |      Default      |                                                    Description                                                     |
| :-----------: | :---------------: | :----------------------------------------------------------------------------------------------------------------: |
|   base_url    | {{REST_BASE_URL}} |                                        The base url of the service to test.                                        |
|     path      |   {{REST_PATH}}   |                                         The path of the endpoint to test.                                          |
|      url      |       None        | The url value is built dynamically from {{base_url}}/{{path}} if not set. Otherwiese the other values are ignored. |
|    method     |        GET        |                                  The method of the call. (GET, POST, DELETE, PUT)                                  |
|     data      |       None        |                               The data of the http call, an object is used as json.                                |
|     files     |       None        |                                               Path of files to send.                                               |
|    payload    |       None        |                                           Payload for multipart request.                                           |
|    header     |        {}         |                                            Headers to use for request.                                             |
| response_type |       JSON        |                                   How to pasrse the response. (JSON, XML, TEXT)                                    |
|   assertion   |       NONE        |                                  The assertion how the response should look like                                   |
|   hide_log    |       False       |                                         Don't print the reply in the logs.                                         |
| status_codes  |       [200]       |                                            The status codes to accept.                                             |