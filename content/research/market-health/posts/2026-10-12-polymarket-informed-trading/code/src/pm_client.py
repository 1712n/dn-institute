import time
import requests
import config


class PolymarketClient:
    def __init__(self):
        self.s = requests.Session()
        self.s.headers.update({"User-Agent": config.USER_AGENT, "Accept": "application/json"})

    def _get(self, url, params=None):
        last = None
        for i in range(config.MAX_RETRIES):
            try:
                r = self.s.get(url, params=params, timeout=40)
                if r.status_code == 200:
                    time.sleep(config.REQUEST_PAUSE)
                    return r.json()
                if r.status_code in (429, 500, 502, 503):
                    time.sleep(1.5 * (i + 1))
                    continue
                if r.status_code in (400, 404, 422):
                    return None
                r.raise_for_status()
            except requests.RequestException as e:
                last = e
                time.sleep(1.0 * (i + 1))
        if last:
            raise last
        return None

    def markets_page(self, tag_id, offset, limit=100, closed=True,
                     end_min=None, end_max=None):
        p = {"tag_id": tag_id, "closed": str(closed).lower(),
             "limit": limit, "offset": offset,
             "order": "volumeNum", "ascending": "false"}
        if end_min:
            p["end_date_min"] = end_min
        if end_max:
            p["end_date_max"] = end_max
        return self._get(f"{config.GAMMA}/markets", p)

    def trades_page(self, condition_id, offset, limit=None):
        limit = limit or config.TRADES_PAGE
        return self._get(f"{config.DATA_API}/trades",
                         {"market": condition_id, "limit": limit, "offset": offset})

    def positions(self, wallet, limit=500):
        return self._get(f"{config.DATA_API}/positions",
                         {"user": wallet, "limit": limit})

    def activity(self, wallet, limit=500):
        return self._get(f"{config.DATA_API}/activity",
                         {"user": wallet, "limit": limit})
