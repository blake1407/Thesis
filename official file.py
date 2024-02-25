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

columns = ["Author", "Author Fullname", "Name", "Parent ID", "Created Time", "Upvote", "Downvote"]
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
        for values in code:
            for value in values: 
                wanted_value = value.split(":")

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
        
        one_person = parsed_values(a, a_f, n, p_i, converted_time, u, d)
        everyone.append(one_person)
    return everyone

sorted_into_class = filtering_values(code_parser(code_body))
