"""Python setup.py for test_tool package"""
import io
import os
from setuptools import find_packages, setup


def read(*paths, **kwargs):
    """Read the contents of a text file safely.
    >>> read("test_tool", "VERSION")
    '0.1.0'
    >>> read("README.md")
    ...
    """

    content = ""
    with io.open(
        os.path.join(os.path.dirname(__file__), *paths),
        encoding=kwargs.get("encoding", "utf8"),
    ) as open_file:
        content = open_file.read().strip()
    return content


def read_requirements(path):
    """
    Read a requirements file.

    Parameters:
    ----------
    path: str
        The path to the requirements file
    """
    return [
        line.strip()
        for line in read(path).split("\n")
        if not line.startswith(('"', "#", "-", "git+"))
    ]


setup(
    name="universal-test-tool",
    version=read("test_tool", "VERSION"),
    description="Awesome universal-test-tool to make tests configurable with a yaml file.",
    url="https://github.com/jackovsky8/universal-test-tool/",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    author="jackovsky8",
    packages=find_packages(exclude=["tests", ".github"]),
    install_requires=read_requirements("requirements.txt"),
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "test-tool = test_tool.__main__:main",
            "test-tool-assert-plugin = test_tool_assert_plugin.__main__:main",
            "test-tool-copy-files-ssh-plugin = test_tool_copy_files_ssh_plugin.__main__:main",
            "test-tool-jdbc-sql-plugin = test_tool_jdbc_sql_plugin.__main__:main",
            "test-tool-python-plugin = test_tool_python_plugin.__main__:main",
            "test-tool-read-jar-manifest-plugin = test_tool_read_jar_manifest_plugin.__main__:main",
            "test-tool-rest-plugin = test_tool_rest_plugin.__main__:main",
            "test-tool-run-process-plugin = test_tool_run_process_plugin.__main__:main",
            "test-tool-selenium-plugin = test_tool_selenium_plugin.__main__:main",
            "test-tool-sql-plus-plugin = test_tool_sql_plus_plugin.__main__:main",
            "test-tool-ssh-cmd-plugin = test_tool_ssh_cmd_plugin.__main__:main",
            "test-tool-timing-plugin = test_tool_timing_plugin.__main__:main",
        ]
    },
    extras_require={"test": read_requirements("requirements-test.txt")},
)
