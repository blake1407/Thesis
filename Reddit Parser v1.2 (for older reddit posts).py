# import urllib library 
from urllib.request import urlopen 

#html parser
from html.parser import HTMLParser
from dataclasses import dataclass
import json 
import html
import pandas as pd
import time
import re
from ast import literal_eval

#import csv, os, datetime for the log file
import csv
import os
from datetime import datetime
import time

import sys, os


csv_filename = "SCIENCE_12-01-23_12-31-23_Extracted Links.csv"
links = []

subredditName = csv_filename.split("_")[0].upper()
start = csv_filename.split("_")[1]
end = csv_filename.split("_")[2]

#Open a designated Extracted Links CSV
with open(csv_filename, 'r', newline='', encoding='utf-8') as file:
    csvFile = csv.reader(file)
    next(csvFile)
    for line in csvFile:
        if line:
            links.append(line[0])

# take_input = input("Please enter the url of the Reddit thread:")

for link in links:
    try: 
        url = link.strip() + ".json"

        """For testing
        links = []
        # url = links[36].strip() + ".json"
        url = "https://www.reddit.com/r/politics/comments/jnduqk/aoc_says_republicans_are_publicly_complicit_in/.json"
        # url = "https://www.reddit.com/r/ForTheKing/comments/bup98d/lore_store_unlocks_verified/.json"
        """

        title = url.split("/")[-2]
        time.sleep(5)
        # store the response of URL 
        response = urlopen(url) 

        #HANDLING TIME-OUT ERROR
        if response.getcode() == 429:
            time.sleep(int(response.headers["Retry-After"]))
        
        # storing the JSON response  
        # from url in data 
        data_json = str(json.loads(response.read()))
        
        # print the json response 
        # print(data_json) 
        #stole from Richa's code, remove emojis from text
        def deEmojify(text):
            emoj = re.compile("["
                u"\U0001F600-\U0001F64F"  # emoticons
                u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                u"\U0001F680-\U0001F6FF"  # transport & map symbols
                u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                u"\U00002500-\U00002BEF"  # chinese char
                u"\U00002702-\U000027B0"
                u"\U000024C2-\U0001F251"
                u"\U0001f926-\U0001f937"
                u"\U00010000-\U0010ffff"
                u"\u2640-\u2642" 
                u"\u2600-\u2B55"
                u"\u200d"
                u"\u23cf"
                u"\u23e9"
                u"\u231a"
                u"\ufe0f"  # dingbats
                u"\u3030"
                            "]+", re.UNICODE)
            return re.sub(emoj, '', text)
        """

        This is parsing ONLY the OG post section, not the comment section.
        The reason is that the buildin HTMLParser does not parse the correct 
        code section of the OG's post, only the replies. 

        """
        unescaped = html.unescape(data_json)

        def remove_extras(x: str):
            '''
            This function removes the extras character leftover from
            the html parser.
            
            Args:
                x (str): any string.
            Returns:
                str: corrected string.
            '''
            #remove html tidbits 
            #remove emojis
            x = deEmojify(x)
            x = x.replace("xad", "")
            x = x.replace("u200b", "")
            x = x.replace("'", "")
            x = x.replace("}}]", "")
            x = x.replace("}}", "")
            x = x.replace("\\t", " ")
            x = x.replace(" | ", ". ")
            x = x.replace('\'', "'")
            x = x.replace(" \'", "'")
            x = x.replace(":\'", "")
            x = x.replace("> ", "")
            x = x.replace("[", "")
            x = x.replace("]", "")
            x = x.replace("**", "")
            x = x.replace("*", "")
            x = x.replace("---", " ")
            x = x.replace("\\n", ". ")
            x = x.replace('\\', "")
            x = x.replace('~~', "")
            x = x.replace("_", "")
            x = x.replace("....", " ")
            x = x.replace("...", ". ")
            x = x.replace("..", ". ")
            x = x.replace(". . ", ". ")
            x = x.replace(".  . ", ". ")
            x = x.replace("^#1", ",").replace("^#2", ",").replace("^#3", ",").replace("^#4", ",").replace("^#5", ",")
            #remove user handles
            x = re.sub('@[^\s]+','',x)
            #regex to remove URLs
            x = re.sub(r'(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?', '', x)
            #remove unk tokens
            # x = re.sub('unk', '', x)
            x = x.replace("()", "")
            #removing anything that's not alphabets
            # x = re.sub('[^A-Z a-z]+', '', x)
            x = x.strip()
            return x

        poster_body = str(literal_eval(unescaped)[0])
        poster_code = remove_extras(poster_body)

        def find_subreddit_name(ogpost: list) -> str:
            """
            Find the subreddit name of the post.
            """
            ogpost_in_list = [ogpost]
            for code in ogpost_in_list:
                splitted = code.split(",")
            for split in splitted:
                if split.startswith(" subreddit:"):
                    subreddit_name = split.split(":")[-1].strip()
            return subreddit_name

        subreddit_name = find_subreddit_name(poster_code)

        @dataclass 
        class parsed_values:
            subreddit: str
            author: str
            author_fullname: str
            name: str
            parent_id: str
            created_time: str
            depth: int
            score: str
            upvote_ratio: float
            body: str
            children: int
            downvote: int

        f = open('unwanted_values.txt', 'r')
        unwanted_value = f.read()

        og_post_with_table = []
        og_post_without_table = []

        body = ""
        splitted = poster_body.split("'user_reports': []")
        parse_for_body = splitted[0].split("'selftext': ")
        body = remove_extras(parse_for_body[-1])
        if body.endswith(", "):
            body = body[:-2]
        if body.endswith(","):
            body = body[:-1]
        split = splitted[-1].split(",")

        #SKIP IF POST IS DELETED, REMOVED, OR HAS NO BODY
        if "deleted" in body or "removed" in body or not body:
            print(f"Post with no body was skipped: {url}")
            continue

        op_date_posted = ""
        op_likes = 0
        op_name = ""
        op_id = 0

        def OG_filtering_values (codes: list) -> parsed_values:
            global op_date_posted, op_likes, op_name, op_id
            og = []
            a = ""
            p_i = ""
            a_f = ""
            n = ""
            url = ""
            for code in codes:
                wanted_value = code.split(":")
                print(wanted_value)
                if wanted_value[0] == " 'author'":
                    a = wanted_value[1].replace("'", "").strip()
                    op_name = a

                elif wanted_value[0] == " 'removed_by_category'":
                    if not wanted_value[1]:
                        continue

                elif wanted_value[0] == " 'author_fullname'":
                    a_f = wanted_value[1].replace("'", "").strip()
                    op_id = a_f

                elif wanted_value[0] == " 'name'":
                    n = wanted_value[1].replace("'", "").strip()

                elif wanted_value[0] == " 'created'":
                    x = wanted_value[1].strip()
                    converted_time = str(time.strftime("%D %H:%M", time.localtime(float(x))))
                    op_date_posted = converted_time

                elif wanted_value[0] == " 'depth'":
                    depth = str(wanted_value[1].strip())

                elif wanted_value[0] == " 'score'":
                    u = str(wanted_value[1].strip())
                    op_likes = int(wanted_value[1].strip())

                elif wanted_value[0] == " 'upvote_ratio'":
                    d = str(wanted_value[1].strip())

                # elif wanted_value[0] == " 'url'":
                #     if "deleted" not in wanted_value[-1] or "removed" not in wanted_value[-1]:
                #         url = "https:" + str(wanted_value[-1].strip())
                #         if url[-1] == "'":
                #             url = url[:-1]

                elif wanted_value[0] == " 'title'":
                    if "deleted by user" in wanted_value[1]:
                        continue
                    else:
                        title = str(wanted_value[1].replace("'", "").strip())
                
            og = parsed_values(subreddit_name, a, a_f, n, p_i, converted_time, 0, u, d, '"'+ title.strip('"') + ". " + body.strip('"'), 0, 0)
            return og

        og_post_without_table = OG_filtering_values(split)

        code_body = []

        class MyHTMLParser(HTMLParser):

            def handle_data(self, data):
                if len(data) > 4:
                    if data.startswith("', '") or data.endswith("'body_html': '"):
                        # print("Code     :" + data)
                        code_body.append("Code     :" + data)
                    # else: 
                        # print("Data     :" + data)

        parser = MyHTMLParser()
        parsed = parser.feed(unescaped)

        def get_comments_body (body: str) -> str:
            split_head = body.split(" 'body': ")
            split_tail = split_head[-1].split(", 'edited': ")
            return remove_extras(split_tail[0])

        def code_parser(codes: list) -> list:
            '''
            This function plugs in the code_body list and parse them into
            [[[a: ..],[b: ..],[c: ..],[d: ..]], [[a: ..],[b: ..],[c: ..],[d: ..]]]
            
            Args:
                codes (str): list output from the html parser - code_body in this case.
            Returns:
                list: list of parsed value per person in the format above.
            '''

            raw = []
            rows = []
            for code in codes:
                values = [remove_extras(code)]
                raw.append(values)
            for r in raw:
                row = []
                for values in r:
                    value = values.strip().split(",")
                    for v in value:
                        V = v.split(",")
                        row.append(V)
                rows.append(row)
            return rows

        def filtering_values(code_bodies: list) -> list:
            '''
            This function takes the value from code_parser(code_body) and filter them to 
            the defined class parsed_values. If no value is found, "" will be used.
            
            Args:
                codes (str): list output from the code_parser(code_body) in this case.
            Returns:
                list: list of class parsed_values for each person.
            '''
            one_person = []
            everyone = []
            all_comments = []

            if bool(og_post_with_table):
                everyone.append([og_post_with_table])
            elif bool(og_post_without_table):
                everyone.append([og_post_without_table])

            codes = code_parser(code_bodies)
            for code in codes[1:]:
                a = ""
                a_count = 0
                a_f_count = 0
                c_t_count = 0
                u = ""
                a_f = ""
                # p_i = ""
                n = ""
                converted_time = ""
                for values in code:
                    for value in values:
                        wanted_value = value.split(":")
                        # print(wanted_value)

                        if wanted_value[0] == " author":
                            name = wanted_value[1].strip()
                            if name != 'AutoModerator':
                                a = name
                            a_count += 1

                        elif wanted_value[0] == " authorfullname":
                            a_f = wanted_value[1].strip()
                            a_count +=1

                        elif wanted_value[0] == " name":
                            n = wanted_value[1].strip()
                        
                        elif wanted_value[0] == " parentid":
                            p_i = (wanted_value[1].strip())

                        elif wanted_value[0] == " createdutc":
                            x = wanted_value[1].strip()
                            converted_time = str(time.strftime("%D %H:%M", time.localtime(float(x))))
                            c_t_count += 1

                        elif wanted_value[0] == " depth":
                            depth = (wanted_value[1].strip())

                        elif wanted_value[0] == " score":
                            u = str(wanted_value[1].strip())

                one_person = parsed_values(subreddit_name, a, a_f, n, p_i, converted_time, depth, u, 0, "", 0, 0)
                everyone.append([one_person])
            return everyone

        sorted_into_class = filtering_values(code_body)

        def fill_in_bodies(filtered: list) -> list:
            all_comments = []
            for code in code_body:
                all_comments.append(get_comments_body(code).replace('\n\n', ""))
            for people, comments in zip(filtered[1:-1], all_comments[1:-1]):
                for person in people:
                    person.body.strip('"')
                    c = comments.strip('"')
                    
                    person.body += '"'
                    person.body += c
                    person.body += '"'

        fill_in_bodies(sorted_into_class)

        #COUNT CHILDREN OF THE SAME PARENT ID
        # Create a dictionary to count occurrences of each parent_id
        parent_id_count = {}

        for lists in sorted_into_class:
            for person in lists:
                if person.parent_id in parent_id_count:
                    parent_id_count[person.parent_id] += 1
                else:
                    parent_id_count[person.parent_id] = 1

        # Print the count of each parent_id
        # for parent_id, count in parent_id_count.items():
        #     print(f'Parent ID: {parent_id}, Count: {count}')

        
        def prep_for_rows (values: list) -> list:
            '''
            This functions converts the parsed_value list of each commentor (sorted_into_class) 
            and return a list of rows value in order to be converted into csv.
            
            Args:
                values (list): list output from filtering_values(code_parser(code_body)) function
                            - sorted_into_class
            Returns:
                list: list of ordered parsed_values for each person to be converted into csv.
                        example: [[r/ name, author, author_fullname, name,...], [r/ name, author, author_fullname, name,...]]
            '''
            count = 0 
            everyone = []
            for value in values:
                one_person = []
                for v in value:
                    # Check if the body contains "removed", "deleted", or is blank
                    if "removed" in v.body or "deleted" in v.body or not v.body.strip('"'):
                        continue  # Skip this entry
                    replies = 0 

                    one_person.append(v.subreddit)
                    one_person.append(v.author)
                    one_person.append(v.author_fullname)
                    one_person.append(v.name)
                    one_person.append(v.parent_id)
                    one_person.append(v.created_time)
                    one_person.append(v.depth)
                    one_person.append(v.score)
                    one_person.append(v.upvote_ratio)

                    if count == 0:
                        one_person.append(len(sorted_into_class))

                    else: 
                        for parent_id, count in parent_id_count.items():
                            if v.name == parent_id:
                                replies = count

                        one_person.append(replies)
                    one_person.append(v.body)

                    count +=1

                everyone.append(one_person)
            return everyone


        columns = ["Subreddit Name", "Author", "Author Fullname", "Name", "Parent ID", "Created Time", "Depth", "Score", "Upvote Ratio", "Number of Replies", "Body"]

        rows = prep_for_rows(sorted_into_class)

        def create_table(title: str, columns: list, rows: list):
            filename = f"{title}'s post.csv"
            with open(filename, 'w', newline='', encoding="UTF-8") as file:
                writer = csv.writer(file)
                writer.writerow(columns)
                writer.writerows(rows)
            print(f"Post '{title}' has been parsed!")

        create_table(title, columns, rows)


        #LOG FiLE 
        def update_log(log_file):
            # Get current date and time
            now = datetime.now()
            current_time = now.strftime("%Y-%m-%d %H:%M:%S")

            # Check if log file exists
            file_exists = os.path.isfile(log_file)
            
            header = ["Scrape Time", "Subreddit Name", "Post Title", "Poster Account", "Poster ID", "Date Posted", "OP no of Likes", "Total Comments", "Post Link"]

            # Open log file in append mode
            with open(log_file, 'a', newline='') as file:
                writer = csv.writer(file)

                # Write header if log file is newly created
                if not file_exists:
                    writer.writerow(header)

                # Write current date and time along with an event description
                writer.writerow([current_time, subreddit_name, title, op_name, op_id, op_date_posted, op_likes, len(sorted_into_class), url + " "])

            print("Log file updated successfully.")

        if __name__ == "__main__":
            log_file = f"{subredditName}_{start}_{end}_LOG.csv"
            update_log(log_file)

        time.sleep(10)

        f.close()

    except Exception as e:
        print(f"An error occurred: {e}")

        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        time.sleep(10)
