import os
import time
import urllib.request
import urllib.parse
import json

BASE = "https://api.etherscan.io/v2/api"
USDC_E = "0x2791bca1f2de4661ed88a30c99a7a9449aa84174"
CHAIN = 137


def _get(params):
    params = {**params, "chainid": CHAIN, "apikey": os.environ.get("ETHERSCAN_KEY", "")}
    url = BASE + "?" + urllib.parse.urlencode(params)
    for i in range(4):
        try:
            r = urllib.request.urlopen(
                urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=30)
            d = json.loads(r.read())
            time.sleep(0.25)
            if isinstance(d.get("result"), list):
                return d["result"]
            if d.get("status") == "0" and "rate limit" in str(d.get("result", "")).lower():
                time.sleep(1.2)
                continue
            return []
        except Exception:
            time.sleep(0.8)
    return []


def wallet_profile(wallet):
    w = wallet.lower()
    usdc = _get({"module": "account", "action": "tokentx",
                 "contractaddress": USDC_E, "address": w, "sort": "asc"})
    native = _get({"module": "account", "action": "txlist", "address": w, "sort": "asc"})

    usdc_in = [t for t in usdc if t.get("to", "").lower() == w]
    native_in = [t for t in native if t.get("to", "").lower() == w and int(t.get("value", 0)) > 0]

    usdc_funders = {}
    for t in usdc_in:
        f = t.get("from", "").lower()
        usdc_funders[f] = usdc_funders.get(f, 0) + int(t.get("value", 0)) / 1e6
    native_funders = sorted({t.get("from", "").lower() for t in native_in})

    first_ts = None
    if native:
        first_ts = int(native[0].get("timeStamp", 0))
    elif usdc_in:
        first_ts = int(usdc_in[0].get("timeStamp", 0))

    return {
        "wallet": w,
        "first_ts": first_ts,
        "n_usdc_in": len(usdc_in),
        "first_usdc_funder": usdc_in[0].get("from", "").lower() if usdc_in else None,
        "usdc_funders": usdc_funders,
        "first_native_funder": native_in[0].get("from", "").lower() if native_in else None,
        "native_funders": native_funders,
        "n_native_tx": len(native),
    }
