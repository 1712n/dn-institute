"""Synthetic fixtures test mechanics only. They are not investigation evidence."""
import json
import unittest
from collect import START, END, check_row, collect_market


def row(timestamp=START):
    return dict(proxy_wallet='0xtest', condition_id='0xmarket', token_id='1',
                side='BUY', size=10, price=.2, timestamp=timestamp,
                outcome='Yes', transaction_hash='0xtransaction')


class CollectorTests(unittest.TestCase):
    def test_date_boundaries(self):
        self.assertTrue(check_row(row(START), '0xmarket'))
        self.assertTrue(check_row(row(END-1), '0xmarket'))
        self.assertFalse(check_row(row(START-1), '0xmarket'))
        self.assertFalse(check_row(row(END), '0xmarket'))

    def test_full_cursor_and_preserved_fills(self):
        pages = iter([
            {'data': [row(END), row()], 'pagination': {'next_cursor': 'abc'}},
            {'data': [row()], 'pagination': {'next_cursor': None}}])
        urls = []
        def fetch(url):
            urls.append(url)
            data = next(pages)
            return data, json.dumps(data).encode()
        rows, count = collect_market('0xmarket', fetch, lambda *args: None, 3)
        self.assertEqual((len(rows), count), (2, 2))
        self.assertIn('cursor=abc', urls[1])
        self.assertIn('taker_only=false', urls[1])

    def test_incomplete_pagination_fails(self):
        payload = {'data': [row()], 'pagination': {'next_cursor': 'same'}}
        with self.assertRaises(ValueError):
            collect_market('0xmarket', lambda _: (payload, b'{}'), lambda *a: None, 5)
        with self.assertRaises(RuntimeError):
            collect_market('0xmarket', lambda _: (payload, b'{}'), lambda *a: None, 1)

    def test_missing_cursor_is_not_a_terminal_page(self):
        for pagination in [{}, {'has_more': False}, {'has_more': True}]:
            with self.subTest(pagination=pagination):
                payload = {'data': [row()], 'pagination': pagination}
                with self.assertRaisesRegex(ValueError, 'Missing next_cursor'):
                    collect_market('0xmarket', lambda _: (payload, b'{}'), lambda *a: None, 2)

    def test_wrong_market_and_invalid_price_fail(self):
        with self.assertRaises(ValueError):
            check_row(row(), 'other')
        invalid = row(); invalid['price'] = float('nan')
        with self.assertRaises(ValueError):
            check_row(invalid, '0xmarket')


if __name__ == '__main__':
    unittest.main()
