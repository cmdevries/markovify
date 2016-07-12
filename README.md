# Markovify
Fetch text from p tags in URLs and generate text using markov chains with
transition probabilities learned from the text.

## Usage 
The program takes a list of URLs to scrape via command line arguments.

    $ ./markovify.py https://en.wikipedia.org/wiki/Art
    https://en.wikipedia.org/wiki/War https://en.wikipedia.org/wiki/Religion

And then it randomly generates often humourus text based on the probabilities
of word transitions in the text scraped from these URLs.

    However the art Symbolism impressionism and military tactics and video or
    intended to each artwork have emerged in the sound of Émile Durkheim Karl
    Marx and infection.

The program will scrape two random Wikipedia pages by default. 

    $ ./markovify

    The Inuyama Castle which is located in 1868.

Mix odd topics for more hilarity.

    $ ./markovify.py https://en.wikipedia.org/wiki/George_W._Bush
    https://en.wikipedia.org/wiki/Fashion
    
    She is using a person chooses to track how to his name be Jesus Day in Iraq
    and to as the law a fashion industry.
