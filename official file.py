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
url = "https://www.reddit.com/r/ForTheKing/comments/18g811y/class_base_stat_and_starting_equipment_infodump/.json"
  
# store the response of URL 
response = urlopen(url) 
  
# storing the JSON response  
# from url in data 
data_json = str(json.loads(response.read()))
  
# print the json response 
# print(data_json) 


"""

This is an attempt at parsing ONLY the comments section, not the OG post.
The reason is that the buildin HTMLParser does not parse the correct code section of the OG's post, 
only the replies. 

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
unescaped = html.unescape(data_json)
parsed = parser.feed(unescaped)

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
                  ' author_flair_background_color', ' collapsed_because_crowd_control']

columns = ["Author", "Author Fullname", "Name", "Parent ID", "Created Time", "Upvote", "Downvote", "Body"]
rows = []

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
        everyone.append(one_person)
    return everyone

sorted_into_class = filtering_values(code_parser(code_body))



