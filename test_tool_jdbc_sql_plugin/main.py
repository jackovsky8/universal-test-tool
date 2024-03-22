"""
Module for the JDBC SQL plugin.
"""
import os
import re
import tempfile
from logging import getLogger
from pathlib import Path
from typing import Any, Dict, List, TypedDict, Optional
from urllib.request import urlretrieve

from jaydebeapi import Cursor, connect  # type: ignore

# Get the logger
test_tool_logger = getLogger("test-tool")

default_jdbc_driver: Dict[str, str] = {
    "org.postgresql.Driver": "https://jdbc.postgresql.org/download"
    + "/postgresql-42.7.3.jar",
    "oracle.jdbc.OracleDriver": "https://download.oracle.com/otn-pub"
    + "/otn_software/jdbc/233/ojdbc11.jar",
}


class JdbcSqlResult(TypedDict):
    """
    This class represents the result of a JDBC SQL call.
    """

    header: List[str]
    rows: List[Dict[str, Any]]


class JdbcSqlSave(TypedDict):
    """
    This class represents a save object.
    """

    path: str
    to: str


class JdbcSqlValidate(TypedDict):
    """
    This class represents a validate object.
    """

    path: str
    expected: str


class JdbcSqlCall(TypedDict):
    """
    This class represents a JDBC SQL call.
    """

    query: str
    save: List[JdbcSqlSave]
    validate: List[JdbcSqlValidate]
    driver: str
    driver_path: Path
    driver_url: str
    url: str
    username: str
    password: str


default_jdbc_sql_call: JdbcSqlCall = {
    "query": None,  # type: ignore
    "save": [],
    "validate": [],
    "driver": None,  # type: ignore
    "driver_path": None,  # type: ignore
    "driver_url": None,  # type: ignore
    "url": None,  # type: ignore
    "username": None,  # type: ignore
    "password": None,  # type: ignore
}

mandatory_jdbc_sql_call: List[str] = ["query"]

default_jdbc_sql_save: JdbcSqlSave = {
    "path": ".",  # type: ignore
    "expected": None,  # type: ignore
}

mandatory_jdbc_sql_save: List[str] = ["expected"]

default_jdbc_sql_validate: JdbcSqlValidate = {
    "path": ".",  # type: ignore
    "expected": None,  # type: ignore
}

mandatory_jdbc_sql_validate: List[str] = ["expected"]


def get_value_from_path(data: JdbcSqlResult, path: str) -> Any:
    """
    This function will get the value from the path.

    Parameters:
    ----------
    data: JdbcSqlResult
        The data to get the value from
    path: str
        The path to get the value from

    Returns:
    -------
    Any
        The value from the path
    """
    value: Any = data
    # Seperate the path
    path_list: List[str] = path.split(".")
    # remove the first element
    path_list = path_list[1:]
    # remove empty strings
    path_list = [el for el in path_list if el]
    path_log = ""
    for key in path_list:
        # Check if the key is a list
        pattern = r"\[(\d+)\]$"
        matches: List[str] = re.findall(pattern, key)
        is_list = bool(matches)
        if is_list:
            key = key.replace(f"[{matches[0]}]", "")
            idx = matches[0]
        try:
            value = value[key]
        except KeyError as e:
            test_tool_logger.error(
                "Invalid path %s in data: %s does not contain %s",
                path,
                path_log,
                key,
            )
            raise KeyError(
                f"Invalid path {path} in data: {path_log} "
                + f"does not contain {key}"
            ) from e
        path_log += f".{key}"
        if is_list:
            try:
                value = value[int(idx)]
            except IndexError as e:
                test_tool_logger.error(
                    "Invalid path %s in data: List %s does not contain idx %s",
                    path,
                    path_log,
                    idx,
                )
                raise IndexError(
                    f"Invalid path {path} in data. List {path_log} "
                    + f"does not contain idx {idx}"
                ) from e
            path_log += f"[{idx}]"
    return value


def extract_result(cursor: Cursor) -> Optional[JdbcSqlResult]:
    """
    This function will extract the result from the cursor.
    It will only return the result if it was an SELECT query.

    Parameters:
    ----------
    cursor: Cursor
        The cursor to extract the result from

    Returns:
    -------
    Optional[JdbcSqlResult]
        The result extracted from the cursor
    """
    result: Optional[JdbcSqlResult] = None
    if cursor.description is not None:
        # Create the object to store the result
        rows: List[Dict[str, Any]] = []
        header = [str(column[0]).lower() for column in cursor.description]

        fetched_rows = cursor.fetchall()
        for row in fetched_rows:
            el = {}
            for i, column in enumerate(header):
                el[column] = row[i]
            rows.append(el)

        result = {"header": header, "rows": rows}

    return result


def make_jdbc_sql_call(call: JdbcSqlCall, data: Dict[str, Any]) -> None:
    """
    This function will be called to make the JDBC SQL call.

    Parameters:
    ----------
    call: JdbcSqlCall
        The call to make
    data: Dict
        The data that was passed to the function
    """
    test_tool_logger.info("Run query: %s", call["query"])

    # Establish the database connection
    test_tool_logger.debug(
        "Connect to %s with driver %s", call["url"], call["driver"]
    )
    with connect(
        call["driver"],
        call["url"],
        [call["username"], call["password"]],
        call["driver_path"].absolute().as_posix(),
    ) as conn:
        with conn.cursor() as cursor:
            # Get the query and execute it
            query = call["query"]
            cursor.execute(query)

            result: Optional[JdbcSqlResult] = extract_result(cursor)

            # Save some values
            if result is None and call["save"]:
                test_tool_logger.error("No result to save")
                raise ValueError("No result to save")
            elif result is not None:
                for save in call["save"]:
                    data[save["to"]] = get_value_from_path(
                        result, save["path"]
                    )

            # Validate some values
            if result is None and call["validate"]:
                test_tool_logger.error("No result to validate")
                raise ValueError("No result to validate")
            elif result is not None:
                for validate in call["validate"]:
                    value = get_value_from_path(result, validate["path"])
                    assert value == validate["expected"], (
                        f"Value of {validate['path']}: "
                        + f"{value} != {validate['expected']}"
                    )


def augment_jdbc_sql_call(
    call: JdbcSqlCall,
    data: Dict,  # pylint: disable=unused-argument
    path: Path,  # pylint: disable=unused-argument
) -> None:
    """
    This function will be called before the function above.

    Parameters:
    ----------
    call: JdbcSqlCall
        The call to make
    data: Dict
        The data that was passed to the function
    path: Path
        The path of the file
    """
    # Check db parameters
    db_parameters: List[str] = [
        "url",
        "username",
        "password",
        "driver",
        "driver_path",
        "driver_url",
    ]
    # Define the required parameters
    db_parameters_required: List[str] = [
        "url",
        "username",
        "password",
        "driver",
    ]

    for parameter in db_parameters:
        env_parameter = f"DB_{parameter.upper()}"
        if call[parameter] is None and env_parameter in data:  # type: ignore
            call[parameter] = data[env_parameter]  # type: ignore
        if call[parameter] is None:  # type: ignore
            call[parameter] = os.getenv(env_parameter)  # type: ignore
        if (
            call[parameter] is None  # type: ignore
            and parameter in db_parameters_required
        ):
            test_tool_logger.error(
                "Env or data %s not provided", env_parameter
            )
            raise KeyError(f"Env or data {env_parameter} not provided")

    if call["driver_path"] is None:
        if call["driver_url"] is None:
            if call["driver"] not in default_jdbc_driver:
                test_tool_logger.error(
                    "Driver url or driver path not provided for driver %s",
                    call["driver"],
                )
                raise KeyError(
                    "Driver url or driver path not provided for driver "
                    + call["driver"]
                )
            else:
                call["driver_url"] = default_jdbc_driver[call["driver"]]

        # Download the driver
        driver_with_version: str = call["driver_url"].split("/")[-1]
        driver_filename: str = f"{tempfile.gettempdir()}/{driver_with_version}"
        if not os.path.exists(driver_filename):
            urlretrieve(call["driver_url"], driver_filename)

        call["driver_path"] = driver_filename

    # Get the absolute path of the driver
    if not Path(call["driver_path"]).is_absolute():
        call["driver_path"] = path.joinpath(call["driver_path"]).resolve()
    else:
        call["driver_path"] = Path(call["driver_path"]).resolve()

    # Query is mandatory
    if call["query"] is None:
        test_tool_logger.error("Missing mandatory parameter query")
        raise ValueError("Missing mandatory parameter query")

    # Validate path for save and validate
    new_list = call.get("save", []) + call.get("validate", [])  # type: ignore
    for el in new_list:
        path_string: str = el["path"]
        pattern: str = (
            r"^\.(rows(\[\d*\](\.[a-zA-Z0-9_]*)?)?|header(\[\d*\])?)$"
        )
        # validate path
        if not re.match(pattern, path_string):
            test_tool_logger.error(
                "Parameter path is invalid: %s", path_string
            )
            raise ValueError(f"Parameter path is invalid: {path_string}")


def main() -> None:
    """
    This function will be called when the plugin is run as a script.
    """
    print("test-tool-jdbc-sql-plugin")
