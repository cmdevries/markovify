# Markovify
Fetch text from p tags in URLs and generate text using large language models or
markov chains with content learned from the text.

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

    $ ./markovify.py

    The Inuyama Castle which is located in 1868.

Mix odd topics for more hilarity.

    $ ./markovify.py https://en.wikipedia.org/wiki/George_W._Bush
    https://en.wikipedia.org/wiki/Fashion
    
    She is using a person chooses to track how to his name be Jesus Day in Iraq
    and to as the law a fashion industry.

Experimental support for generation using the Microsoft phi-2 LLM on Apple
silicon using MLX.

    $ ./markovify.py --mlx

    The Nikon AF-S DX Nikkor mm f/2.8G ED VR is a full-frame,
    wide angle prime lens for Nikon DX format DSLR cameras.
