#!/usr/bin/env python3
"""Public Polymarket evidence collector. Python 3.10+, standard library only.

No wallet connection, credentials, trading, or third-party dependencies.
API contract checked against Polymarket's documentation on 2026-10-07.
"""
import argparse
import csv
import datetime as dt
import hashlib
import json
import pathlib
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile

START = int(dt.datetime(2025, 11, 1, tzinfo=dt.timezone.utc).timestamp())
# Include the entire May 1 UTC day; disclose this interpretation in the report.
END = int(dt.datetime(2026, 5, 2, tzinfo=dt.timezone.utc).timestamp())
FIELDS = ['proxy_wallet', 'condition_id', 'token_id', 'side', 'size', 'price',
          'timestamp', 'outcome', 'transaction_hash', 'title', 'slug']


def get_json(url):
    for attempt in range(4):
        try:
            request = urllib.request.Request(url, headers={
                'User-Agent': 'PolymarketResearchCollector/0.1',
                'Accept': 'application/json'})
            with urllib.request.urlopen(request, timeout=30) as response:
                raw = response.read()
            return json.loads(raw), raw
        except urllib.error.HTTPError as error:
            if error.code not in (429, 500, 502, 503, 504) or attempt == 3:
                raise
            time.sleep(2 ** attempt)
        except (urllib.error.URLError, TimeoutError):
            if attempt == 3:
                raise
            time.sleep(2 ** attempt)


def check_row(row, condition):
    if row.get('condition_id', '').lower() != condition.lower():
        raise ValueError('API returned a row from another market')
    for field in FIELDS[:9]:
        if field not in row:
            raise ValueError('Missing trade field: ' + field)
    price, size = float(row['price']), float(row['size'])
    if not (0 <= price <= 1 and 0 < size < float('inf')):
        raise ValueError('Invalid trade price/size')
    if row['side'] not in ('BUY', 'SELL'):
        raise ValueError('Unknown trade side')
    return START <= int(row['timestamp']) < END


def collect_market(condition, fetch, save, max_pages):
    """Preserve maker and taker rows; do not deduplicate distinct fills by tx hash."""
    rows, seen_cursors = [], set()
    params = {'condition': condition, 'limit': 1000, 'taker_only': 'false'}
    for page in range(max_pages):
        url = 'https://data-api.polymarket.com/v2/trades?' + urllib.parse.urlencode(params)
        payload, raw = fetch(url)
        save(page, url, raw)
        batch = payload.get('data')
        pagination = payload.get('pagination')
        if not isinstance(batch, list) or not isinstance(pagination, dict):
            raise ValueError('Unexpected response envelope')
        rows.extend(row for row in batch if check_row(row, condition))
        if 'next_cursor' not in pagination:
            raise ValueError('Missing next_cursor in pagination')
        cursor = pagination['next_cursor']
        if cursor is None:
            if pagination.get('has_more') is True:
                raise ValueError('has_more without a cursor')
            return rows, page + 1
        if not batch or cursor in seen_cursors:
            raise ValueError('Empty continuing page or repeated cursor')
        seen_cursors.add(cursor)
        params = {'condition': condition, 'cursor': cursor, 'taker_only': 'false'}
        # Market feeds ignore start/end: exhaust the cursor, then filter locally.
    raise RuntimeError('Page budget exceeded; collection is incomplete')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--event', action='append', help='Polymarket event slug; repeatable')
    parser.add_argument('--max-pages', type=int, default=2000)
    parser.add_argument('--out', default='evidence')
    args = parser.parse_args()
    if args.max_pages < 1:
        parser.error('--max-pages must be positive')
    # A documented event in the challenge window, used as a retrieval pilot.
    # Whether it supports pre-news analysis must be established from its metadata.
    events = args.event or ['maduro-in-us-custody-by-january-31']
    root = pathlib.Path(args.out)
    root.mkdir(parents=True, exist_ok=False)
    (root / 'raw').mkdir()
    manifest = {'status': 'incomplete', 'retrieved_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
                'window_start_inclusive': START, 'window_end_exclusive': END,
                'event_slugs': events, 'sources': [], 'markets': [],
                'notes': ['API exhaustion is not proof of complete blockchain history.',
                          'Maker/taker rows may describe opposite sides of the same fill.',
                          'Repeated-looking fills are preserved, not silently discarded.']}

    def save(name, url, raw):
        path = root / 'raw' / name
        path.write_bytes(raw)
        manifest['sources'].append({'path': str(path.relative_to(root)), 'url': url,
                                    'sha256': hashlib.sha256(raw).hexdigest(),
                                    'retrieved_at_utc': dt.datetime.now(dt.timezone.utc).isoformat()})

    all_rows, markets = [], {}
    try:
        for index, slug in enumerate(events):
            url = 'https://gamma-api.polymarket.com/events?'+urllib.parse.urlencode({'slug': slug})
            data, raw = get_json(url)
            save('event_%03d.json' % index, url, raw)
            if not isinstance(data, list) or len(data) != 1 or data[0].get('slug') != slug:
                raise ValueError('Event lookup did not return the requested unique event: ' + slug)
            for market in data[0].get('markets', []):
                if market.get('conditionId'):
                    markets[market['conditionId']] = market
        if not markets:
            raise ValueError('No markets in the selected events')
        for index, (condition, market) in enumerate(markets.items()):
            print('Collecting:', market.get('question', condition), flush=True)
            rows, pages = collect_market(condition, get_json,
                lambda page, url, raw: save('market_%03d_page_%05d.json' % (index, page), url, raw),
                args.max_pages)
            all_rows.extend(rows)
            manifest['markets'].append({'condition_id': condition,
                'question': market.get('question'), 'created_at': market.get('createdAt'),
                'closed': market.get('closed'), 'end_date': market.get('endDate'),
                'pages': pages, 'rows_in_window': len(rows), 'cursor_exhausted': True})
        with (root / 'trades.csv').open('w', newline='', encoding='utf-8') as output:
            writer = csv.DictWriter(output, fieldnames=FIELDS, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(all_rows)
        manifest['status'] = 'collected' if all_rows else 'empty_window'
        manifest['rows_in_window'] = len(all_rows)
    except Exception as error:
        manifest['error'] = type(error).__name__ + ': ' + str(error)
        raise
    finally:
        (root / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
        with zipfile.ZipFile(str(root) + '.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(root.rglob('*')):
                if path.is_file():
                    archive.write(path, path.relative_to(root))
    print('Saved:', str(root) + '.zip', 'Rows:', len(all_rows))
    if not all_rows:
        raise SystemExit('No in-window trades; this is not a usable findings dataset.')


if __name__ == '__main__':
    main()
