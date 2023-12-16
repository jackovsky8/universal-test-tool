from enum import Enum
from logging import info
from pathlib import Path
from time import sleep
from typing import Any, Callable, Dict, List, Optional, TypedDict, Union

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chromium.options import ChromiumOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager


def assert_equals(
        reference: Any, 
        given: Any, 
        message: str = 'Values should equal:') -> None:
    """Assert that the given and reference values are equal."""
    assert reference == given, f'{message} Reference: {reference} Given: {given}'

def assert_not_equals(
        reference: Any, 
        given: Any, 
        message: str = 'Values should not equal:') -> None:
    """Assert that the given and reference values are not equal."""
    assert reference != given, f'{message} Reference: {reference} Given: {given}'

def assert_true(
        given: Any, 
        message: str = 'Value should be true:') -> None:
    """Assert that the given value is true."""
    assert given, f'{message} Given: {given}'

def assert_false(
        given: Any, 
        message: str = 'Value should be false:') -> None:
    """Assert that the given value is false."""
    assert not given, f'{message} Given: {given}'

def assert_greater_than(
        reference: Any, 
        given: Any, 
        message: str = 'Value should be greater than:') -> None:
    """Assert that the given value is greater than the reference value."""
    assert reference > given, f'{message} Reference: {reference} Given: {given}'

def assert_greater_than_or_equals(
        reference: Any, 
        given: Any, 
        message: str = 'Value should be greater or equal than:') -> None:
    """Assert that the given value is greater than or equals the reference value."""
    assert reference >= given, f'{message} Reference: {reference} Given: {given}'

def assert_less_than(
        reference: Any, 
        given: Any, 
        message: str = 'Value should be less than:') -> None:
    """Assert that the given value is less than the reference value."""
    assert reference < given, f'{message} Reference: {reference} Given: {given}'

def assert_less_than_or_equals(
        reference: Any, 
        given: Any, 
        message: str = 'Value should be less or equal than:') -> None:
    """Assert that the given value is less than or equals the reference value."""
    assert reference <= given, f'{message} Reference: {reference} Given: {given}'

# Blacklist
BLACKLIST: List[str] = [
    r'__.*__',  # Python magic methods
    'quit',     # Quit the browser
    'close',    # Close the current window
]

ADD_ACTION: Dict[str, Any] = {
    'sleep': sleep,
    'assert_equals': assert_equals,
    'assert_not_equals': assert_not_equals,
    'assert_true': assert_true,
    'assert_false': assert_false,
    'assert_greater_than': assert_greater_than,
    'assert_greater_than_or_equals': assert_greater_than_or_equals,
    'assert_less_than': assert_less_than,
    'assert_less_than_or_equals': assert_less_than_or_equals,
}

# Type definition for arguments
Arguments = List[Union[Dict[Any, Any], List[Any], str, int, float, bool]]

# Define enum for the different browser types
class BrowserType(Enum):
    CHROME = 'chrome'
    GECKO = 'gecko'
    CHROMIUM_EDGE = 'chromium-edge'

# Define the mapping between the browser type and the driver manager
BROWSER_MAPPING: Dict[BrowserType, Callable] = {
    BrowserType.CHROME: ChromeDriverManager,
    BrowserType.GECKO: GeckoDriverManager,
    BrowserType.CHROMIUM_EDGE: EdgeChromiumDriverManager,
}

# Define the mapping between the browser type and the options
BROWSER_OPTIONS_MAPPING: Dict[BrowserType, Callable] = {
    BrowserType.CHROME: ChromeOptions,
    BrowserType.GECKO: FirefoxOptions,
    BrowserType.CHROMIUM_EDGE: ChromiumOptions,
}

# Define the mapping between the browser type and the driver
BROWSER_DRIVER_MAPPING: Dict[BrowserType, Callable] = {
    BrowserType.CHROME: webdriver.Chrome,
    BrowserType.GECKO: webdriver.Firefox,
    BrowserType.CHROMIUM_EDGE: webdriver.ChromiumEdge,
}

# Define enum for the different argument types
class ArgumentType(Enum):
    BOOLEAN = 'boolean'
    STRING = 'string'
    INTEGER = 'integer'
    FLOAT = 'float'
    LIST = 'list'
    DICTIONARY = 'dictionary'
    EVAL = 'eval'
    ACTION = 'action'

# Define the call structure
class SeleniumCall(TypedDict):
    actions: List['SeleniumAction']
    base_url: str
    path: str
    url: Optional[str]
    webdriver: List[BrowserType]

# Define the action structure
class SeleniumAction(TypedDict):
    action: str
    args: Optional[Arguments]
    actions: Optional[List['SeleniumAction']]
    log: Optional[str]

# Define the default call
default_selenium_call: SeleniumCall = {
    'actions': [],
    'base_url': '${GUI_BASE_URL}',
    'path': '${GUI_PATH}',
    'url': None,
    'webdriver': ['chrome']
}

# Define the function that will be called
def make_selenium_call(call: SeleniumCall, data: Dict[str, Any]) -> None:
    """Make a Selenium call.
    
    Parameters:
    - call: The call to make.
    - data: The data to make the call with.
    
    Returns:
    Nothing.
    """
    info(f'Selenium Call wit url {call["url"]}')

    # For each webdriver
    for webdriver in call['webdriver']:
        # Install the webdriver
        BROWSER_MAPPING[webdriver]().install()

        # Create browser options
        browser_options = BROWSER_OPTIONS_MAPPING[webdriver]()
        for option in call['options'].keys():
            if option in BLACKLIST:
                ValueError(f'Option {option} is not allowed.')
            elif option not in dir(browser_options):
                ValueError(f'Action {option} is not available.')
            else:
                get_set_or_call_attribute(
                    browser_options, 
                    option, 
                    get_arguments(call['options'][option], browser_options))


        # Create a new instance of the Chrome driver
        driver = BROWSER_DRIVER_MAPPING[webdriver](options=browser_options)

        # Open the website
        driver.get(call['url'])

        # Run some actions on the website
        for action in call['actions']:
            run_action(action, driver)

        # Quit the browser
        driver.quit()
    
def run_action(action: SeleniumAction, element: Any) -> Any:
    """Run an action.
    
    Parameters:
    - action: The action to run.
    - element: The element to run the action on.
    
    Returns:
    The result of the action.
    """
    # Log the action
    info(action.get('log', f'Action {action["action"]}'))
    # Action is an extra action that is not part of Selenium
    if action['action'] in ADD_ACTION.keys():
        result = call_callable_with_args(
            ADD_ACTION[action['action']], 
            get_arguments(action.get('args', None), element))
    # Check if the action is in the blacklist
    elif action['action'] in BLACKLIST:
        raise ValueError(f'Action {action["action"]} is not allowed.')
        return None
    # Check if the action is available
    elif action['action'] not in dir(element):
        raise ValueError(f'Action {action["action"]} is not available.')
    else:
        # Call the callable with the arguments
        result = get_set_or_call_attribute(
            element, 
            action['action'], 
            get_arguments(action.get('args', None), element))

    # Get and run the following actions
    actions = action.get('actions', [])
    new_result = result
    for sub_action in actions:
        new_result = run_action(sub_action, result)

    return new_result

# Todo Type of parameter
def get_arguments(args: Any, element: Any) -> Arguments:
    """Get the arguments of an action.
    
    Parameters:
    - args: The arguments to get.
    - element: The element to get the arguments for.
    
    Returns:
    The arguments.
    """
    # List of arguments
    result: Arguments = []
    # Native types
    if isinstance(args, bool) or isinstance(args, str) or isinstance(args, int) or isinstance(args, float):
        result.append(args)
    # Dict can be everything
    elif isinstance(args, dict):
        type = ArgumentType(args.get('type', None))
        if type in (
                ArgumentType.BOOLEAN, 
                ArgumentType.STRING, 
                ArgumentType.INTEGER, 
                ArgumentType.FLOAT, 
                ArgumentType.LIST, 
                ArgumentType.DICTIONARY
            ):
            result.append(args['value'])
        elif type == ArgumentType.EVAL:
            result.append(eval(args['value']))
        elif type == ArgumentType.ACTION:
            action: SeleniumAction = args['value']
            result.append(run_action(action, element))
    # List can be a list of everything
    elif isinstance(args, list):
        for arg in args:
            result.extend(get_arguments(arg, element))

    return result

# TODO Argumnts is always a list
def get_set_or_call_attribute(clazz: Any, attribute: str, args: Arguments) -> Any:
    """Get, set or call an attribute of a class.

    Parameters:
    - clazz: The class to get, set or call the attribute of.
    - attribute: The attribute to get, set or call.
    - args: The arguments to call the attribute with.

    Returns:
    The result of the attribute.
    """
    attribute_of_clazz = getattr(clazz, attribute)
    if callable(attribute_of_clazz):
        return call_callable_with_args(attribute_of_clazz, args)
    else:
        # Get attribute
        if len(args) == 0:
            return getattr(clazz, attribute)
        # Set attribute
        else:
            if isinstance(attribute_of_clazz, bool):
                if not len(args) == 1 or not isinstance(args[0], bool):
                    raise ValueError(f'Option {attribute} is a boolean, but arg isn\'t.')
                else:
                    setattr(clazz, attribute, args[0])
            elif isinstance(attribute_of_clazz, str):
                if not len(args) == 1 or not isinstance(args[0], str):
                    raise ValueError(f'Option {attribute} is a string, but arg isn\'t.')
                else:
                    setattr(clazz, attribute, args[0])
            elif isinstance(attribute_of_clazz, int):
                if not len(args) == 1 or not isinstance(args[0], int):
                    raise ValueError(f'Option {attribute} is an integer, but arg isn\'t.')
                else:
                    setattr(clazz, attribute, args[0])
            elif isinstance(attribute_of_clazz, float):
                if not len(args) == 1 or not isinstance(args[0], float):
                    raise ValueError(f'Option {attribute} is a float, but arg isn\'t.')
                else:
                    setattr(clazz, attribute, args[0])
            else:
                # Setter no implemented for other values
                raise NotImplementedError(f'Option {attribute} is of type {type(attribute_of_clazz)}.')

    return clazz

def call_callable_with_args(
        callable: Callable, 
        args: Optional[Union[Dict, List, int, float, str]] = None) -> Any:
    """Call a callable with the given arguments.
    
    Parameters:
    - callable: The callable to call.
    - args: The arguments to call the callable with.
    
    Returns:
    The result of the callable.
    """
    if isinstance(args, dict):
        return callable(**args)
    elif isinstance(args, list):
        return callable(*args)
    elif args is not None:
        return callable(args)
    else:
        return callable()

# Define the function that will be called before the function above
def augment_selenium_call(call: SeleniumCall, data: Dict, path: Path) -> None:
    """Augment the call.
    
    Parameters:
    - call: The call to augment.
    - data: The data to augment the call with.
    - path: The path of the call.
    
    Returns:
    Nothing.
    """
    # Augment the url
    if call['url'] == None:
        call['url'] = f'{call["base_url"]}{call["path"]}'

    # The webdriver is a list of browser types
    call['webdriver'] = [BrowserType(driver) for driver in call['webdriver']]

                     
# Define the main function                     
def main() -> None:
    print('test-tool-selenium-plugin')