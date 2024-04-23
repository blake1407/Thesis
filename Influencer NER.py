import csv 
import os
   
import pandas as pd 
import spacy 
import requests 
from bs4 import BeautifulSoup

#Sentence Tokenization using sent_tokenize
from nltk.tokenize import sent_tokenize

#Detect language using detect_langs
import langdetect
from langdetect import detect_langs

"""
First, I'm gonna get the entire corpus from the "Reddit Post Parsed" folder.
"""
all_post_titles = []
expected_no_comments = 0
corpus = ""
comment_urls = []

with open('log.csv', mode = 'r') as file:
    title_column = []
    comments_column = []
    all_no_comments = []
    csvFile = csv.reader(file)
    for line in csvFile:
        title_column.append(line[2])
        all_post_titles = title_column[1:]
        comments_column.append(line[9])
        all_no_comments = comments_column[1:]
    for number in all_no_comments:
        expected_no_comments += int(number)

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
    
    base_folder = "Reddit Post Parsed"
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
            if comment.strip() == '"[deleted]"' or comment.strip() == '"[removed]"':
                no_deleted_comments +=1
                comment = ""
            if comment.strip().startswith('"https:'):
                comment_urls.append(comment.strip())
            else:
                count_proper_comments += 1 
                corpus = corpus + " " + comment.replace("**", "").replace("#", "").strip()[1:-1] 
    print(f'Number of comments yielded for the corpus (that are not urls or deleted): {count_proper_comments}.') 
    print(f'Number of removed/deleted comments (has been filetered from corpus): {no_deleted_comments}.')                  
                
create_corpus(all_post_titles)

# print(corpus)
# print(comment_urls)

"""
NER for names using spaCy!
"""
# Load the spaCy English model
nlp = spacy.load("en_core_web_sm")
pd.set_option("display.max_rows", 200)
 
NER_output = []

# Process the text using spaCy
doc = nlp(corpus)

sentence_tokens = sent_tokenize(corpus)

#sort into english, spanish, or mixed sentences
en_sentences = ""
mixed_sentences = ""
es_sentences = ""

def filter_languages():
    global sentence_tokens
    global en_sentences
    global mixed_sentences
    global es_sentences
    for token in sentence_tokens:
        detected_lang = langdetect.detect_langs(token)
        #if only one language is detected
        if len(detected_lang) == 1:
            for lang in detected_lang: 
                if lang.lang == 'en' and lang.prob > 0.5:
                    en_sentences = en_sentences + " " + token
                if lang.lang == 'es' and lang.prob > 0.5:
                    es_sentences = es_sentences + " " + token
        #if more than one language is detected
        if len(detected_lang) > 1:
            mixed_sentences = mixed_sentences + " " + token 

filter_languages()
en_doc = nlp(en_sentences)
es_doc = nlp(es_sentences)
mixed_doc = nlp(mixed_sentences)

en_lemmatized_tokens = [token.lemma_ for token in en_doc]
en_lemmatized_text = ' '.join(en_lemmatized_tokens)

es_lemmatized_tokens = [token.lemma_ for token in es_doc]
es_lemmatized_text = ' '.join(es_lemmatized_tokens)

mixed_lemmatized_tokens = [token.lemma_ for token in mixed_doc]
mixed_lemmatized_text = ' '.join(mixed_lemmatized_tokens)

for ent in nlp(en_lemmatized_text).ents:
    # The output displayed the names of the entities and their predicted labels.
    if ent.text not in NER_output:
        NER_output.append(ent.text)

# Find noun phrases in the corpus
# print("Noun phrases:", [chunk.text for chunk in doc.noun_chunks])

# Find verbs in the corpus
# print("Verbs:", [token.lemma_ for token in doc if token.pos_ == "VERB"])

print(NER_output)
filtered_corpus = ""
def remove_output_from_corpus() -> str:
    global NER_output
    global corpus
    global filtered_corpus
    filtered_corpus = corpus
    for entity in NER_output:
        filtered_corpus = filtered_corpus.replace(entity, "")

remove_output_from_corpus()

filtered_doc = nlp(filtered_corpus)
remained_nouns = [chunk.text for chunk in filtered_doc.noun_chunks]

print(remained_nouns)