"""Restore byte-identical history CSVs from the GitHub submission's CSV parts."""
import hashlib
import json
from pathlib import Path


def restore_table(root, destination):
    root = Path(root)
    destination = Path(destination)
    manifest = json.loads((root / 'data/prepared/csv_parts_manifest.json').read_text(encoding='utf-8'))
    entry = manifest[destination.relative_to(root).as_posix()]
    temporary = destination.with_suffix('.csv.tmp')
    digest = hashlib.sha256()
    with temporary.open('wb') as output:
        header = None
        for index, part in enumerate(entry['parts']):
            content = (root / part['path']).read_bytes()
            if hashlib.sha256(content).hexdigest() != part['sha256']:
                raise ValueError(f"CSV part checksum mismatch: {part['path']}")
            first_line, rest = content.split(b'\n', 1)
            if header is None:
                header = first_line
            elif header != first_line:
                raise ValueError(f"CSV part header mismatch: {part['path']}")
            payload = content if index == 0 else rest
            output.write(payload)
            digest.update(payload)
    if temporary.stat().st_size != entry['bytes'] or digest.hexdigest() != entry['sha256']:
        raise ValueError(f'Original CSV checksum mismatch: {destination.name}')
    temporary.replace(destination)
    return destination


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / 'data/prepared/csv_parts_manifest.json').read_text(encoding='utf-8'))
    for relative in manifest:
        destination = root / relative
        restore_table(root, destination)
        print(f'Restored and verified: {relative}')
