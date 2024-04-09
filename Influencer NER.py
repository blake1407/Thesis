import csv 
import os

all_post_titles = []

with open('log.csv', mode = 'r') as file:
    csvFile = csv.reader(file)
    for line in csvFile:
        all_post_titles.append(line[2])

#loop to open all post titles in create one big corpus of all comments
corpus = ""
def create_corpus(titles: list) -> str:
    global corpus
    base_folder = "Reddit Post Parsed"
    for title in titles[1:]:
        title_csv = os.path.join(base_folder, title + "'s post.csv")
        if not os.path.isfile(title_csv):
            print(f"File '{title_csv}' not found.")
            continue
        with open(title_csv, mode='r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            for line in csv_reader:
                if line[-2].strip() != "Body":
                    refined = line[-2].strip()
                    if not refined.startswith('"https://') and refined != '"[removed]"' and refined != '"[deleted]"':
                        if refined.startswith('"'):
                            refined = refined[1:]
                        if refined.endswith('"'):
                            refined = refined[-2] + ". "
                        corpus += refined


create_corpus(all_post_titles)

print(corpus)
