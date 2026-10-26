import unittest
from card import Carte, Paquet
from evaluator_fast import EvaluateurFast
from simulator import Simulateur
from app import app


class TestCarte(unittest.TestCase):
    def test_carte_creation(self):
        c = Carte('A', 'h')
        self.assertEqual(c.valeur, 'A')
        self.assertEqual(c.couleur, 'h')
        self.assertEqual(c.rang, 12)
        self.assertEqual(repr(c), 'Ah')
        self.assertIn('As', str(c))
        self.assertIn('Cœur', str(c))

    def test_carte_invalide(self):
        with self.assertRaises(ValueError):
            Carte('X', 'h')
        with self.assertRaises(ValueError):
            Carte('A', 'z')

    def test_carte_from_str(self):
        c1 = Carte.from_str('Ah')
        self.assertEqual(c1, Carte('A', 'h'))
        
        c2 = Carte.from_str('10s')
        self.assertEqual(c2, Carte('T', 's'))
        
        c3 = Carte('10', 's')
        self.assertEqual(c3, Carte('T', 's'))

        with self.assertRaises(ValueError):
            Carte.from_str('')
        with self.assertRaises(ValueError):
            Carte.from_str('A')
        with self.assertRaises(ValueError):
            Carte.from_str('10z')

    def test_carte_equality_and_hash(self):
        c1 = Carte('A', 'h')
        c2 = Carte.from_str('Ah')
        c3 = Carte('K', 'h')
        
        self.assertEqual(c1, c2)
        self.assertNotEqual(c1, c3)
        self.assertEqual(hash(c1), hash(c2))
        self.assertEqual(len({c1, c2}), 1)
        self.assertIn(c1, [c2])


class TestPaquet(unittest.TestCase):
    def test_paquet_init(self):
        p = Paquet()
        self.assertEqual(len(p.cartes), 52)
        unique_cards = set(p.cartes)
        self.assertEqual(len(unique_cards), 52)

    def test_tirer(self):
        p = Paquet()
        carte = p.tirer()
        self.assertIsInstance(carte, Carte)
        self.assertEqual(len(p.cartes), 51)

    def test_retirer_cartes(self):
        p = Paquet()
        c1 = Carte('A', 's')
        p.retirer_cartes([c1, 'Kh', '10d'])
        self.assertEqual(len(p.cartes), 49)
        self.assertNotIn(c1, p.cartes)
        self.assertNotIn(Carte('K', 'h'), p.cartes)
        self.assertNotIn(Carte('T', 'd'), p.cartes)


class TestEvaluateurFast(unittest.TestCase):
    def parse_cards(self, cards_str):
        return [Carte.from_str(s) for s in cards_str.split()]

    def test_hand_rankings_5_cards(self):
        high_card = self.parse_cards('As Kd Qc Jh 9s')
        one_pair = self.parse_cards('As Ac Kd Qc Jh')
        two_pair = self.parse_cards('As Ac Ks Kc Qh')
        three_kind = self.parse_cards('As Ac Ad Ks Qh')
        straight = self.parse_cards('9s 8c 7d 6h 5s')
        wheel_st8 = self.parse_cards('5s 4c 3d 2h As')
        flush = self.parse_cards('As Js 8s 6s 2s')
        full_house = self.parse_cards('As Ac Ad Ks Kc')
        quads = self.parse_cards('As Ac Ad Ah Ks')
        straight_flush = self.parse_cards('9s 8s 7s 6s 5s')
        royal_flush = self.parse_cards('As Ks Qs Js Ts')

        ranks = [
            high_card, one_pair, two_pair, three_kind, straight,
            flush, full_house, quads, straight_flush, royal_flush
        ]

        scores = [
            (EvaluateurFast.evaluer_5_ints([c.bit_value for c in h])[1] << 24)
            | EvaluateurFast.evaluer_5_ints([c.bit_value for c in h])[0]
            for h in ranks
        ]

        # Verify strictly increasing ranks
        for i in range(len(scores) - 1):
            self.assertGreater(scores[i + 1], scores[i], f"Rank {i+1} not greater than {i}")

    def test_straight_wheel_tie_breaker(self):
        wheel = self.parse_cards('5s 4c 3d 2h As')
        six_high = self.parse_cards('6s 5c 4d 3h 2s')
        s_wheel = (EvaluateurFast.evaluer_5_ints([c.bit_value for c in wheel])[1] << 24) | EvaluateurFast.evaluer_5_ints([c.bit_value for c in wheel])[0]
        s_six = (EvaluateurFast.evaluer_5_ints([c.bit_value for c in six_high])[1] << 24) | EvaluateurFast.evaluer_5_ints([c.bit_value for c in six_high])[0]
        self.assertGreater(s_six, s_wheel)

    def test_full_house_priority(self):
        aces_full = self.parse_cards('As Ac Ad 2s 2c')
        kings_full = self.parse_cards('Ks Kc Kd As Ac')
        s_aces = (EvaluateurFast.evaluer_5_ints([c.bit_value for c in aces_full])[1] << 24) | EvaluateurFast.evaluer_5_ints([c.bit_value for c in aces_full])[0]
        s_kings = (EvaluateurFast.evaluer_5_ints([c.bit_value for c in kings_full])[1] << 24) | EvaluateurFast.evaluer_5_ints([c.bit_value for c in kings_full])[0]
        self.assertGreater(s_aces, s_kings)

    def test_7_cards_evaluation(self):
        # 7 cards with hidden royal flush
        cards = self.parse_cards('As Ks Qs Js Ts 2c 3d')
        res_type, res_score = EvaluateurFast.evaluer_7_cartes(cards)
        self.assertEqual(res_type, 8)  # Straight Flush
        
        # 7 cards with 3 pairs (should pick highest two pair)
        three_pairs = self.parse_cards('As Ac Ks Kc Qs Qc 2d')
        res_type, res_score = EvaluateurFast.evaluer_7_cartes(three_pairs)
        self.assertEqual(res_type, 2)  # Two Pair


class TestSimulateur(unittest.TestCase):
    def test_outs_unpaired_undercards(self):
        hero = [Carte('8', 's'), Carte('7', 'h')]
        board = [Carte('A', 's'), Carte('K', 'd'), Carte('Q', 'c')]
        outs = Simulateur.calculer_outs(hero, board, [])
        # Only 3 eights and 3 sevens should be counted
        self.assertEqual(len(outs), 6)
        out_ranks = {c.valeur for c in outs}
        self.assertEqual(out_ranks, {'8', '7'})

    def test_outs_flush_draw_overcards(self):
        hero = [Carte('A', 'h'), Carte('K', 'h')]
        board = [Carte('2', 'h'), Carte('7', 'h'), Carte('T', 'c')]
        outs = Simulateur.calculer_outs(hero, board, [])
        # 9 hearts + 3 Aces + 3 Kings = 15 outs
        self.assertEqual(len(outs), 15)

    def test_outs_open_ended_straight_draw(self):
        hero = [Carte('9', 's'), Carte('8', 's')]
        board = [Carte('7', 'h'), Carte('6', 'c'), Carte('2', 'd')]
        outs = Simulateur.calculer_outs(hero, board, [])
        # 4 fives + 4 tens + 3 eights + 3 nines = 14 outs
        self.assertEqual(len(outs), 14)

    def test_outs_river_complete(self):
        hero = [Carte('A', 'h'), Carte('K', 'h')]
        board = [Carte('2', 'h'), Carte('7', 'h'), Carte('T', 'c'), Carte('4', 's'), Carte('5', 'd')]
        outs = Simulateur.calculer_outs(hero, board, [])
        self.assertEqual(len(outs), 0)

    def test_texture_analysis(self):
        # Wheel straight draw
        tex1 = Simulateur.analyser_texture([Carte('A', 's'), Carte('2', 'h'), Carte('3', 'c')])
        self.assertIn("Tirage Quinte possible", tex1)

        # Trips on board
        tex2 = Simulateur.analyser_texture([Carte('7', 's'), Carte('7', 'h'), Carte('7', 'c')])
        self.assertIn("Brelan sur le tableau", tex2)
        self.assertNotIn("Paire sur le tableau", tex2)

        # Two pair on board
        tex3 = Simulateur.analyser_texture([Carte('7', 's'), Carte('7', 'h'), Carte('8', 'c'), Carte('8', 'd')])
        self.assertIn("Double Paire sur le tableau", tex3)

        # Monotone river board
        tex4 = Simulateur.analyser_texture([Carte('A', 'h'), Carte('K', 'h'), Carte('Q', 'h'), Carte('J', 'h'), Carte('T', 'h')])
        self.assertIn("Couleur sur le tableau", tex4)
        self.assertIn("Quinte sur le tableau", tex4)

    def test_simuler_monte_carlo(self):
        hero = [Carte('A', 's'), Carte('A', 'h')]
        win, tie, win_dist, abs_dist = Simulateur.simuler(hero, [], ['any'], iterations=1000)
        self.assertGreater(win, 75.0)
        self.assertIsInstance(win_dist, dict)
        self.assertIsInstance(abs_dist, dict)
        self.assertGreater(len(win_dist), 0)

    def test_simuler_deck_exhaustion_safety(self):
        hero = [Carte('A', 's'), Carte('A', 'h')]
        # 30 opponents would exceed 52 cards -> should return safely without crash
        win, tie, win_dist, abs_dist = Simulateur.simuler(hero, [], ['any'] * 30, iterations=10)
        self.assertEqual(win, 0.0)
        self.assertEqual(tie, 0.0)


class TestWebApp(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_simulate_empty_body(self):
        res = self.client.post('/simulate', json={})
        self.assertFalse(res.json['success'])
        self.assertIn("exactement 2 cartes", res.json['error'])

    def test_simulate_duplicate_hand(self):
        res = self.client.post('/simulate', json={'ma_main': ['Ah', 'Ah']})
        self.assertFalse(res.json['success'])
        self.assertIn("double", res.json['error'])

    def test_simulate_duplicate_board(self):
        res = self.client.post('/simulate', json={'ma_main': ['Ah', 'Kd'], 'tableau': ['Ah', '2c', '3d']})
        self.assertFalse(res.json['success'])
        self.assertIn("double", res.json['error'])

    def test_simulate_invalid_board_size(self):
        res = self.client.post('/simulate', json={'ma_main': ['Ah', 'Kd'], 'tableau': ['2c', '3d']})
        self.assertFalse(res.json['success'])
        self.assertIn("0 (Pré-flop), 3 (Flop)", res.json['error'])

    def test_simulate_10_notation_success(self):
        res = self.client.post('/simulate', json={
            'ma_main': ['10h', 'As'],
            'tableau': ['10s', 'Kd', '2c'],
            'profiles': ['any']
        })
        self.assertTrue(res.json['success'])
        self.assertGreater(res.json['win'], 0)
        self.assertIn('outs', res.json)
        self.assertIn('mains_gagnantes', res.json)
        self.assertIn('mains_absolues', res.json)


if __name__ == '__main__':
    unittest.main()
