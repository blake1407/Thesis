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

# print(corpus)
# print(comment_urls)

"""
NER for names using spaCy!
"""
# Load the spaCy English model
en_nlp = spacy.load("en_core_web_sm")
pt_nlp = spacy.load('pt_core_news_sm')
pd.set_option("display.max_rows", 200)
 
#separate into tokenized sentences
# tokenizer = nltk.data.load('tokenizers/punkt/PY3/english.pickle')
tokenizer = nltk.data.load('tokenizers\punkt\english.pickle')
sentences = tokenizer.tokenize(corpus)

#Sentences with more than one languages detected
mixed_s = []
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
        # print("This throws an error: " + sentence)
        continue 


NER_output = []

@dataclass
class entities:
    name: str
    label: str

# Process the text using spaCy
en_doc = en_nlp(" ".join(en_s) + " ".join(mixed_s))
pt_doc = pt_nlp(" ".join(es_s) + " ".join(pt_s))

combined_doc = en_nlp(corpus)
test1_output = []

#English NER model
for ent in en_doc.ents:
    if ent.text not in NER_output:
        NER_output.append(entities(ent.text, ent.label_))

#Portuguese NER model
for ent in pt_doc.ents:
    if ent.text not in NER_output:
        NER_output.append(entities(ent.text, ent.label_))

#English NER model
for ent in combined_doc.ents:
    if ent.text not in test1_output:
        test1_output.append(entities(ent.text, ent.label_)) 

filtered_corpus = ""
filtered1_corpus = ""
def remove_output_from_corpus() -> str:
    #remove already found NER output from the general corpus.
    global NER_output
    global corpus
    global filtered_corpus
    global filtered1_corpus

    filtered_corpus = corpus
    for entity in NER_output:
        filtered_corpus = filtered_corpus.replace(entity.name, "")

    filtered1_corpus = corpus
    for entity in test1_output:
        filtered1_corpus = filtered1_corpus.replace(entity.name, "")

remove_output_from_corpus()

filtered_doc = en_nlp(filtered_corpus)
filtered1_doc = en_nlp(filtered1_corpus)

#find reminaing noun phrases
remained_nouns = [chunk.text for chunk in filtered_doc.noun_chunks]
remained1_nouns = [chunk.text for chunk in filtered1_doc.noun_chunks]

##strip out the pronouns, conjunctions, etc.!
pronouns = ['I', 'you', 'my', 'mine', 'myself', 'we', 'us', 'our', 'ours', 'ourselves', 'you', 'you', 'your', 
            'yours', 'yourself', 'you', 'you', 'your', 'your', 'yourselves', 'he', 'him', 'his', 'his', 'himself'
            'she', 'her', 'her', 'her', 'herself', 'it', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 
            'themself', 'they', 'them', 'their', 'theirs', 'themselves', "Another", "anybody", "anyone", "anything", 
            "each", "either", "enough", "everybody", "everyone", "everything", "little", "much", "neither", "nobody", 
            "no one", "nothing", "one", "other", "somebody", "something", "Both", "few", "fewer", "many", "others", 
            "several", "All", "any", "more", "most", "someone", "none", "some", "such", "this", "that", "these", "those"
            "who", "whom", "whose", "what", "which", "those people", "these guys", "me", "some people"]

#filter out pronouns from the remainded_nouns
pronouns_lower = set([pronoun.lower() for pronoun in pronouns])

# Filter out pronouns from the remained_nouns list
filtered_remained_nouns = [noun for noun in remained_nouns if noun.lower() not in pronouns_lower]

filtered1 = [noun for noun in remained1_nouns if noun.lower() not in pronouns_lower]


# print(filtered_remained_nouns)
# corpus_remained_nouns = "".join(remained_nouns)

# Lula = ["Luiz Inácio Lula da Silva", "Luiz Inacio Lula da Silva", "da Silva", "President Jair", "leftist Luiz Inacio", "Luiz Inácio"]
# Bolsonaro = ["Jair Bolsonaro", "Bolsonaro", "Lula"]

print("Method 1: Langdetect each sentence in the corpus and use 2 NER models (en & es)")
print(f'Amount of NER output: {len(NER_output)}.')
print(f'Amount of remained nouns: {len(filtered_remained_nouns)}.\n') 

print("Method 2: No langdetect and use 1 NER models (en) for the entire corpus")
print(f'Amount of NER output: {len(test1_output)}.')
print(f'Amount of remained nouns: {len(filtered1)}.\n') 

for entity in test1_output:
    print(entity)
