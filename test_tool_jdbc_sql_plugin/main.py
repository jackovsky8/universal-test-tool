"""
Module for the JDBC SQL plugin.
"""
from logging import debug, error, info
from pathlib import Path
from typing import Any, Dict, List, TypedDict

from jaydebeapi import connect  # type: ignore


class JdbcSqlSave(TypedDict):
    """
    This class represents a save object.
    """
    row: int
    column: int
    name: str


class JdbcSqlValidate(TypedDict):
    """
    This class represents a validate object.
    """
    row: int
    column: int
    value: str


class JdbcSqlCall(TypedDict):
    """
    This class represents a JDBC SQL call.
    """
    query: str
    save: List[JdbcSqlSave]
    validate: List[JdbcSqlValidate]
    driver: str
    driver_path: Path
    url: str
    username: str
    password: str


default_jdbc_sql_call: JdbcSqlCall = {
    "query": None,  # type: ignore
    "save": [],
    "validate": [],
    "driver": "{{DB_DRIVER}}",
    "driver_path": "{{DB_DRIVER_PATH}}",  # type: ignore
    "url": "{{DB_URL}}",
    "username": "{{DB_USERNAME}}",
    "password": "{{DB_PASSWORD}}",
}


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
    info(f'Run query: {call["query"]}')

    # Establish the database connection
    debug(f'Connect to {call["url"]} with driver {call["driver"]}')
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

            # Get the result if needed
            if len(call["save"]) > 0 or len(call["validate"]) > 0:
                rows = cursor.fetchall()

            # Save some values
            for save in call["save"]:
                try:
                    data[save["name"]] = rows[save["row"]][save["column"]]
                except KeyError as e:
                    error(f"Save Object misses key {str(e)}")
                    assert False

            # Validate some values
            for validate in call["validate"]:
                try:
                    if str(
                        rows[validate["row"]][validate["column"]]
                    ) == str(validate["value"]):
                        info(
                            f'Validated row {validate["row"]}, \
                                column {validate["column"]} with value \
                                    {rows[validate["row"]][validate["column"]]}'
                        )
                    else:
                        error(
                            f'Expected {validate["value"]} in row {validate["row"]}, \
                                column {validate["column"]}, \
                                    but was {rows[validate["row"]][validate["column"]]}'
                        )
                        assert False
                except KeyError as e:
                    error(f"Validate Object misses key {str(e)}")
                    assert False


def augment_jdbc_sql_call(
    call: JdbcSqlCall, data: Dict, path: Path  # pylint: disable=unused-argument
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
    if not Path(call["driver_path"]).is_absolute():
        call["driver_path"] = path.joinpath(call["driver_path"]).resolve()
    else:
        call["driver_path"] = Path(call["driver_path"]).resolve()


def main() -> None:
    """
    This function will be called when the plugin is run as a script.
    """
    print("test-tool-jdbc-sql-plugin")
