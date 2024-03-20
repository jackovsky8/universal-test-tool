"""
Module for reading a JAR manifest file.
"""
from logging import debug, error, info
from pathlib import Path
from typing import Any, Dict, List, Optional, TypedDict
from zipfile import ZipFile


class SaveValue(TypedDict):
    """
    This class represents a save value.
    """

    name: str
    key: Optional[str]


class ReadJarManifestCall(TypedDict):
    """
    This class represents a read JAR manifest call.
    """

    jar_path: Path
    manifest_path: str
    save: List[SaveValue]


default_read_jar_manifest_call: ReadJarManifestCall = {
    "jar_path": "{{PATH_JAR_FILE}}",  # type: ignore
    "manifest_path": "META-INF/MANIFEST.MF",
    "save": [],
}


def make_read_jar_manifest_call(
    call: ReadJarManifestCall, data: Dict[str, Any]
) -> None:
    """
    This function makes the call to read the JAR manifest.

    Parameters
    ----------
    call : ReadJarManifestCall
        The call to make.
    data : Dict[str, Any]
        The data from the test tool.
    """
    info(f'Reading manifest from {call["jar_path"]}:{call["manifest_path"]}')

    with ZipFile(call["jar_path"], "r") as zip_file:
        with zip_file.open(call["manifest_path"]) as f:
            manifest_content: str = f.read().decode("utf-8")

    # Parse specific attributes from the manifest
    # Every line is a key-value pair
    manifest_lines: List[str] = manifest_content.split("\r\n")
    manifest: Dict[str, str] = {}
    for line in manifest_lines:
        if ": " in line:
            key, value = line.split(": ", 1)
            if isinstance(key, str) and isinstance(value, str):
                manifest[key] = value

    info(f"Got manifest:\n{manifest}")

    # Save specific attributes from the manifest
    for save in call["save"]:
        if save["key"] in manifest:
            data[save["name"]] = manifest[save["key"]]

            debug(f'Saving {save["name"]}={data[save["name"]]}')
        else:
            error(f'No value for {save["name"]}')


def augment_read_jar_manifest_call(
    call: ReadJarManifestCall,
    data: Dict,
    path: Path,  # pylint: disable=unused-argument
) -> None:
    """
    This function augments the call with the absolute path to the JAR file.

    Parameters
    ----------
    call : ReadJarManifestCall
        The call to augment.
    data : Dict
        The data from the test tool.
    path : Path
        The path of the test tool.
    """
    if call["jar_path"] is None:
        raise ValueError("jar_path is required")
    else:
        call["jar_path"] = Path(call["jar_path"])
        if not call["jar_path"].is_absolute():
            call["jar_path"] = path.joinpath(call["jar_path"])


def main() -> None:
    """
    This is the main function of the plugin.
    """
    print("test-tool-read-jar-manifest-plugin")
