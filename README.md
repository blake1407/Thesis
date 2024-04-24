# Reddit-JSON-Parser
This repository is an attempt at parsing reddit posts' data.

I. Data Collection:
In order to access archived content from Reddit, use this website: https://search.pullpush.io and input appropriate keywords (subreddit name, before and after timestamp).
Keyword used: 
1. (Brazil AND election*) OR (Brazil) OR (election*)

II. Library required for the NER file: 
1. Natural Language Toolkit
2. spaCy, including the "en_core_web_sm" model. (for more information: https://spacy.io/models; https://github.com/explosion/spacy-models)
To install all of them, run each of the code in the terminal (without the "$"):
$ pip install spacy
$ pip install nltk
$ python -m spacy download en_core_web_sm

Troubleshooting:
1. When installing for en_core_web_sm: "No module named spacy". 
Download the model zip file from https://github.com/explosion/spacy-models/releases.
Then use: (".." is whatever folders the file is in)
$ pip install /Users/you/../en_core_web_sm-3.0.0.tar.gz


