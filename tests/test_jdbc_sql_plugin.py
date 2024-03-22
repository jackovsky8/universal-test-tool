"""
This module contains tests for the JDBC SQL plugin.
"""
import os
from copy import deepcopy
from pathlib import Path
from typing import Dict

import pytest
from jaydebeapi import DatabaseError  # type: ignore
from test_tool_jdbc_sql_plugin.main import (
    JdbcSqlCall,
    JdbcSqlResult,
    augment_jdbc_sql_call,
    default_jdbc_sql_call,
    get_value_from_path,
    make_jdbc_sql_call,
)

# pylint: disable-next=F0401
from testcontainers.postgres import PostgresContainer  # type: ignore

POSTGRES = PostgresContainer("postgres:16-alpine")


@pytest.fixture(scope="module", autouse=True)
def setup(request) -> None:
    """
    Setup the test environment by starting the Postgres container.

    Parameters:
    ----------
    request : fixture
        Pytest fixture that allows the test to be configured.
    """
    POSTGRES.start()

    def remove_container():
        POSTGRES.stop()

    request.addfinalizer(remove_container)
    host: str = POSTGRES.get_container_host_ip()
    port: int = POSTGRES.get_exposed_port(5432)
    db: str = POSTGRES.dbname
    os.environ["DB_URL"] = f"jdbc:postgresql://{host}:{port}/{db}"
    os.environ["DB_USERNAME"] = POSTGRES.username
    os.environ["DB_PASSWORD"] = POSTGRES.password
    os.environ["DB_DRIVER"] = "org.postgresql.Driver"


@pytest.fixture(scope="module", autouse=True)
def setup_basic_data() -> None:
    """
    Setup the test data.
    """
    call: JdbcSqlCall = deepcopy(default_jdbc_sql_call)
    call["query"] = "CREATE TABLE test (id INT PRIMARY KEY, name VARCHAR(255))"

    data: Dict = {}

    augment_jdbc_sql_call(call, data, Path(__file__))
    make_jdbc_sql_call(call, data)


@pytest.fixture(scope="function", autouse=True)
def setup_data() -> None:
    """
    Setup the test data.
    """
    call: JdbcSqlCall = deepcopy(default_jdbc_sql_call)
    call["query"] = "DELETE FROM test"

    data: Dict = {}

    augment_jdbc_sql_call(call, data, Path(__file__))
    make_jdbc_sql_call(call, data)

    call["query"] = "INSERT INTO test VALUES (1, 'test1')"
    make_jdbc_sql_call(call, data)

    call["query"] = "INSERT INTO test VALUES (2, 'test2')"
    make_jdbc_sql_call(call, data)


def test_jdbc_sql_plugin_basic() -> None:
    """
    Basic test for the JDBC SQL plugin.
    """
    call: JdbcSqlCall = deepcopy(default_jdbc_sql_call)
    call["query"] = "SELECT 1"

    data: Dict = {}

    augment_jdbc_sql_call(call, data, Path(__file__))
    make_jdbc_sql_call(call, data)


def test_retrieve_and_save_one_row() -> None:
    """
    Test to retrieve and save one row.
    """
    call: JdbcSqlCall = deepcopy(default_jdbc_sql_call)
    call["query"] = "SELECT * FROM test WHERE id = 1"
    call["save"] = [{"path": ".rows[0].name", "to": "name"}]

    data: Dict = {}

    augment_jdbc_sql_call(call, data, Path(__file__))
    make_jdbc_sql_call(call, data)

    assert data["name"] == "test1"


def test_retrieve_and_validate_one_row() -> None:
    """
    Test to retrieve and validate one row.
    """
    call: JdbcSqlCall = deepcopy(default_jdbc_sql_call)
    call["query"] = "SELECT * FROM test WHERE id = 1"
    call["validate"] = [{"path": ".rows[0].name", "expected": "test1"}]

    data: Dict = {}

    augment_jdbc_sql_call(call, data, Path(__file__))
    make_jdbc_sql_call(call, data)


def test_insert_one_row() -> None:
    """
    Test to insert one row.
    """
    call: JdbcSqlCall = deepcopy(default_jdbc_sql_call)
    call["query"] = "INSERT INTO test VALUES (3, 'test3')"

    data: Dict = {}

    augment_jdbc_sql_call(call, data, Path(__file__))
    make_jdbc_sql_call(call, data)


def test_wrong_syntax() -> None:
    """
    Test for wrong syntax.
    """
    call: JdbcSqlCall = deepcopy(default_jdbc_sql_call)
    call["query"] = "SELECT * FROM test WHERES id = 1"

    data: Dict = {}

    augment_jdbc_sql_call(call, data, Path(__file__))
    with pytest.raises(DatabaseError) as excinfo:
        make_jdbc_sql_call(call, data)

    assert 'ERROR: syntax error at or near "id"\n  Position: 27' in str(
        excinfo.value.args[0].args[0]
    )


def test_invalid_path() -> None:
    """
    Test for invalid path.
    """
    call: JdbcSqlCall = deepcopy(default_jdbc_sql_call)
    call["query"] = "SELECT * FROM test WHERE id = 1"
    call["save"] = [{"path": "rows[0].name", "to": "name"}]

    data: Dict = {}

    with pytest.raises(ValueError) as excinfo:
        augment_jdbc_sql_call(call, data, Path(__file__))

    assert "Parameter path is invalid: rows[0].name" in str(
        excinfo.value.args[0]
    )


def test_missing_query() -> None:
    """
    Test for missing query.
    """
    call: JdbcSqlCall = deepcopy(default_jdbc_sql_call)

    data: Dict = {}

    with pytest.raises(ValueError) as excinfo:
        augment_jdbc_sql_call(call, data, Path(__file__))

    assert "Missing mandatory parameter query" in str(excinfo.value.args[0])


def test_get_value_from_path_existing() -> None:
    """
    Test for getting a value from a path that exists.
    """
    data: JdbcSqlResult = {"rows": [{"name": "test1"}], "header": ["name"]}

    assert get_value_from_path(data, ".rows[0].name") == "test1"


def test_get_value_from_path_not_existing() -> None:
    """
    Test for getting a value from a path that does not exist.
    """
    data: JdbcSqlResult = {"rows": [{"name": "test1"}], "header": ["name"]}

    with pytest.raises(KeyError) as excinfo:
        get_value_from_path(data, ".rows[0].names")

    assert (
        excinfo.value.args[0]
        == "Invalid path .rows[0].names in data: .rows[0] does not contain names"
    )
