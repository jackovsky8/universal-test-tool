from logging import error, info
from pathlib import Path
from typing import Any, Dict, TypedDict
from enum import Enum

# Enumerate the possible operators
class Operator(Enum):
    EQUAL = '=='
    NOT_EQUAL = '!='
    LESS_THAN = '<'
    LESS_THAN_OR_EQUAL = '<='
    GREATER_THAN = '>'
    GREATER_THAN_OR_EQUAL = '>='

# Define the call structure
class AssertCall(TypedDict):
    value: Any
    expected: Any
    operator: Operator
    error_msg: str

# Define the default call
default_assert_call: AssertCall = {
    'value': None,
    'expected': None,
    'operator': '==',
    'error_msg': 'The value is not as expected.'
}

# Define the function that will be called
def make_assert_call(call: AssertCall, data: Dict[str, Any]) -> None:
    info(f'Asserting {call["value"]} {call["operator"].name} {call["expected"]}')

    # Compare to values dynamically
    if call['operator'] == Operator.EQUAL:
        if call['value'] != call['expected']:
            error(call['error_msg'])
            assert False, call['error_msg']
    elif call['operator'] == Operator.NOT_EQUAL:
        if call['value'] == call['expected']:
            error(call['error_msg'])
            assert False, call['error_msg']
    elif call['operator'] == Operator.LESS_THAN:
        if call['value'] >= call['expected']:
            error(call['error_msg'])
            assert False, call['error_msg']
    elif call['operator'] == Operator.LESS_THAN_OR_EQUAL:
        if call['value'] > call['expected']:
            error(call['error_msg'])
            assert False, call['error_msg']
    elif call['operator'] == Operator.GREATER_THAN:
        if call['value'] <= call['expected']:
            error(call['error_msg'])
            assert False, call['error_msg']
    elif call['operator'] == Operator.GREATER_THAN_OR_EQUAL:
        if call['value'] < call['expected']:
            error(call['error_msg'])
            assert False, call['error_msg']
    else:
        error(f'Unknown operator {call["operator"]}')

# Define the function that will be called before the function above
def augment_assert_call(call: AssertCall, data: Dict, path: Path) -> None:
    try:
        call['operator'] = Operator(call['operator'])
    except ValueError:
        error(f'Unknown operator {call["operator"]}')
                     
# Define the main function                     
def main() -> None:
    print('test-tool-assert-plugin')