import csv 
import os

all_post_titles = []
expected_no_comments = 0

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

def remove_unwanted(check: str) -> str:
    check = check.strip()
    if check == '"[deleted]"' or check == '"[removed]"':
        check = ""
    elif check.startswith('"https:'):
        check = ""
    elif check != "Body" and check:
        return check

#loop to open all post titles in create one big corpus of all comments
corpus = ""
def create_corpus(titles: list) -> str:
    global corpus
    base_folder = "Reddit Post Parsed"
    for title in titles:
        title_csv = os.path.join(base_folder, title + "'s post.csv")
        if not os.path.isfile(title_csv):
            print(f"File '{title_csv}' not found.")
            continue
    
        with open(title_csv, mode='r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            try:
                for _ in range(9):
                    next(csv_reader)
            except StopIteration:
                None
                # print("The CSV file doesn't have enough rows.")
                # exit(1)
            row_index = 9
            for row in csv_reader:
                row_index +=1
                col_index = 0
                for value in row[9:]:
                    col_index += 1
                    print(f"Value at {chr(65+col_index)}{row_index}: {value}")
                    if not value:
                        break
                    

create_corpus(all_post_titles)