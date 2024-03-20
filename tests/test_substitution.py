"""
This module contains tests for the substitution module.
"""
import pytest
from test_tool.substitute import (
    replace_string_variables,
    recursively_replace_variables,
)


def test_basic_string_substitution_in_string():
    """
    Test basic string substitution.
    """
    data = {"var": "value"}
    string = "This is a {{var}}"

    assert replace_string_variables(string, data) == "This is a value"


def test_basic_int_substitution_in_string():
    """
    Test basic int substitution.
    """
    data = {"var": 1}
    string = "This is a {{var}}"

    assert replace_string_variables(string, data) == "This is a 1"


def test_basic_float_substitution_in_string():
    """
    Test basic float substitution.
    """
    data = {"var": 1.0}
    string = "This is a {{var}}"

    assert replace_string_variables(string, data) == "This is a 1.0"


def test_basic_bool_substitution_in_string():
    """
    Test basic bool substitution.
    """
    data = {"var": True}
    string = "This is a {{var}}"

    assert replace_string_variables(string, data) == "This is a True"


def test_basic_dict_substitution_in_string():
    """
    Test basic dict substitution.
    """
    data = {"var": {"key": "value"}}
    string = "This is a {{var}}"

    assert (
        replace_string_variables(string, data) == "This is a {'key': 'value'}"
    )


def test_basic_list_substitution_in_string():
    """
    Test basic list substitution.
    """
    data = {"var": ["value"]}
    string = "This is a {{var}}"

    assert replace_string_variables(string, data) == "This is a ['value']"


def test_basic_string_substitution_standalone():
    """
    Test basic string substitution.
    """
    data = {"var": "value"}
    string = "{{var}}"

    assert replace_string_variables(string, data) == "value"


def test_basic_int_substitution_standalone():
    """
    Test basic int substitution.
    """
    data = {"var": 1}
    string = "{{var}}"

    assert replace_string_variables(string, data) == 1


def test_basic_float_substitution_standalone():
    """
    Test basic float substitution.
    """
    data = {"var": 1.0}
    string = "{{var}}"

    assert replace_string_variables(string, data) == 1.0


def test_basic_bool_substitution_standalone():
    """
    Test basic bool substitution.
    """
    data = {"var": True}
    string = "{{var}}"

    assert replace_string_variables(string, data) is True


def test_basic_dict_substitution_standalone():
    """
    Test basic dict substitution.
    """
    data = {"var": {"key": "value"}}
    string = "{{var}}"

    assert replace_string_variables(string, data) == {"key": "value"}


def test_basic_list_substitution_standalone():
    """
    Test basic list substitution.
    """
    data = {"var": ["value"]}
    string = "{{var}}"

    assert replace_string_variables(string, data) == ["value"]


def test_basic_list_substitution_last_element_standalone():
    """
    Test basic list substitution.
    """
    data = {"var": ["value", "value2"]}
    string = "{{var[-1]}}"

    assert replace_string_variables(string, data) == "value2"


def test_int_pipe_int_string_substitution():
    """
    Test int pipe int string substitution.
    """
    data = {"var": "1"}
    string = "{{var|int}}"

    assert replace_string_variables(string, data) == 1


def test_int_pipe_float_string_substitution():
    """
    Test int pipe float string substitution.
    """
    data = {"var": "1.0"}
    string = "{{var|int}}"

    with pytest.raises(ValueError) as excinfo:
        replace_string_variables(string, data)

    assert (
        excinfo.value.args[0]
        == "invalid literal for int() with base 10: '1.0'"
    )


def test_int_pipe_bool_string_substitution():
    """
    Test int pipe bool string substitution.
    """
    data = {"var": "True"}
    string = "{{var|int}}"

    with pytest.raises(ValueError) as excinfo:
        replace_string_variables(string, data)

    assert (
        excinfo.value.args[0]
        == "invalid literal for int() with base 10: 'True'"
    )


def test_int_pipe_random_string_substitution():
    """
    Test int pipe random string substitution.
    """
    data = {"var": "random"}
    string = "{{var|int}}"

    with pytest.raises(ValueError) as excinfo:
        replace_string_variables(string, data)

    assert (
        excinfo.value.args[0]
        == "invalid literal for int() with base 10: 'random'"
    )


def test_float_pipe_int_string_substitution():
    """
    Test float pipe int string substitution.
    """
    data = {"var": "1"}
    string = "{{var|float}}"

    assert replace_string_variables(string, data) == 1.0


def test_float_pipe_float_string_substitution():
    """
    Test float pipe float string substitution.
    """
    data = {"var": "1.0"}
    string = "{{var|float}}"

    assert replace_string_variables(string, data) == 1.0


def test_float_pipe_bool_string_substitution():
    """
    Test float pipe bool string substitution.
    """
    data = {"var": "True"}
    string = "{{var|float}}"

    with pytest.raises(ValueError) as excinfo:
        replace_string_variables(string, data)

    assert excinfo.value.args[0] == "could not convert string to float: 'True'"


def test_float_pipe_random_string_substitution():
    """
    Test float pipe random string substitution.
    """
    data = {"var": "random"}
    string = "{{var|float}}"

    with pytest.raises(ValueError) as excinfo:
        replace_string_variables(string, data)

    assert (
        excinfo.value.args[0] == "could not convert string to float: 'random'"
    )


def test_bool_pipe_int_string_substitution():
    """
    Test bool pipe int string substitution.
    """
    data = {"var": "1"}
    string = "{{var|bool}}"

    assert replace_string_variables(string, data) is True


def test_bool_pipe_float_string_substitution():
    """
    Test bool pipe float string substitution.
    """
    data = {"var": "1.0"}
    string = "{{var|bool}}"

    assert replace_string_variables(string, data) is True


def test_bool_pipe_bool_string_substitution():
    """
    Test bool pipe bool string substitution.
    """
    data = {"var": "True"}
    string = "{{var|bool}}"

    assert replace_string_variables(string, data) is True


def test_bool_pipe_random_string_substitution():
    """
    Test bool pipe random string substitution.
    """
    data = {"var": "random"}
    string = "{{var|bool}}"

    assert replace_string_variables(string, data) is True


def test_str_pipe_int_string_substitution():
    """
    Test str pipe int string substitution.
    """
    data = {"var": 1}
    string = "{{var|str}}"

    assert replace_string_variables(string, data) == "1"


def test_str_pipe_float_string_substitution():
    """
    Test str pipe float string substitution.
    """
    data = {"var": 1.0}
    string = "{{var|str}}"

    assert replace_string_variables(string, data) == "1.0"


def test_str_pipe_bool_string_substitution():
    """
    Test str pipe bool string substitution.
    """
    data = {"var": True}
    string = "{{var|str}}"

    assert replace_string_variables(string, data) == "True"


def test_str_pipe_dict_string_substitution():
    """
    Test str pipe dict string substitution.
    """
    data = {"var": {"key": "value"}}
    string = "{{var|str}}"

    assert replace_string_variables(string, data) == "{'key': 'value'}"


def test_str_pipe_list_string_substitution():
    """
    Test str pipe list string substitution.
    """
    data = {"var": ["value"]}
    string = "{{var|str}}"

    assert replace_string_variables(string, data) == "['value']"


def test_round_pipe_int_substitution():
    """
    Test round pipe int string substitution.
    """
    data = {"var": 1.0}
    string = "{{var|round}}"

    assert replace_string_variables(string, data) == 1


def test_round_pipe_float_substitution():
    """
    Test round pipe float string substitution.
    """
    data = {"var": 1.512}
    string = "{{var|round:1}}"

    assert replace_string_variables(string, data) == 1.5


def test_unavailable_pipe_substitution():
    """
    Test round pipe float string substitution.
    """
    data = {"var": 1}
    string = "{{var|unavailable}}"

    with pytest.raises(KeyError) as excinfo:
        replace_string_variables(string, data)

    assert (
        excinfo.value.args[0]
        == "Pipe unavailable not found in available pipes"
    )


def test_wrong_number_of_arguments_pipe_substitution():
    """
    Test round pipe float string substitution.
    """
    data = {"var": 1}
    string = "{{var|round:1:2}}"

    with pytest.raises(TypeError) as excinfo:
        replace_string_variables(string, data)

    assert (
        excinfo.value.args[0] == "round() takes at most 2 arguments (3 given)"
    )


def test_substitute_not_found():
    """
    Test that the function returns None when no substitution is found.
    """
    data = {"var": "value"}
    string = "This is a {{not_found}}"

    with pytest.raises(KeyError) as excinfo:
        replace_string_variables(string, data)

    assert excinfo.value.args[0] == "Key not_found not found in data"


def test_substitute_not_found_in_list():
    """
    Test that the function returns None when no substitution is found.
    """
    data = {"var": ["value"]}
    string = "This is a {{var[1]}}"

    with pytest.raises(IndexError) as excinfo:
        replace_string_variables(string, data)

    assert excinfo.value.args[0] == "Index 1 not found in list data.var"


def test_recursively_substitute():
    """
    Test that the function returns None when no substitution is found.
    """
    data = {"var": "value"}
    call = {"key": "This is a {{var}}"}

    recursively_replace_variables(call, data)
    assert call == {"key": "This is a value"}


def test_recursively_substitute_more_complex():
    """
    Test that the function returns None when no substitution is found.
    """
    data = {"var": "value", "var2": "value2"}
    call = {"key": "This is a {{var}} and {{var2}}"}

    recursively_replace_variables(call, data)
    assert call == {"key": "This is a value and value2"}


def test_recursively_substitute_more_complex_inducing_dict():
    """
    Test that the function returns None when no substitution is found.
    """
    data = {
        "var": "value",
        "var2": "value2",
        "var3": {"key": "This is a {{var}} and {{var2}}"},
    }
    call = {"key": "{{var3}}"}

    recursively_replace_variables(call, data)
    assert call == {"key": {"key": "This is a value and value2"}}


def test_recursively_substitute_more_complex_inducing_list():
    """
    Test that the function returns None when no substitution is found.
    """
    data = {
        "var": "value",
        "var2": "value2",
        "var3": ["This is a {{var}} and {{var2}}"],
    }
    call = {"key": "{{var3}}"}

    recursively_replace_variables(call, data)
    assert call == {"key": ["This is a value and value2"]}


def test_recursively_substitute_more_complex_inducing_list_in_list():
    """
    Test that the function returns None when no substitution is found.
    """
    data = {
        "var": "value",
        "var2": "value2",
        "var3": ["This is a {{var}} and {{var2}}"],
    }
    call = {"key": ["{{var3}}", "{{var3}}"]}

    recursively_replace_variables(call, data)
    assert call == {
        "key": [["This is a value and value2"], ["This is a value and value2"]]
    }
