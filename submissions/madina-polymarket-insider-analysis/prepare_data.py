"""Restore the public-data snapshot from verified archive parts (Python 3.10+)."""
import hashlib
import io
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main():
    manifest = json.loads((ROOT / 'snapshot' / 'manifest.json').read_text())
    chunks = []
    for item in manifest['parts']:
        chunk = (ROOT / 'snapshot' / item['path']).read_bytes()
        if len(chunk) != item['size_bytes'] or hashlib.sha256(chunk).hexdigest() != item['sha256']:
            raise ValueError('Snapshot part failed verification: ' + item['path'])
        chunks.append(chunk)
    archive = b''.join(chunks)
    if hashlib.sha256(archive).hexdigest() != manifest['archive_sha256']:
        raise ValueError('Snapshot archive failed verification')
    with zipfile.ZipFile(io.BytesIO(archive)) as source:
        entries = source.infolist()
        for item in entries:
            target = (ROOT / item.filename).resolve()
            if not target.is_relative_to(ROOT / 'data'):
                raise ValueError('Unexpected archive path: ' + item.filename)
            if target.exists() and not item.is_dir():
                if target.read_bytes() != source.read(item):
                    raise ValueError('Existing data differs; use a fresh checkout: ' + item.filename)
        source.extractall(ROOT)
    print('Public-data snapshot restored and verified.')


if __name__ == '__main__':
    main()
