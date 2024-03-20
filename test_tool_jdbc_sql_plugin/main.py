"""
Module for the JDBC SQL plugin.
"""
from logging import debug, error, info
from pathlib import Path
from typing import Any, Dict, List, TypedDict

from jaydebeapi import connect


class JdbcSqlSave(TypedDict):
    row: int
    column: int
    name: str


class JdbcSqlValidate(TypedDict):
    row: int
    column: int
    value: str


class JdbcSqlCall(TypedDict):
    query: str
    save: List[JdbcSqlSave]
    validate: List[JdbcSqlValidate]
    driver: str
    driver_path: str
    url: str
    username: str
    password: str


default_jdbc_sql_call: JdbcSqlCall = {
    "query": None,  # type: ignore
    "save": [],
    "validate": [],
    "driver": "{{DB_DRIVER}}",
    "driver_path": "{{DB_DRIVER_PATH}}",
    "url": "{{DB_URL}}",
    "username": "{{DB_USERNAME}}",
    "password": "{{DB_PASSWORD}}",
}


def make_jdbc_sql_call(call: JdbcSqlCall, data: Dict[str, Any]) -> None:
    info(f'Run query: {call["query"]}')

    # Establish the database connection
    debug(f'Connect to {call["url"]} with driver {call["driver"]}')
    with connect(
        call["driver"],
        call["url"],
        [call["username"], call["password"]],
        call["driver_path"],
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
                    if not str(
                        rows[validate["row"]][validate["column"]]
                    ) == str(validate["value"]):
                        error(
                            f'Expected {validate["value"]} in row {validate["row"]}, column {validate["column"]}, but was {rows[validate["row"]][validate["column"]]}'
                        )
                        assert False
                    else:
                        info(
                            f'Validated row {validate["row"]}, column {validate["column"]} with value {rows[validate["row"]][validate["column"]]}'
                        )
                except KeyError as e:
                    error(f"Validate Object misses key {str(e)}")
                    assert False


def augment_jdbc_sql_call(
    call: JdbcSqlCall, data: Dict, path: Path
) -> None:  # pylint: disable=unused-argument
    pass


def main() -> None:
    print("test-tool-jdbc-sql-plugin")
