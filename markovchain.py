import random
import requests
import sys

from HTMLParser import HTMLParser

class Text(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.p = 0
        self.ptext = ''
        
    def handle_starttag(self, tag, attrs):
        if tag == 'p':
            self.p += 1

    def handle_endtag(self, tag):
        if tag == 'p':
            self.p -= 1

    def handle_data(self, data):
        if self.p > 0:
            self.ptext += ' ' + data;

def fetch_text(url):
    response = requests.get(url)
    parser = Text()
    parser.feed(response.text)
    return parser.ptext

def sort_print(bigrams):
    items = bigrams.items()
    items.sort(key = lambda x: x[1])
    for kv in items:
        print('%s -> %s' % kv)

def parse_bigrams(text):
    bigrams = {} # (word1, word2) -> count
                 # where word1 appears immediately before word2 
    previous_word = ''
    current_word = ''
    include = set(["'", "."])
    for c in text:
        if c.isalnum() or c in include:
            current_word += c
        else:
            words_not_empty = previous_word != '' and current_word != ''
            one_word_is_a = current_word == 'a' or previous_word == 'a'
            words_not_single_letter = len(current_word) > 1 and len(previous_word) > 1
            if words_not_empty and (one_word_is_a or words_not_single_letter):
                bigram = (previous_word, current_word)
                if bigram not in bigrams:
                    bigrams[bigram] = 0
                bigrams[bigram] += 1
            previous_word = current_word
            current_word = ''
    return bigrams 

def generate_text(bigrams):
    total = 0
    for count in bigrams.values():
        total += count
    words = {} # word -> list of (word, probability)    
    for bigram, count in bigrams.items():
        word1, word2 = bigram
        if word1 not in words:
            words[word1] = []
        words[word1].append([word2, count])    
    for countlist in words.values():
        total = 0
        for word, count in countlist:
            total += count
        for pair in countlist:
            pair[1] = pair[1] / float(total)
        countlist.sort(key = lambda x: x[1], reverse = True)    
    current_word = 'a'
    while current_word[0].islower(): # start with an upper case word
        current_word = random.choice(words.keys())
    if True:
        maximum = 10000
        for i in range(maximum):
            print current_word,
            if current_word[-1] == '.':
                print
                print
            r = random.random()
            curr_prob = 0
            for word, prob in words[current_word]:
                curr_prob += prob
                if r < curr_prob:
                    if word in words:
                        current_word = word
                        break
                    else:
                        current_word = random.choice(words.keys())
    else:
        sentences = 1000
        prob_stop = 0.05
        maximum = 20
        minimum = 5
        for s in range(sentences): 
            for i in range(maximum):
                r = random.random()
                stripped_word = current_word.strip('.')
                if i == 0:
                    print "%s%s" % (stripped_word[0].upper(), stripped_word[1:]),
                else:
                    if i > minimum and r < prob_stop or i == maximum - 1:
                        print "%s.\n" % stripped_word
                        break
                    else:
                        print stripped_word,
                curr_prob = 0
                for word, prob in words[current_word]:
                    curr_prob += prob
                    if r < curr_prob:
                        if word in words:
                            current_word = word
                            break
                        else:
                            current_word = random.choice(words.keys())

def markov(urls):
    bigrams = {}
    def merge(bigrams_new):
        for bigram, count in bigrams_new.items():
            if bigram not in bigrams:
                bigrams[bigram] = 0
            bigrams[bigram] += count    
    for url in urls:
        merge(parse_bigrams(fetch_text(url)))
    generate_text(bigrams)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: %s [list of urls to learn markov chains from]'
            % sys.argv[0])
        sys.exit(1)
    markov(sys.argv[1:])
