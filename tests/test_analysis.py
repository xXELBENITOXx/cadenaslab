import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from analysis import analyze, kmp_search, boyer_moore_horspool, euclid, modular, sieve

class AnalysisTests(unittest.TestCase):
    def test_identical(self):
        self.assertEqual(analyze('El análisis de cadenas permite comparar textos y palabras.',
                                 'El análisis de cadenas permite comparar textos y palabras.')['score'], 100.0)
    def test_disjoint(self):
        self.assertEqual(analyze('manzana pera plátano cereza naranja sandía',
                                 'motor puerta ventana rueda coche vehículo')['score'], 0.0)
    def test_accents_case(self):
        self.assertEqual(analyze('ÁRBOL árbol tecnología datos sistema', 'arbol ÁRBoL TECNOLOGÍA datos SISTEMA')['score'], 100.0)
    def test_partial_highlights(self):
        r = analyze('Uno dos tres cuatro cinco seis siete', 'Otro dos tres cuatro cinco seis diez')
        self.assertTrue(0 < r['score'] < 100)
        self.assertTrue(r['ranges_a'] and r['fragments'])
    def test_too_short(self):
        self.assertEqual(analyze('uno dos', 'uno dos')['score'], 0)
    def test_oversize(self):
        with self.assertRaises(ValueError): analyze('a'*20001,'otro')
    def test_kmp(self):
        self.assertEqual(kmp_search('ABABCABABC', 'ABC')['positions'], [2, 7])
    def test_boyer(self):
        self.assertEqual(boyer_moore_horspool('ABABCABABC', 'ABC')['positions'], [2, 7])
    def test_euclid(self):
        self.assertEqual(euclid(48, 18)['gcd'], 6)
    def test_modular(self):
        self.assertEqual(modular(3, 7, 11)['result'], 9)
    def test_sieve(self):
        self.assertEqual(sieve(20)['primes'], [2,3,5,7,11,13,17,19])

if __name__ == '__main__': unittest.main()
