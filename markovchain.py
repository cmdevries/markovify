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
    
    def text(self):
        return self.ptext

def fetch_text(url):
    response = requests.get(url)
    parser = Text()
    parser.feed(response.text)
    return parser.text()

def valid_bigram(previous_word, current_word):
    # strip full stops for determining validity
    # for example, 'M.' is a single character word
    previous_word = previous_word.strip('.')
    current_word = current_word.strip('.')
    words_not_empty = previous_word != '' and current_word != ''
    one_word_is_a = current_word == 'a' or previous_word == 'a'
    words_not_single_letter = len(current_word) > 1 and len(previous_word) > 1
    return words_not_empty and (one_word_is_a or words_not_single_letter)

def count_bigram(bigrams, previous_word, current_word):
    if valid_bigram(previous_word, current_word):
        if previous_word not in bigrams:
            bigrams[previous_word] = {}
        if current_word not in bigrams[previous_word]:
            bigrams[previous_word][current_word] = 0
        bigrams[previous_word][current_word] += 1

def count_bigrams(text):
    bigrams = {} # bigrams[word1][word2] -> count
                 # where word1 appears immediately before word2 in the text 
    previous_word = ''
    current_word = ''
    include = set(["'", "."])
    for c in text:
        if c.isalnum() or c in include:
            current_word += c
        else:
            current_word.strip("'") # only process apostrophes inside words
            if current_word != '':
                count_bigram(bigrams, previous_word, current_word)
                previous_word = current_word
                current_word = ''
    return bigrams 

def merge(bigrams, bigrams_new):
    for previous_word, countmap in bigrams_new.items():
        for current_word, count in countmap.items():
            if previous_word not in bigrams:
                bigrams[previous_word] = {}
            if current_word not in bigrams[previous_word]:
                bigrams[previous_word][current_word] = 0
            bigrams[previous_word][current_word] += count

def convert_to_probabilities(bigrams):
    for countmap in bigrams.values():
        total = 0
        for count in countmap.values():
            total += count
        for word in countmap.keys():
            countmap[word] = countmap[word] / float(total) if total != 0 else 0

def generate_text(bigrams):
    if len(bigrams) == 0:
        print 'No statistics to generate text from'
        return
    current_word = 'a'
    while current_word[0].islower(): # start with an upper case word
        current_word = random.choice(bigrams.keys())
    maximum = 10000
    for i in range(maximum):
        print current_word,
        if current_word[-1] == '.' and current_word.count('.') == 1:
            print
            print
        r = random.random()
        curr_prob = 0
        for word, prob in bigrams[current_word].items():
            curr_prob += prob
            if r < curr_prob:
                if word in bigrams:
                    current_word = word
                    break
                else:
                    current_word = random.choice(bigrams.keys())

def process(urls):
    bigrams = {}
    for url in urls:
        merge(bigrams, count_bigrams(fetch_text(url)))
    convert_to_probabilities(bigrams)
    generate_text(bigrams)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: %s [list of urls to learn markov chains from]'
            % sys.argv[0])
        sys.exit(1)
    process(sys.argv[1:])
