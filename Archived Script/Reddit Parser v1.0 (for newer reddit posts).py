# import urllib library 
from urllib.request import urlopen 

#html parser
from html.parser import HTMLParser

#import dataclass
from dataclasses import dataclass

# import json 
import json 

#import html
import html

#import pandas
import pandas as pd

#import time
import time

# store the URL in url as  
# parameter for urlopen

# take_input = input("Please enter the url of the Reddit thread:")

# url = take_input.strip() + ".json"

url = "https://www.reddit.com/r/Brazil/comments/yhtimr/lula_stages_astonishing_comeback_to_beat_farright/.json"

title = url.split("/")[-2]
  
# store the response of URL 
response = urlopen(url) 
  
# storing the JSON response  
# from url in data 
data_json = str(json.loads(response.read()))
  
# print the json response 
# print(data_json) 

"""

This is parsing ONLY the OG post section, not the comment section.
The reason is that the buildin HTMLParser does not parse the correct 
code section of the OG's post, only the replies. 

"""
unescaped = html.unescape(data_json)

def remove_extras(x):
    '''
    This function removes the extras character leftover from
    the html parser.
    
    Args:
        x (str): any string.
    Returns:
        str: corrected string.
    '''
    y = x.replace("'", "").replace("}}]", "").replace("}}", "").replace("\\n\\n", "").replace('\'', "'").replace(" \'", "'").replace(":\'", "").replace("\\", "").replace("> ", "").strip()
    return y

poster_body = unescaped.split("-- SC_OFF --")[0]

poster_code = [remove_extras(poster_body.split("&#x200B;")[-1])]

def find_subreddit_name(ogpost: list) -> str:
    """
    Find the subreddit name of the post.
    """
    for code in ogpost:
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
    score: str
    upvote_ratio: float
    body: str

f = open('unwanted_values.txt', 'r')
unwanted_value = f.read()

og_post_with_table = []
og_post_without_table = []

for f in poster_code:
    """
    If it does starts with "[{kind: ", then the post has no tables.
    Therefore, if it doesnt, it does have a table.
    """
    if not f.startswith("[{kind: "):

        poster_post = poster_body.split("&#x200B;")[:-1]

        def check_for_tables (sections: list) -> list:
            '''
            This function checks whether OG post has a table.
            If there's a table, it will be return as the first index of
            the output list. Otherwise, the essay portion will be separated
            for each paragraph in the output list.  
            
            Args:
                sections (str): (poster_post) parsed code of the OG post.
            Returns:
                list: list separated by paragraph.
            '''
            all = []
            table = []
            essay = []
            together = []
            for section in sections:
                all.append(section.split("\\n\\n"))
            for a in all:
                for each in a:
                    if each.startswith("|") and each.endswith("|"):
                        table.append(each)
                    else:
                        essay.append(each)
            if len(table) >= 1:
                together = table + essay
            else:
                together.append(essay)
            return together

        check_for_tables(poster_post)

        table = check_for_tables(poster_post)[0]
        essays = check_for_tables(poster_post)[1:]
        # print(table)

        def get_columns(line: str, number: int) -> list:
            columns = []
            items = line[number].split("|")
            for item in items:
                if item != "" and item != ":-": 
                    columns.append(item)
            return columns

        def get_line_data(data: str):
            data_list = []
            for i in range(len(data)-1):
                column = get_columns(data, i)
                if len(column)>0:
                    data_list.append(column)
            return data_list

        def create_table(data: str):
            splitted_lines = get_line_data(data)
            header = splitted_lines[0]
            data = splitted_lines[1:]
            filename = title + "'s table.csv"
            with open(filename, 'w') as file:
                for header in header:
                    file.write(str(header)+', ')
                file.write('\n')
                for row in data:
                    for x in row:
                        file.write(str(x)+', ')
                    file.write('\n')

        # def table_to_csv(table: str):
        #     splitted_text = table.split("\\n")
        #     create_table(splitted_text)
        #     print("Table " + title + " has been created!")

        # table_to_csv(table)

        def essay_body (essays: list) -> str:
            """
            Return the OG Post essay portion as a string.
            """
            fixed = ""
            for essay in essays:
                if not essay.startswith("[{'kind'"):
                    e = essay.replace("**", "")
                    fixed += e
            return fixed

        og_essay = essay_body(essays)
    
        splitted_code = f.split(",")

        def OG_filtering_values (codes: list) -> parsed_values:
            og = []
            a = ""
            p_i = ""
            d = 0
            for code in codes:
                wanted_value = code.split(":")

                if wanted_value[0] == " author":
                    a = wanted_value[1].strip()

                elif wanted_value[0] == " author_fullname":
                    a_f = wanted_value[1].strip()

                elif wanted_value[0] == " name":
                    n = wanted_value[1].strip()

                elif wanted_value[0] == " created":
                    x = wanted_value[1].strip()
                    converted_time = str(time.strftime("%D %H:%M", time.localtime(float(x))))

                elif wanted_value[0] == " score":
                    u = str(wanted_value[1].strip())

                elif wanted_value[0] == " upvote_ratio":
                    d = str(wanted_value[1].strip())
        
            og = parsed_values(subreddit_name, a, a_f, n, p_i, converted_time, u, d, '"' + og_essay + '"')
            return og
        og_post_with_table = OG_filtering_values(splitted_code)

    else:
        splitted = f.split(" user_reports: [], ")
        parse_for_body = splitted[0].split(" selftext: ")
        body = parse_for_body[-1]
        if body[-1] == ",":
            body = body[:-1]
        split = splitted[-1].split(",")

        def OG_filtering_values (codes: list) -> parsed_values:
            og = []
            a = ""
            p_i = ""
            for code in codes:
                wanted_value = code.split(":")

                if wanted_value[0] == " author":
                    a = wanted_value[1].strip()

                elif wanted_value[0] == " author_fullname":
                    a_f = wanted_value[1].strip()

                elif wanted_value[0] == " name":
                    n = wanted_value[1].strip()

                elif wanted_value[0] == " created":
                    x = wanted_value[1].strip()
                    converted_time = str(time.strftime("%D %H:%M", time.localtime(float(x))))

                elif wanted_value[0] == " score":
                    u = str(wanted_value[1].strip())

                elif wanted_value[0] == " upvote_ratio":
                    d = str(wanted_value[1].strip())
        
            og = parsed_values(subreddit_name, a, a_f, n, p_i, converted_time, u, d, '"' + body + '"')
            return og
        
        og_post_without_table = OG_filtering_values(split)


"""

This is parsing ONLY the comments section, not the OG post.
The reason is that the buildin HTMLParser does not parse 
the correct code section of the OG's post,  only the replies. 

"""

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


def filtering_values(codes: list) -> list:
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

    if bool(og_post_with_table):
        everyone.append([og_post_with_table])
    elif bool(og_post_without_table):
        everyone.append([og_post_without_table])

    for code in codes[:-1]:
        a = ""
        a_count = 0
        a_f_count = 0
        c_t_count = 0
        u = ""
        helpme = []

        for values in code:
            for value in values: 
                wanted_value = value.split(":")
                leftover_body = ""

                if wanted_value[0] == " author" and a_count == 0:
                    a = wanted_value[1].strip()
                    a_count += 1

                elif wanted_value[0] == " author_fullname" and a_f_count == 0:
                    a_f = wanted_value[1].strip()
                    a_count +=1

                elif wanted_value[0] == " name":
                    n = wanted_value[1].strip()

                elif wanted_value[0] == " created_utc" and c_t_count == 0:
                    x = wanted_value[1].strip()
                    converted_time = str(time.strftime("%D %H:%M", time.localtime(float(x))))
                    c_t_count += 1

                elif wanted_value[0] == " parent_id":
                    p_i = (wanted_value[1].strip())

                elif wanted_value[0] == " score":
                    u = str(wanted_value[1].strip())

                # elif wanted_value[0] == " downs":
                #     d = str(wanted_value[1].strip())
                
                elif wanted_value[0] == " body" or wanted_value[0] not in unwanted_value:
                    if wanted_value[0] == " body":
                        b1 = str(wanted_value[1].strip()).replace('"', "")
                    if wanted_value[0] not in unwanted_value:
                        leftover_body = leftover_body + wanted_value[0]
                        helpme.append(leftover_body + ",")
                    b2 = "".join(helpme)
        b = '"' + b1 + b2 + '"'
        
        one_person = parsed_values(subreddit_name, a, a_f, n, p_i, converted_time, u, 0, b)
        everyone.append([one_person])
    return everyone

sorted_into_class = filtering_values(code_parser(code_body))

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
    everyone = []
    for value in values:
        one_person = []
        for v in value:
            one_person.append(v.subreddit)
            one_person.append(v.author)
            one_person.append(v.author_fullname)
            one_person.append(v.name)
            one_person.append(v.parent_id)
            one_person.append(v.created_time)
            one_person.append(v.score)
            one_person.append(v.upvote_ratio)
            one_person.append(v.body)
        everyone.append(one_person)
    return everyone

columns = ["Subreddit Name", "Author", "Author Fullname", "Name", "Parent ID", "Created Time", "Score", "Upvote Ratio", "Body"]

rows = prep_for_rows(sorted_into_class)

def create_table(c: list, r:list):
    columns = c
    rows = r
    filename = title + "'s post.csv"
    with open(filename, 'w', encoding="UTF-8") as file:
        for column in columns:
            file.write(str(column)+', ')
        file.write('\n')
        for row in rows:
            for x in row:
                file.write(str(x)+', ')
            file.write('\n')

create_table(columns, rows)

print("Post " + title + " has been parsed!")