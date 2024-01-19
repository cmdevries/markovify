#!/usr/bin/env python
import random
import re
import requests
import sys

from html.parser import HTMLParser

class Text(HTMLParser):
    """Extract text from <p> tags inside HTML."""

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
        """Retrieve the text observed inside <p> tags."""
        return self.ptext

def fetch_text(url):
    """fetch_text(string) -> string

    Retrieve the text inside <p> tags from the specified url.
    """
    response = requests.get(url)
    parser = Text()
    parser.feed(response.text)
    return parser.text(), response.url

def valid_bigram(previous_word, current_word):
    """valid_bigram(string, string) -> boolean

    Given two words that are adjacent in text determine if is a valid. The words
    can be empty strings. The previous word for the first word is the empty
    string and there are other cases where an empty word can occur does to
    irregularities in the text such as a token contain only characters that are
    ignored.

    Full stops are stripped prior to determining validity. For example, 'M.'
    is a single character word.
    """
    previous_word = previous_word.strip('.')
    current_word = current_word.strip('.')
    words_not_empty = previous_word != '' and current_word != ''
    one_word_is_a = (current_word == 'a') ^ (previous_word == 'a')
    words_not_single_letter = len(current_word) > 1 and len(previous_word) > 1
    return words_not_empty and (one_word_is_a or words_not_single_letter)

def count_bigram(bigrams, previous_word, current_word):
    """count_bigram(dict(dict(numeric)), string, string) -> None

    Update the counts for bigrams[previous_word][current_word].
    """
    if valid_bigram(previous_word, current_word):
        if previous_word not in bigrams:
            bigrams[previous_word] = {}
        if current_word not in bigrams[previous_word]:
            bigrams[previous_word][current_word] = 0
        bigrams[previous_word][current_word] += 1

def clean_word(current_word):
    """clean_word(string) -> string

    Clean the current word of unwanted characters. There are only apostrophes
    and dashes inside words and fullstops at the end.
    """
    ends_with_fullstop = False
    if len(current_word) > 0:
        ends_with_fullstop = current_word[-1] == '.'
    current_word = current_word.strip("'-.")
    if ends_with_fullstop:
        current_word += '.'
    return current_word

def parse_tokens(text):
    """parse_tokens(string) -> list(string)

    Return a list of words in the text.
    """
    words = []
    current_word = ''
    include = set(["'", ".", "-"])
    for c in text:
        if c.isalnum() or c in include:
            current_word += c
        else:
            current_word = clean_word(current_word)
            if current_word != '':
                words.append(current_word)
                current_word = ''
    if current_word != '':
        words.append(current_word)
    return words

def count_bigrams(text):
    """bigrams(string) -> dict(dict(int))

    Returns bigrams where, bigrams[word1][word2] -> count, and word1 appears
    immediately before word2 in the text.
    """
    bigrams = {}
    tokens = parse_tokens(text)
    for previous_word, current_word in zip(tokens[:-1], tokens[1:]):
        count_bigram(bigrams, previous_word, current_word)
    return bigrams

def merge(bigrams, bigrams_new):
    """merge(dict(dict(numeric)), dict(dict(numeric))) -> None

    Merges bigrams_new into bigrams where the counts are added.
    """
    for previous_word, countmap in bigrams_new.items():
        for current_word, count in countmap.items():
            if previous_word not in bigrams:
                bigrams[previous_word] = {}
            if current_word not in bigrams[previous_word]:
                bigrams[previous_word][current_word] = 0
            bigrams[previous_word][current_word] += count

def convert_to_probabilities(bigrams):
    """convert_to_probabilities(dict(dict(numeric))) -> None

    Modify bigrams so that for each word in the outer dictionary the numeric
    type associated with all words in the inner dictionary sums to 1; i.e.
    count / total.
    """
    for countmap in bigrams.values():
        total = 0
        for count in countmap.values():
            total += count
        for word in countmap.keys():
            countmap[word] = countmap[word] / float(total) if total != 0 else 0

def format_word(current_word):
    """make_word(string) -> string

    Format the current word for appending to the generated text.
    """
    word = '%s ' % current_word
    if current_word[-1] == '.' and current_word.count('.') == 1:
        word += '\n\n'
    return word

def generate_text(bigrams):
    """generate_text(dict(dict(float))) -> string

    Generate text randomly based on the transition probabilities in bigrams.
    """
    if len(bigrams) == 0:
        return 'No statistics to available generate text'
    current_word = 'a'
    while current_word[0].islower(): # start with an upper case word
        current_word = random.choice(list(bigrams.keys()))
    maximum = 10000
    text = ''
    for i in range(maximum):
        text += format_word(current_word)
        if current_word not in bigrams:
            current_word = random.choice(list(bigrams.keys()))
            text += format_word(current_word)
        r = random.random()
        cumulative_probability = 0.0
        for word, probability in bigrams[current_word].items():
            cumulative_probability += probability
            if r < cumulative_probability:
                current_word = word
                break
    return text

def remove_broken_chains(bigrams):
    """remove_broken_chains(dict(dict(numeric))

    Remove bigrams where the second word does not exist as a first word. This
    prevents following a bigram that can not be followed. This removes words
    from the inner dictionaries that do not exist in the outer dictionary.
    If the outer dictionary is also empty, it is also removed."""
    removed_any = True
    while removed_any:
        removed_any = False
        for countmap in bigrams.values():
            for current_word in list(countmap.keys()):
                if current_word not in bigrams:
                    countmap.pop(current_word)
                    removed_any = True
        for previous_word, countmap in list(bigrams.items()):
            if len(countmap) == 0:
                bigrams.pop(previous_word)
                removed_any = True

def process(urls):
    """process(list(string)) -> None

    Parse all the text inside <p> tags for each url in urls and generate random
    text using the transition probabilities.
    """
    bigrams = {}
    for url in urls:
        text, final_url = fetch_text(url)
        print('FETCHED TEXT FROM: %s\n' % final_url)
        merge(bigrams, count_bigrams(text))
    remove_broken_chains(bigrams)
    convert_to_probabilities(bigrams)
    print(generate_text(bigrams))

def process_mlx(urls):
    """process_mlx(list(string)) -> None
    
    Prompt the Microsoft Phi-2 LLM with all the text inside <p> tags and
    generate text.
    """
    all_text = ''
    for url in urls:
        text, final_url = fetch_text(url)
        print('FETCHED TEXT FROM: %s\n' % final_url)
        all_text += text
    all_text = all_text.replace('\n', '')
    all_text = re.sub('[^a-zA-Z\.\s]', '', all_text)
    all_text = re.sub('\s+', ' ', all_text)
    all_text = re.sub(' \.', '.', all_text)
    prompt = f'Summarize the following. {all_text}.'
    from mlx_lm import load, generate
    model, tokenizer = load('microsoft/phi-2')
    response = generate(model, tokenizer, max_tokens=2048, prompt=all_text, \
        verbose=True, temp=0.5)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1].lower() == '--help':
        print('usage: %s [list of urls to learn markov chains from]'
            % sys.argv[0])
        print('To use the phi-2 LLM on MacBook with MLX:')
        print('%s --mlx [list of urls to learn from]' % sys.argv[0])
        sys.exit(1)
    pages = []
    random_page = 'https://en.wikipedia.org/wiki/Special:Random'
    if len(sys.argv) > 1 and sys.argv[1].lower() == '--mlx':
        if len(sys.argv) < 3:
            pages = [random_page, random_page]
        else:
            pages = sys.argv[2:]
        process_mlx(pages)
    else:
        if len(sys.argv) < 2:
            pages = [random_page, random_page]
        else:
            pages = sys.argv[1:]
        process(pages)
