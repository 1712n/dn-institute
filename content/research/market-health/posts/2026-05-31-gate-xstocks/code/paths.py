"""Where the scripts read trade dumps and write datasets and figures.

Figures go into the post directory beside index.md, datasets into its data/ folder. Every
dump the post's numbers use is committed under data/trades/, with the SOL and LINK controls
as size tables (see build_sizes.py). A dump that is not committed, such as the raw SOL and
LINK months build_sizes.py reads, is downloaded into a temporary directory. Every file,
committed or downloaded, must match its hash: committed files in data/trades/SHA256SUMS,
downloaded ones in data/trades/SHA256SUMS.download.
"""
import hashlib
import os
import tempfile
import urllib.request

CODE = os.path.dirname(os.path.abspath(__file__))
POST = os.path.dirname(CODE)
DATA = os.path.join(POST, "data")
TRADES = os.path.join(DATA, "trades")
CACHE = os.path.join(tempfile.gettempdir(), "gate-xstocks-dumps")
TIMEOUT = 60

SHA256 = {}
for listing in ("SHA256SUMS", "SHA256SUMS.download"):
    with open(os.path.join(TRADES, listing)) as fh:
        SHA256.update({name: digest for digest, name in (line.split() for line in fh if line.strip())})


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def _download(url, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd, part = tempfile.mkstemp(dir=os.path.dirname(path), suffix=".part")
    try:
        with os.fdopen(fd, "wb") as out, urllib.request.urlopen(url, timeout=TIMEOUT) as resp:
            for block in iter(lambda: resp.read(1 << 20), b""):
                out.write(block)
        os.replace(part, path)
    finally:
        if os.path.exists(part):
            os.remove(part)


def dump(name, url=None):
    """Path to the file `name`, such as "gate/HOODX_USDT-202605.csv.gz", checked against its hash."""
    path = os.path.join(TRADES, name)
    if not os.path.exists(path):
        path = os.path.join(CACHE, name)
        if not os.path.exists(path):
            if url is None:
                raise FileNotFoundError(f"{name} is not under data/trades/ and has no download URL")
            _download(url, path)
    if _sha256(path) != SHA256[name]:
        raise ValueError(f"{name} does not match its hash in data/trades")
    return path
