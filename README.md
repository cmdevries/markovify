# markovchain
Fetch text from p tags in URLs and generate text using markov chains with
transition probabilities learned from the text.

## usage 
The program takes a list of URLs to scrape via command line arguments.

    $ python markovchain.py https://en.wikipedia.org/wiki/Art
    https://en.wikipedia.org/wiki/War https://en.wikipedia.org/wiki/Religion

And then it randomly generates often humourus text based on the probabilities
of word transitions in the text scraped from these URLs.

    However the art Symbolism impressionism and military tactics and video or
    intended to each artwork have emerged in the sound of Émile Durkheim Karl
    Marx and infection.

Mix odd topics for more hilarity.

    $ python markovchain.py https://en.wikipedia.org/wiki/George_W._Bush
    https://en.wikipedia.org/wiki/Fashion

    Machine vision technology has spent some textile design motifs had been.
