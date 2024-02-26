# import urllib library 
from urllib.request import urlopen 

#import beautifulsoup
from bs4 import BeautifulSoup 

#html parser
from html.parser import HTMLParser
from html.entities import name2codepoint

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

url = "https://www.reddit.com/r/AITAH/comments/1b06vi7/my_childs_teacher_made_a_sexual_comment_towards/.json"

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
    y = x.replace("'", "").replace("}}]", "").replace("}}", "").replace("\\n\\n", "").replace('\'', "'").replace(" \'", "'").replace(":\'", "").strip()
    return y

poster_body = unescaped.split("-- SC_OFF --")[0]

poster_code = [remove_extras(poster_body.split("&#x200B;")[-1])]

@dataclass 
class parsed_values:
    author: str
    author_fullname: str
    name: str
    parent_id: str
    created_time: str
    upvote: str
    downvote: str
    body: str

unwanted_value = ['Code     ', ' likes', ' suggested_sort', ' banned_at_utc', ' view_count', ' archived', 
                  ' no_follow', ' is_crosspostable', ' pinned', ' over_18', ' all_awardings', ' awarders', 
                  ' media_only', ' can_gild', ' spoiler', ' locked', ' author_flair_text', ' treatment_tags', 
                  ' visited', ' removed_by', ' num_reports', ' distinguished', ' subreddit_id', ' author_is_blocked', 
                  ' mod_reason_by', ' removal_reason', ' link_flair_background_color', ' id', ' is_robot_indexable', 
                  ' num_duplicates', ' report_reasons', ' author', ' discussion_type', ' num_comments', ' send_replies', 
                  ' media', ' contest_mode', ' author_patreon_flair', ' author_flair_text_color', ' permalink', 
                  ' whitelist_status', ' stickied', ' url', ' subreddit_subscribers', ' num_crossposts', 
                  ' mod_reports', ' is_video', ' before', ' {kind', ' data: {after', ' dist', ' modhash', ' geo_filter', 
                  ' children', ' data', ' approved_at_utc', ' author_is_blocked', ' comment_type', ' awarders', 
                  ' mod_reason_by', ' banned_by', ' author_flair_type', ' total_awards_received', ' subreddit', 
                  ' author_flair_template_id', ' likes', ' replies', ' data', ' dist', ' modhash', ' geo_filter', 
                  ' children', ' data', ' approved_at_utc', ' author_is_blocked', ' comment_type', ' awarders', 
                  ' mod_reason_by', ' banned_by', ' author_flair_type', ' total_awards_received', ' subreddit', 
                  ' author_flair_template_id', ' likes', ' replies', ' user_reports', ' saved', ' id', ' banned_at_utc', 
                  ' mod_reason_title', ' gilded', ' archived', ' collapsed_reason_code', ' no_follow', ' author', 
                  ' can_mod_post', ' created_utc', ' send_replies', ' parent_id', ' score', ' author_fullname', 
                  ' removal_reason', ' approved_by', ' mod_note', ' all_awardings', ' edited', ' top_awarded_type', 
                  ' author_flair_css_class', ' name', ' is_submitter', ' downs', ' author_flair_richtext', 
                  ' author_patreon_flair', ' body_html', ' body', ' collapsed', ' gildings', ' collapsed_reason',
                  ' associated_award', ' author_premium', ' link_id', ' unrepliable_reason', ' score_hidden',
                  ' subreddit_type', ' created', ' subreddit_name_prefixed', ' controversiality', ' depth',
                  ' author_flair_background_color', ' collapsed_because_crowd_control', ' link_flair_template_id']

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

        def table_to_csv(table: str):
            splitted_text = table.split("\\n")
            create_table(splitted_text)
            print("Table " + title + " has been created!")

        table_to_csv(table)

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

                elif wanted_value[0] == " ups":
                    u = str(wanted_value[1].strip())

                elif wanted_value[0] == " downs":
                    d = str(wanted_value[1].strip())
        
            og = parsed_values(a, a_f, n, p_i, converted_time, u, d, og_essay)
            return og
        og_post_with_table = OG_filtering_values(splitted_code)

    else:
        splitted = f.split(" user_reports: [], ")
        parse_for_body = splitted[0].split(" selftext: ")
        body = parse_for_body[-1]
        split = splitted[-1].split(",")

        print(body)

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

                elif wanted_value[0] == " ups":
                    u = str(wanted_value[1].strip())

                elif wanted_value[0] == " downs":
                    d = str(wanted_value[1].strip())
        
            og = parsed_values(a, a_f, n, p_i, converted_time, u, d, body)
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

def remove_utfextras(x):
    '''
    This function removes misread symbols of utf-8 encoding.
    
    Args:
        x (str): any string.
    Returns:
        str: corrected string.
    '''
    y = x.replace("â€œ", "\"").replace('â€¢', '·').replace("â€", "\"").replace("â€™", "'").replace('â€', "'").replace("Â£", "£")
    return y                                                                                       

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

                elif wanted_value[0] == " ups":
                    u = str(wanted_value[1].strip())

                elif wanted_value[0] == " downs":
                    d = str(wanted_value[1].strip())
                
                elif wanted_value[0] == " body" or wanted_value[0] not in unwanted_value:
                    if wanted_value[0] == " body":
                        b1 = str(wanted_value[1].strip()).replace('"', "")
                    if wanted_value[0] not in unwanted_value:
                        leftover_body = leftover_body + wanted_value[0]
                        helpme.append(leftover_body)
                    b2 = "".join(helpme)
        b = b1 + b2
        
        one_person = parsed_values(a, a_f, n, p_i, converted_time, u, d, b)
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
                example: [[author, author_fullname, name,...], [author, author_fullname, name,...]]
    '''
    everyone = []
    for value in values:
        one_person = []
        for v in value:
            one_person.append(v.author)
            one_person.append(v.author_fullname)
            one_person.append(v.name)
            one_person.append(v.parent_id)
            one_person.append(v.created_time)
            one_person.append(v.upvote)
            one_person.append(v.downvote)
            one_person.append(v.body)
        everyone.append(one_person)
    return everyone

columns = ["Author", "Author Fullname", "Name", "Parent ID", "Created Time", "Upvote", "Downvote", "Body"]

rows = prep_for_rows(sorted_into_class)

def create_table(c: list, r:list):
    columns = c
    rows = r
    filename = title + "'s post.csv"
    with open(filename, 'w', encoding="utf-8") as file:
        for column in columns:
            file.write(str(column)+', ')
        file.write('\n')
        for row in rows:
            for x in row:
                file.write((x)+', ')
            file.write('\n')

create_table(columns, rows)

print("Post " + title + " has been parsed!")