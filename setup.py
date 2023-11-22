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
    return [
        line.strip()
        for line in read(path).split("\n")
        if not line.startswith(('"', "#", "-", "git+"))
    ]


setup(
    name="test_tool",
    version=read("test_tool", "VERSION"),
    description="Awesome test_tool created by jackovsky8",
    url="https://github.com/jackovsky8/test-tool/",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    author="jackovsky8",
    packages=find_packages(exclude=["tests", ".github"]),
    install_requires=read_requirements("requirements.txt"),
    entry_points={
        "console_scripts": ["test_tool = test_tool.__main__:main"]
    },
    extras_require={"test": read_requirements("requirements-test.txt")},
)
