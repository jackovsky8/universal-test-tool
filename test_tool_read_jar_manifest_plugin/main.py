from logging import debug, error, info
from pathlib import Path
from typing import Any, Dict, List, TypedDict, Optional
from zipfile import ZipFile


class SaveValue(TypedDict):
    name: str
    key: Optional[str]

class ReadJarManifestCall(TypedDict):
    jar_path: Path
    manifest_path: str
    save: List[SaveValue]

default_read_jar_manifest_call: ReadJarManifestCall = {
    'jar_path': '${PATH_JAR_FILE}',
    'manifest_path': 'META-INF/MANIFEST.MF',
    'save': []
}

def make_read_jar_manifest_call(call: ReadJarManifestCall, data: Dict[str, Any]) -> None:
    info(f'Reading manifest from {call["jar_path"]}:{call["manifest_path"]}')

    with ZipFile(call['jar_path'], 'r') as zip_file:
        with zip_file.open(call['manifest_path']) as manifest:
            manifest_content = manifest.read().decode('utf-8')

    # Parse specific attributes from the manifest
    # Every line is a key-value pair
    manifest_lines = manifest_content.split('\r\n')
    manifest: Dict[str, str] = {}
    for line in manifest_lines:
        if ': ' in line:
            key, value = line.split(': ', 1)
            manifest[key] = value

    info(f'Got manifest:\n{manifest}')

    # Save specific attributes from the manifest
    for save in call['save']:
        if save['key'] in manifest:
            data[save['name']] = manifest[save['key']]

            debug(f'Saving {save["name"]}={data[save["name"]]}')
        else:
            error(f'No value for {save["name"]}')

def augment_read_jar_manifest_call(call: ReadJarManifestCall, data: Dict, path: Path) -> None:
    if call['jar_path'] is not None:
        call['jar_path'] = Path(call['jar_path'])

    if not call['jar_path'].is_absolute():
        call['jar_path'] = path.joinpath(call['jar_path'])
                     
def main() -> None:
    print('test-tool-read-jar-manifest-plugin')