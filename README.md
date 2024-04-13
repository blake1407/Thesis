# Reddit-JSON-Parser
This repository is an attempt at parsing reddit posts' data.

I. Data Collection:
In order to access archived content from Reddit, use this website: https://search.pullpush.io and input appropriate keywords (subreddit name, before and after timestamp).
Keyword used: 
1. (Brazil AND election*) OR (Brazil) OR (election*)

II. Library required for the NER file: 
1. Natural Language Toolkit
2. spaCy, including the "en_core_web_sm" model.
To install all of them, run each of the code in the terminal (without the "$"):
$ pip install spacy
$ pip install nltk
$ python -m spacy download en_core_web_sm

