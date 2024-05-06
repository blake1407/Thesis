import csv 
import os
   
import pandas as pd 
import spacy 
# spacy.cli.download("pt_core_news_sm")
# spacy.cli.download("es_core_news_sm")

import requests 
from bs4 import BeautifulSoup
from dataclasses import dataclass

#Sentence Tokenization using sent_tokenize
import nltk
# nltk.download('punkt')
from nltk import word_tokenize,sent_tokenize
from nltk.tokenize import word_tokenize


#Detect language using detect_langs
import langdetect
from langdetect import detect_langs

#Detect language using Lingua
from lingua import Language, LanguageDetectorBuilder

"""
First, I'm gonna get the entire corpus from the "Reddit Post Parsed" folder.
"""
all_post_titles = []
expected_no_comments = 0
corpus = ""
comment_urls = []
all_links = []

with open('log.csv', mode = 'r') as file:
    link_column = []
    title_column = []
    comments_column = []
    all_no_comments = []
    csvFile = csv.reader(file)
    for line in csvFile:
        title_column.append(line[2])
        all_post_titles = title_column[1:]
        comments_column.append(line[9])
        all_no_comments = comments_column[1:]
        link_column.append(line[3])
        all_links = link_column[1:]
    for number in all_no_comments:
        expected_no_comments += int(number)

# print(all_links)
#loop to open all post titles in create one big corpus of all comments
def create_corpus(titles: list) -> str:
    """
    This function takes in a list of posts titles in the 
    folder "Reddit Post Parsed" and loops through each 
    csv file to filter for proper comments, that are not urls
    and deleted to return the corpus.

    Comments that are just links will be 
    appended to the list "comment_urls"!
    """
    global corpus
    global comment_urls

    count_proper_comments = 0
    no_deleted_comments = 0
    empty = ""
    list_of_comments = []
    
    base_folder = "Update posts files"
    for title in titles:
        title_csv = os.path.join(base_folder, title + "'s post.csv")
        if not os.path.isfile(title_csv):
            print(f"File '{title_csv}' not found.")
            continue
    
        with open(title_csv, mode='r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                list_of_comments.append(empty.join(row[9:]))

    for comment in list_of_comments:
        if comment.strip() != "Body":
            if comment.strip() == '"deleted"' or comment.strip() == '"removed"':
                no_deleted_comments +=1
                comment = ""
            if comment.strip().startswith('"https:'):
                comment_urls.append(comment.replace('"', "").strip())
            else:
                count_proper_comments += 1 
                corpus = corpus + " " + comment.replace("**", "").replace("#", "").strip()[1:-1] 
    print(f'Number of comments yielded for the corpus (that are not urls or deleted): {count_proper_comments}.') 
    print(f'Number of removed/deleted comments (has been filetered from corpus): {no_deleted_comments}.\n')                  
                
create_corpus(all_post_titles)

@dataclass
class entities:
    name: str
    label: str

#strip out the pronouns, conjunctions, etc.!
f = open('pronouns.txt', 'r')
pronouns = f.read()

#filter out pronouns from the remainded_nouns
pronouns_lower = set([pronoun.lower() for pronoun in pronouns])

# print(corpus)
# print(comment_urls)

"""
METHOD 1: Langdetect each sentence in the corpus and use 2 NER models (en & pt)
"""
# Load the spaCy English & Portuguese models
en_nlp = spacy.load("en_core_web_sm")
pt_nlp = spacy.load('pt_core_news_sm')
pd.set_option("display.max_rows", 200)
 
#separate into tokenized sentences
# tokenizer = nltk.data.load('tokenizers/punkt/PY3/english.pickle')
tokenizer = nltk.data.load('tokenizers\punkt\english.pickle')
sentences = tokenizer.tokenize(corpus)

#Sentences with more than one languages detected
mixed_s = []
#Sentences with only one language detected
en_s = []
es_s = []
pt_s = []

for sentence in sentences:
    #benchmark is with a language probablity over 0.5
    try:
        score = detect_langs(sentence)
        if len(score) > 1:
            mixed_s.append(sentence)
        for s in score:
            if s.lang == 'en' and s.prob >= 0.5:
                en_s.append(sentence)
            if s.lang == 'es' and s.prob >= 0.5:
                es_s.append(sentence)
            if s.lang == 'pt' and s.prob >= 0.5:
                pt_s.append(sentence)
            else:
                mixed_s.append(sentence)
    except:
        #discard "." or numbers
        # print("This throws an error: " + sentence)
        continue 


method1_NER_output = []

# Process the text using spaCy
en_doc = en_nlp(" ".join(en_s) + " ".join(mixed_s))
pt_doc = pt_nlp(" ".join(es_s) + " ".join(pt_s))


#English NER model
for ent in en_doc.ents:
    if entities(ent.text, ent.label_) not in method1_NER_output:
        if ent.label_ == "PERSON":
            method1_NER_output.append(entities(ent.text, ent.label_))

#Portuguese NER model
for ent in pt_doc.ents:
    if entities(ent.text, ent.label_) not in method1_NER_output:
        if ent.label_ == "PERSON":
            method1_NER_output.append(entities(ent.text, ent.label_))

method1_filtered_corpus = ""
def remove_output_from_corpus() -> str:
    #remove already found NER output from the general corpus.
    global method1_NER_output
    global corpus
    global method1_filtered_corpus

    method1_filtered_corpus = corpus
    for entity in method1_NER_output:
        method1_filtered_corpus = method1_filtered_corpus.replace(entity.name, "")

remove_output_from_corpus()

method1_filtered_doc = en_nlp(method1_filtered_corpus)

#find reminaing noun phrases
method1_remained_nouns = [chunk.text for chunk in method1_filtered_doc.noun_chunks]

# Filter out pronouns from the remained_nouns list
method1_filtered_remained_nouns = [noun for noun in method1_remained_nouns if noun.lower() not in pronouns_lower]

# filtered1 = [noun for noun in remained1_nouns if noun.lower() not in pronouns_lower]


"""
METHOD 2: No langdetect and use 1 NER models (en) for the entire corpus
"""

combined_doc = en_nlp(corpus)

method2_output = []

#English NER model
for ent in combined_doc.ents:
    if entities(ent.text, ent.label_) not in method2_output:
        if ent.label_ == "PERSON":
            method2_output.append(entities(ent.text, ent.label_)) 

method2_filtered_corpus = ""

def remove_output_from_corpus() -> str:
    #remove already found NER output from the general corpus.
    global method2_output
    global corpus
    global method2_filtered_corpus

    method2_filtered_corpus = corpus
    for entity in method2_output:
        method2_filtered_corpus = method2_filtered_corpus.replace(entity.name, "")

remove_output_from_corpus()

method2_filtered_doc = en_nlp(method2_filtered_corpus)

method2_remained_nouns = [chunk.text for chunk in method2_filtered_doc.noun_chunks]

# Filter out pronouns from the remained_nouns list
method2_filtered_remained_nouns = [noun for noun in method2_remained_nouns if noun.lower() not in pronouns_lower]


"""
METHOD 3: Langdetect word by word
"""
words_token = word_tokenize(corpus)

#remove pronouns
words = [noun for noun in words_token if noun.lower() not in pronouns_lower]


language_detected = []
for word in words:
    #benchmark is with a language probablity over 0.5
    try:
        w_score = detect_langs(word)
        for s in w_score:
            if s.lang not in language_detected and s.prob > 0.8:
                language_detected.append(s.lang)
    except:
        #discard punctuations or numbers
        # print("This throws an error: " + word)
        continue 


"""
METHOD 4: Lingua the entire corpus
"""
languages = [Language.ENGLISH, Language.PORTUGUESE, Language.SPANISH]
detector = LanguageDetectorBuilder.from_languages(*languages).build()
corpus_confidence_values = detector.compute_language_confidence_values(corpus)
# for confidence in corpus_confidence_values:
#     print(f"{confidence.language.name}: {confidence.value:.2f}")

"""
METHOD 5: Lingua word by word
"""
en_lingua = []
pt_lingua = []

for word in words:
    w = detector.compute_language_confidence_values(word)
    for s in w:
        if s.value > 0.5 and s.language.name == "ENGLISH":
            en_lingua.append(word)
        if s.value > 0.5 and s.language.name == "PORTUGUESE":
            pt_lingua.append(word)
            
print("Method 1: Langdetect each sentence in the corpus and use 2 NER models (en & pt/es)")
print(f'Amount of NER output: {len(method1_NER_output)}.')
print(f'Amount of remained nouns: {len(method1_filtered_remained_nouns)}.\n')

print("Method 2: No langdetect and use 1 NER models (en) for the entire corpus")
print(f'Amount of NER output: {len(method2_output)}.')
print(f'Amount of remained nouns: {len(method2_filtered_remained_nouns)}.\n') 

print("Method 3: Langdetect word by word (unreliable and time-consuming)")
print(f'Amount of total words: {len(words)}.')
print(f'Amount of language detected with probabilty over 0.8: {len(language_detected)}.\nIncluding {language_detected}\n')

print("Method 4: Lingua detect the entire corpus")
for confidence in corpus_confidence_values:
    print(f"{confidence.language.name}: {confidence.value:.2f}")
print('\n')

print("Method 4: Lingua detect word by word")
# print(f'English words: {en_lingua}.\n')
print(f'Portuguese words: {pt_lingua}.\n')


# for entity in method2_output:
#     print(entity)

f.close()

# Lula = ["Luiz Inácio Lula da Silva", "Luiz Inacio Lula da Silva", "da Silva", "President Jair", "leftist Luiz Inacio", "Luiz Inácio"]
# Bolsonaro = ["Jair Bolsonaro", "Bolsonaro", "Lula"]