import unittest
from analyze import CUTOFF, DAY, rank


def trade(wallet='a',side='BUY',outcome='Yes',size=10000,price=.1,timestamp=CUTOFF-1):
    return dict(proxy_wallet=wallet,side=side,outcome=outcome,size=size,price=price,timestamp=timestamp)


class RankingTests(unittest.TestCase):
    def test_cutoff_is_exclusive(self):
        r=rank([trade(timestamp=CUTOFF)])[0]
        self.assertFalse(r['eligible']); self.assertEqual(r['buy_yes_notional'],0)

    def test_future_data_cannot_change_existing_score(self):
        base=rank([trade()])[0]
        future=rank([trade(),trade(size=1e9,timestamp=CUTOFF+1)])[0]
        self.assertEqual(base['score'],future['score'])

    def test_hedged_pair_is_ineligible(self):
        r=rank([trade(),trade(outcome='No',price=.9)])[0]
        self.assertFalse(r['eligible']); self.assertEqual(r['net_directional_share_flow'],0)

    def test_round_trip_is_ineligible(self):
        self.assertFalse(rank([trade(),trade(side='SELL')])[0]['eligible'])

    def test_baseline_purchase_reduces_burst(self):
        base=rank([trade()])[0]
        active=rank([trade(),trade(timestamp=CUTOFF-2*DAY,size=1e6)])[0]
        self.assertLess(active['burst'],base['burst'])

    def test_trade_splitting_does_not_change_score(self):
        a=rank([trade()])[0]; b=rank([trade(size=5000),trade(size=5000)])[0]
        self.assertEqual(a['score'],b['score'])

    def test_small_purchases_do_not_qualify(self):
        self.assertFalse(rank([trade(size=4990)])[0]['eligible'])
        self.assertTrue(rank([trade(size=5000)])[0]['eligible'])

    def test_equal_scores_share_rank(self):
        r=rank([trade(wallet='b'),trade(wallet='a')])
        self.assertEqual([x['rank'] for x in r],[1,1])
        self.assertEqual([x['wallet'] for x in r],['a','b'])

    def test_window_start_is_inclusive(self):
        self.assertTrue(rank([trade(timestamp=CUTOFF-12*3600)],window_hours=12)[0]['eligible'])
        self.assertFalse(rank([trade(timestamp=CUTOFF-12*3600-1)],window_hours=12)[0]['eligible'])

    def test_baseline_moves_with_window(self):
        rows=[trade(),trade(timestamp=CUTOFF-18*3600,size=20000)]
        short=rank(rows,window_hours=12)[0]
        long=rank(rows,window_hours=24)[0]
        self.assertEqual(short['baseline_7d_buy_yes_notional'],2000)
        self.assertEqual(long['baseline_7d_buy_yes_notional'],0)
        self.assertEqual(long['buy_yes_notional'],3000)


if __name__=='__main__':
    unittest.main()
