"""
Docstring for the main module.
"""
from enum import Enum
from logging import getLogger
from typing import Any, Callable, Dict, List, TypedDict

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chromium.options import ChromiumOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from test_tool_selenium_plugin.actions import (BLACKLIST, SeleniumAction,
                                               get_arguments,
                                               get_set_or_call_attribute,
                                               run_action)
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

# Get the logger
test_tool_logger = getLogger("test-tool")


class BrowserType(Enum):
    """
    Enum for the different browser types.
    """

    CHROME = "chrome"
    GECKO = "gecko"
    CHROMIUM_EDGE = "chromium-edge"


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


class SeleniumCall(TypedDict):
    """
    The structure of a Selenium call.
    """

    actions: List[SeleniumAction]
    base_url: str
    path: str
    url: str
    webdriver: List[BrowserType]
    options: Dict[str, Any]


# Define the default call
default_selenium_call: SeleniumCall = {
    "actions": [],
    "base_url": "{{GUI_BASE_URL}}",
    "path": "{{GUI_PATH}}",
    "url": None,  # type: ignore
    "webdriver": ["chrome"],  # type: ignore
    "options": {},
}


def make_selenium_call(call: SeleniumCall) -> None:
    """
    Make a Selenium call.

    Parameters:
    -----------
    call: SeleniumCall
        The call to make.
    data: Dict[str, Any]
        The data to make the call with.
    """
    test_tool_logger.info("Selenium Call wit url %s", call["url"])

    # For each webdriver
    for web_driver in call["webdriver"]:
        # Install the webdriver
        BROWSER_MAPPING[web_driver]().install()

        # Create browser options
        browser_options = BROWSER_OPTIONS_MAPPING[web_driver]()
        for option in call["options"].keys():
            if option in BLACKLIST:
                raise ValueError(f"Option {option} is not allowed.")
            elif option not in dir(browser_options):
                raise ValueError(f"Action {option} is not available.")
            else:
                get_set_or_call_attribute(
                    browser_options,
                    option,
                    get_arguments(call["options"][option], browser_options),
                )

        # Create a new instance of the Chrome driver
        driver = BROWSER_DRIVER_MAPPING[web_driver](options=browser_options)

        # Open the website
        driver.get(call["url"])

        # Run some actions on the website
        for action in call["actions"]:
            run_action(action, driver)

        # Quit the browser
        driver.quit()


def augment_selenium_call(call: SeleniumCall) -> None:
    """
    Augment the call.

    Parameters:
    -----------
    call: SeleniumCall
        The call to augment.
    """
    # Augment the url
    if call["url"] is None:
        call["url"] = f'{call["base_url"]}{call["path"]}'

    # The webdriver is a list of browser types
    call["webdriver"] = [BrowserType(driver) for driver in call["webdriver"]]


# Define the main function
def main() -> None:
    """
    The main function.^
    """
    print("test-tool-selenium-plugin")
