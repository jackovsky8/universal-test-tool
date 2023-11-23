from enum import Enum
from json import JSONDecodeError, dumps
from logging import debug, error, info
from pathlib import Path
from typing import BinaryIO, Dict, List, Optional, TextIO, Any
from xml.dom.minidom import parseString

from requests import delete, get, post, put


class Method(Enum):
    POST = 1
    GET = 2
    PUT = 3
    DELETE = 4

class Type(Enum):
    XML = 1
    JSON = 2
    TEXT = 3

class RestCall():
    base_url: str
    path: str
    url: Optional[str]
    method: Method
    data: str|object
    files: Dict[str, str]|Dict[str, TextIO]|Dict[str, BinaryIO]
    payload: Optional[Dict[str, str]]
    header: Dict
    response_type: Type
    assertion: str|Dict[str, str]
    hide_logs: bool
    status_codes: List[int]

default_rest_call: RestCall = {
    'base_url': '${REST_BASE_URL}',
    'path': '${REST_PATH}',
    'url': None,
    'method': 'GET',
    'data': None,
    'files': None,
    'payload': None,
    'headers': {},
    'response_type': 'JSON',
    'assertion': None,
    'hide_logs': False,
    'status_codes': [200]
}

def pretty_xml(xml: str) -> None:
    dom = parseString(xml)
    return dom.toprettyxml()

def pretty_json(json: str) -> None:
    return dumps(json, indent=2)

def multipartify(data, parent_key=None, formatter: callable = None) -> dict:
    if formatter is None:
        formatter = lambda v: (None, v)  # Multipart representation of value

    if type(data) is not dict:
        return {parent_key: formatter(data)}

    converted = []

    for key, value in data.items():
        current_key = key if parent_key is None else f'{parent_key}[{key}]'
        if type(value) is dict:
            converted.extend(multipartify(value, current_key, formatter).items())
        elif type(value) is list:
            for ind, list_value in enumerate(value):
                iter_key = f'{current_key}[{ind}]'
                converted.extend(multipartify(list_value, iter_key, formatter).items())
        else:
            converted.append((current_key, formatter(value)))

    return dict(converted)

def assert_response(call: RestCall) -> None:
    url = call['url']
    
    data: Dict = {
        'headers': call['headers']
    }

    # Add payload as files
    if call['payload']:
        if call['files'] == None:
            call['files'] = {}
        for key, value in call['payload'].items():
            call['files'][key] = value

    # Add multipart as files
    if call['multipart']:
        if call['files'] == None:
            call['files'] = {}
        for key, value in call['multipart'].items():
            call['files'][key] = value

    # Add data or files
    if call['files']:
        data['files'] = call['files']
        del data['headers']['Content-Type']
    elif call['data'] != None:
        data['data'] = dumps(call['data'])

    # Make the call
    info(f'Make {call["method"].name} to {url}')
    if call['method'] == Method.GET:
        response = get(url, **data)
    elif call['method'] == Method.POST:
        response = post(url, **data)
    elif call['method'] == Method.PUT:
        response = put(url, **data)
    elif call['method'] == Method.DELETE:
        response = delete(url, **data)

    info('Response Status: {}'.format(response.status_code))
    if call['hide_logs'] == False:
        try:
            info('Response:\n{}'.format(dumps(response.json(), indent=2)))
        except JSONDecodeError:
            info('Response: "{}"'.format(response.text))

    assert response.status_code in call['status_codes']
    
    if call['assertion'] != None:
        if type(call['assertion']) == str:
            assert response.text == call['assertion']
        elif type(call['assertion']) == dict:
            assert response.json() == call['assertion']
        elif type(call['assertion']) == list:
            assert response.json() == call['assertion']
        else:
            error(f'Assertion type "{type(call["assertion"])}" not supported yet.')
            assert False

def make_rest_call(call: RestCall, data: Dict[str, Any]) -> None:
    try:
        assert_response(call)
    except AssertionError:
        error('Call {} did not response as expected.'.format(call['url']))
        # Log the expected response
        try:
            if call['response_type'] == Type.XML:
                error('Expexted:\n{}'.format(pretty_xml(call['assertion'])))
            elif call['response_type'] == Type.JSON:
                error('Expexted:\n{}'.format(pretty_json(call['assertion'])))
            else:
                error('Expexted:\n{}'.format(call['assertion']))
            assert False
        except KeyError:
            pass

def augment_rest_call(call: RestCall, data: Dict, path: Path) -> None:
    # Augment the url
    if call['url'] == None:
        call['url'] = f'{call["base_url"]}{call["path"]}'

    # To Enums
    call['method'] = Method[call['method']]
    call['response_type'] = Type[call['response_type']]

    # Load files
    if call['files'] != None:
        for key, file in call['files'].items():
            if file['binary']:
                file_type = 'rb'
            else:
                file_type = 'r'
            call['files'][key] = (file['path'], open(path.joinpath(file['path']), file_type), file['media'])

    # Set Payload to None if empty
    if call['payload'] != None:
        call['payload'] = multipartify(call['payload'])

    # Work with multipart
    try:
        for key, part in call['multipart'].items():
            call['multipart'][key] = (None, dumps(part), 'application/json')

    except KeyError:
        call['multipart'] = None

def main() -> None:
    print('test-tool-rest-plugin')
