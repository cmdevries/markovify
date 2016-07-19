#!/usr/bin/env python
import markovify
import requests
import unittest

class TestTextParser(unittest.TestCase):
    def parse(self, html, expected):
        parser = markovify.Text()
        parser.feed(html)
        self.assertEqual(parser.text(), expected)

    def test_empty(self):
        self.parse('<html><p></p></html>', '')
    
    def test_one_paragraph(self):
        # The parser always prepends a space to ensure words are space separated
        self.parse('<html><p>Andrei Andreevich Markov was a Russian Mathematician</p></html>',
                   ' Andrei Andreevich Markov was a Russian Mathematician')

    def test_two_paragraph(self):
        # It is assumed that words do not span across multiple p tags
        self.parse('<html><p>Math</p><p>ematician</p></html>', ' Math ematician')
    
    def test_nested_paragraph(self):
        # It is assumed that words do not span across multiple p tags
        self.parse('<html><p>Math<p>ematician</p></p></html>', ' Math ematician')
    
    def test_tree(self):
        # Depth first traversal
        self.parse('<html><p>a<p>b<p>c</p><p>d<p>e</p></p></p><p>f</p></p></html>',
                   ' a b c d e f')

class TestFetchText(unittest.TestCase):
    def test_fetch_text(self):
        # Monkey patch requests to mock get(url) to reutrn fixed HTML
        original = requests.get
        class Response:
            def __init__(self):
                self.text = '<html><p>a<p>b<p>c</p><p>d<p>e</p></p></p><p>f</p></p></html>'
                self.url = 'http://www.markovchain.com'
        requests.get = lambda x: Response()
        self.assertTrue(markovify.fetch_text('dummy'), ' a b c d e f')
        requests.get = original

class TestValidBigram(unittest.TestCase):
    def test_valid(self):
        self.assertTrue(markovify.valid_bigram('markov', 'chain'))
        self.assertTrue(markovify.valid_bigram('markov', 'a'))
        self.assertTrue(markovify.valid_bigram('a', 'chain'))

    def test_both_a(self):
        self.assertFalse(markovify.valid_bigram('a', 'a'))

    def test_empty(self):
        self.assertFalse(markovify.valid_bigram('', ''))
        self.assertFalse(markovify.valid_bigram('markov', ''))
        self.assertFalse(markovify.valid_bigram('', 'chain'))

    def test_period(self):
        self.assertFalse(markovify.valid_bigram('.', '.'))
        self.assertFalse(markovify.valid_bigram('.', ''))
        self.assertFalse(markovify.valid_bigram('', '.'))
        self.assertFalse(markovify.valid_bigram('M.', 'U.'))
        self.assertFalse(markovify.valid_bigram('', '...'))
        self.assertFalse(markovify.valid_bigram('....', '...'))
        self.assertFalse(markovify.valid_bigram('markov', '..'))
        self.assertFalse(markovify.valid_bigram('.', 'chain'))
        self.assertTrue(markovify.valid_bigram('markov.', 'chain.'))
        self.assertTrue(markovify.valid_bigram('..markov.', 'chain...'))
        self.assertTrue(markovify.valid_bigram('markov.chain..', '..mark.c.'))

class TestCountBigram(unittest.TestCase):
    def test_count_bigram(self):
        bigrams = {}
        markovify.count_bigram(bigrams, 'markov', 'chain')
        self.assertEqual(bigrams['markov']['chain'], 1)
        markovify.count_bigram(bigrams, 'markov', 'chain')
        self.assertEqual(bigrams['markov']['chain'], 2)
        markovify.count_bigram(bigrams, 'markov', 'chain')
        markovify.count_bigram(bigrams, 'markov', 'chain')
        self.assertEqual(bigrams['markov']['chain'], 4)
        markovify.count_bigram(bigrams, 'markov', 'tree')
        markovify.count_bigram(bigrams, 'markov', 'graph')
        markovify.count_bigram(bigrams, 'markov', 'random')
        markovify.count_bigram(bigrams, 'markov', 'graph')
        markovify.count_bigram(bigrams, 'random', 'field')
        markovify.count_bigram(bigrams, 'random', 'field')
        self.assertEqual(bigrams['markov']['tree'], 1)
        self.assertEqual(bigrams['markov']['graph'], 2)
        self.assertEqual(bigrams['markov']['random'], 1)
        self.assertEqual(bigrams['random']['field'], 2)
        self.assertEqual(bigrams['markov']['chain'], 4)

class TestCleanWord(unittest.TestCase):
    def test_unmodified(self):
        self.assertEqual(markovify.clean_word(''), '')
        self.assertEqual(markovify.clean_word('a'), 'a')
        self.assertEqual(markovify.clean_word('Markov'), 'Markov')

    def test_ends_with_period(self):
        self.assertEqual(markovify.clean_word('Markov.'), 'Markov.')
        self.assertEqual(markovify.clean_word('.Markov.'), 'Markov.')
        self.assertEqual(markovify.clean_word('..Markov.'), 'Markov.')
        self.assertEqual(markovify.clean_word('.Mar.kov.'), 'Mar.kov.')
        self.assertEqual(markovify.clean_word('.Mar.kov..'), 'Mar.kov.')
        self.assertEqual(markovify.clean_word('..Mar.kov.'), 'Mar.kov.')
        self.assertEqual(markovify.clean_word('..Mar.kov..'), 'Mar.kov.')

    def test_hyphenated(self):
        self.assertEqual(markovify.clean_word('markov-chain'), 'markov-chain')
        self.assertEqual(markovify.clean_word('-markov-chain'), 'markov-chain')
        self.assertEqual(markovify.clean_word('-markov-chain-'), 'markov-chain')
        self.assertEqual(markovify.clean_word('markov-chain-'), 'markov-chain')
        self.assertEqual(markovify.clean_word('markov-chain--'), 'markov-chain')

    def test_apostrophe(self):
        self.assertEqual(markovify.clean_word("markov's"), "markov's")
        self.assertEqual(markovify.clean_word("'markov's"), "markov's")
        self.assertEqual(markovify.clean_word("'markov's'"), "markov's")
        self.assertEqual(markovify.clean_word("markov's'"), "markov's")

    def test_all_together(self):
        self.assertEqual(markovify.clean_word("ma.rk-ov's"), "ma.rk-ov's")
        self.assertEqual(markovify.clean_word("'-..-'ma.rk-ov's"), "ma.rk-ov's")
        self.assertEqual(markovify.clean_word("'-..-'ma.rk-ov's'..-"), "ma.rk-ov's")

class TestMerge(unittest.TestCase):
    def test_both_nonempty(self):
        bigrams = {'markov': {'chain': 1336}, 'chain': {'mal': 31335}}
        bigrams_new = {'markov': {'chain' : 1}, 'chain': {'mal': 2}}
        markovify.merge(bigrams, bigrams_new)
        self.assertEqual(bigrams['markov']['chain'], 1337)
        self.assertEqual(bigrams['chain']['mal'], 31337)

    def test_left_empty(self):
        bigrams = {}
        bigrams_new = {'markov': {'chain' : 1}, 'chain': {'mal': 2}}
        markovify.merge(bigrams, bigrams_new)
        self.assertEqual(bigrams['markov']['chain'], 1)
        self.assertEqual(bigrams['chain']['mal'], 2)

    def test_right_empty(self):
        bigrams = {'markov': {'chain' : 1}, 'chain': {'mal': 2}}
        bigrams_new = {}
        markovify.merge(bigrams, bigrams_new)
        self.assertEqual(bigrams['markov']['chain'], 1)
        self.assertEqual(bigrams['chain']['mal'], 2)

    def test_both_empty(self):
        bigrams = {}
        bigrams_new = {}
        markovify.merge(bigrams, bigrams_new)
        self.assertEqual(bigrams, {})

class TestConverToProbabilities(unittest.TestCase):
    def test_one_bigram(self):
        bigrams = {'markov': {'chain': 1}}
        markovify.convert_to_probabilities(bigrams)
        self.assertEqual(bigrams['markov']['chain'], 1/float(1))
    
    def test_one_previous_many_current_words(self):
        bigrams = {'markov': {'chain': 1, 'tree': 1, 'graph': 1}}
        markovify.convert_to_probabilities(bigrams)
        self.assertEqual(bigrams['markov']['chain'], 1/float(3))
        self.assertEqual(bigrams['markov']['tree'], 1/float(3))
        self.assertEqual(bigrams['markov']['graph'], 1/float(3))

    def test_many_previous_many_current_words(self):
        bigrams = {'markov': {'chain': 1, 'tree': 1, 'graph': 1},
                   'chain': {'mal': 1, 'bridge': 1}}
        markovify.convert_to_probabilities(bigrams)
        self.assertEqual(bigrams['markov']['chain'], 1/float(3))
        self.assertEqual(bigrams['markov']['tree'], 1/float(3))
        self.assertEqual(bigrams['markov']['graph'], 1/float(3))
        self.assertEqual(bigrams['chain']['mal'], 1/float(2))
        self.assertEqual(bigrams['chain']['bridge'], 1/float(2))

class TestFormatWord(unittest.TestCase):
    def test_format_word(self):
        self.assertEqual(markovify.format_word('hello'), 'hello ')
        self.assertEqual(markovify.format_word('a'), 'a ')
        self.assertEqual(markovify.format_word('markov.'), 'markov. \n\n')

class TestGenerateText(unittest.TestCase):
    def test_generate_text(self):
        bigrams = {'Markov': {'chain': 1, 'tree': 1, 'graph': 1},
                   'chain': {'mal': 1, 'bridge': 1}}
        markovify.convert_to_probabilities(bigrams)
        text = markovify.generate_text(bigrams)
        generated_bigrams = markovify.count_bigrams(text)
        markovify.convert_to_probabilities(generated_bigrams)
        def test(previous_word, current_word):
            epsilon = 0.02
            diff = (bigrams[previous_word][current_word] -
                   generated_bigrams[previous_word][current_word])
            self.assertTrue(diff < epsilon)
        test('Markov', 'chain')
        test('Markov', 'tree')
        test('Markov', 'graph')
        test('chain', 'mal')
        test('chain', 'bridge')

class TestRemoveBrokenChains(unittest.TestCase):
    def test_remove_broken_chains(self):
        bigrams = {'markov': {'chain': 1, 'tree': 1, 'graph': 1},
                   'chain': {'mal': 1, 'bridge': 1, 'markov': 1},
                   'mal' : {'knight': 1}}
        markovify.remove_broken_chains(bigrams)
        self.assertEqual(bigrams,{'markov': {'chain': 1}, 'chain': {'markov': 1}})

if __name__ == '__main__':
    unittest.main()
