#!/usr/bin/env python
import markovify
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

if __name__ == '__main__':
    unittest.main()
