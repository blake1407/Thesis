import csv 
import os

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
    This function takes in a list of posts titles in the folder "Reddit Post Parsed"
    and loops through each csv file to filter for proper comments, that are not urls
    and deleted to return the corpus.
    Comments that are just links will be appended to the list "comment_urls"!
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
                corpus = corpus + " " + comment.strip()[1:-1] 
    print(f'Number of comments yielded for the corpus (that are not urls or deleted): {count_proper_comments}.') 
    print(f'Number of removed/deleted comments (has been filetered from corpus): {no_deleted_comments}.')                  
                
create_corpus(all_post_titles)

print(corpus)
print(comment_urls)