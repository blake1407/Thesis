# Reddit-JSON-Parser
This repository is an attempt at parsing reddit posts' data.

I. Data Collection:
In order to access archived content from Reddit, use this website: https://search.pullpush.io and input appropriate keywords (subreddit name, before and after timestamp).
Keyword used: 
1. (Brazil AND election*) OR (Brazil) OR (election*)

II. Library required for the NER file: 
1. Natural Language Toolkit
2. langdetect
3. spaCy, including the "en_core_web_sm" model. (for more information: https://spacy.io/models; https://github.com/explosion/spacy-models)
4. Lingua, (for more information: https://github.com/pemistahl/lingua-py.git)

To install all of them, run each of the code in the terminal (without the "$"):
$ pip install lingua-language-detector
$ pip install spacy
$ pip install langdetect
$ pip install nltk
$ python -m spacy download en_core_web_sm
$ python -m spacy download pt_core_news_sm


Troubleshooting:
1. When installing for en_core_web_sm: "No module named spacy". 
Download the model zip file from https://github.com/explosion/spacy-models/releases.
Then use: (".." is whatever folders the file is in)
$ pip install /Users/you/../en_core_web_sm-3.0.0.tar.gz
2. Or, uncomment the following lines (will automatically update the package everytime the program is run): 
# spacy.cli.download("pt_core_news_sm")
# spacy.cli.download("es_core_news_sm")

III. NER Label 101:
PERSON:      People, including fictional.
NORP:        Nationalities or religious or political groups.
FAC:         Buildings, airports, highways, bridges, etc.
ORG:         Companies, agencies, institutions, etc.
GPE:         Countries, cities, states.
LOC:         Non-GPE locations, mountain ranges, bodies of water.
PRODUCT:     Objects, vehicles, foods, etc. (Not services.)
EVENT:       Named hurricanes, battles, wars, sports events, etc.
WORK_OF_ART: Titles of books, songs, etc.
LAW:         Named documents made into laws.
LANGUAGE:    Any named language.
DATE:        Absolute or relative dates or periods.
TIME:        Times smaller than a day.
PERCENT:     Percentage, including ”%“.
MONEY:       Monetary values, including unit.
QUANTITY:    Measurements, as of weight or distance.
ORDINAL:     “first”, “second”, etc.
CARDINAL:    Numerals that do not fall under another type.


