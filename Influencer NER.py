import csv 
import os
   
import pandas as pd 
import spacy 
import requests 
from bs4 import BeautifulSoup

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
                comment_urls.append(comment.replace('"', "").strip())
            else:
                count_proper_comments += 1 
                corpus = corpus + " " + comment.strip()[1:-1] 
    print(f'Number of comments yielded for the corpus (that are not urls or deleted): {count_proper_comments}.') 
    print(f'Number of removed/deleted comments (has been filetered from corpus): {no_deleted_comments}.')                  
                
create_corpus(all_post_titles)

# print(corpus)
# print(comment_urls)

"""
NER for names using spaCy!
"""
nlp = spacy.load("en_core_web_sm")
pd.set_option("display.max_rows", 200)
 
NER_output = []
doc = nlp(corpus)

for ent in doc.ents:
    # The output displayed the names of the entities and their predicted labels. !!!!!!!!!(sort for person names)
    if ent.text not in NER_output:
        NER_output.append(ent.text,  ent.label)
print(NER_output)

# Find noun phrases in the corpus
# print("Noun phrases:", [chunk.text for chunk in doc.noun_chunks])

# Find verbs in the corpus
# print("Verbs:", [token.lemma_ for token in doc if token.pos_ == "VERB"])


filtered_corpus = ""
def remove_output_from_corpus() -> str:
    #remove already found NER output from the general corpus.
    global NER_output
    global corpus
    global filtered_corpus
    filtered_corpus = corpus
    for entity in NER_output:
        filtered_corpus = filtered_corpus.replace(entity, "")

remove_output_from_corpus()

filtered_doc = nlp(filtered_corpus)
#find reminaing noun phrases
remained_nouns = [chunk.text for chunk in filtered_doc.noun_chunks]

print(remained_nouns)

corpus_remained_nouns = remained_nouns.join()

Lula = ["Luiz Inácio Lula da Silva", "Luiz Inacio Lula da Silva", "da Silva"]
Bolsonaro = ["Jair Bolsonaro", "Bolsonaro", "Lula"]

# def names_in_urls() -> list:
#     global comment_urls
#     for comment in comment_urls:

# names_in_urls()
