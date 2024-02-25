# import urllib library 
from urllib.request import urlopen 

#import beautifulsoup
from bs4 import BeautifulSoup 

#html parser
from html.parser import HTMLParser
from html.entities import name2codepoint

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

# def parse_html(html):
#     elem = BeautifulSoup(html, features="html.parser")
#     text = ''
#     for e in elem.descendants:
#         if isinstance(e, str):
#             text += e.get_text().strip()
#         elif e.name in ['span']:
#             text += ' '
#         elif e.name in ['br',  'p', 'h1', 'h2', 'h3', 'h4', 'tr', 'th', 'div']:
#             text += '\n'
#         elif e.name == 'li':
#             text += '\n- '
#     return text

code_body = []

class MyHTMLParser(HTMLParser):
    # def handle_starttag(self, tag, attrs):
    #     print("Start tag:", tag)
    #     for attr in attrs:
    #         print("     attr:", attr)

    # def handle_endtag(self, tag):
    #     print("End tag  :", tag)

    def handle_data(self, data):
        if len(data) > 4:
            if data.startswith("',") or data.endswith("'body_html': '"):
                # print("Code     :" + data)
                code_body.append("Code     :" + data)
            # else: 
                # print("Data     :" + data)

    # def handle_comment(self, data):
    #     print("Comment  :", data)

    # def handle_entityref(self, name):
    #     c = chr(name2codepoint[name])
    #     print("Named ent:", c)

    # def handle_charref(self, name):
    #     if name.startswith('x'):
    #         c = chr(int(name[1:], 16))
    #     else:
    #         c = chr(int(name))
    #     print("Num ent  :", c)

    # def handle_decl(self, data):
    #     print("Decl     :", data)

parser = MyHTMLParser()
unescaped = html.unescape(data_json)
parsed = parser.feed(unescaped)

columns = ["Author", "Author Fullname", "Name", "Created Time", "Parent ID", "Upvote", "Downvote"]
rows = []

def code_parser(codes: list) -> list:
    rows = []
    for code in codes:
        row = []
        for values in code:
            value = values.strip().replace("'", "").replace("}}]", "").replace("}}", "").replace("\\n\\n", "").split(",")
            row.append(value)
        rows.append(row)
    return rows

def filtering_values(codes: list) -> list:
    code_s = code_parser(codes)
    everyone = []
    for code in code_s:
        one_person = []
        for values in code:
            for value in values: 
                if value.startswith("author:"):
                    wanted_value = value.split(":")
                    one_person.append(wanted_value[1].strip())
                if value.startswith("name:"):
                    wanted_value = value.split(":")
                    one_person.append(wanted_value[1].strip())
                if value.startswith("created_utc:"):
                    wanted_value = value.split(":")
                    x = wanted_value[1].strip()
                    converted_time = time.strftime("%D %H:%M", time.localtime(float(x)))
                    one_person.append(converted_time)
                if value.startswith("parent_id:"):
                    wanted_value = value.split(":")
                    one_person.append(wanted_value[1].strip())
                if value.startswith("ups:"):
                    wanted_value = value.split(":")
                    one_person.append(wanted_value[1].strip())
                if value.startswith("downs:"):
                    wanted_value = value.split(":")
                    one_person.append(wanted_value[1].strip())
        everyone.append(one_person)
    return everyone

print(filtering_values(code_body))
# print(filtering_values(code_body))
# print(type(code_parser(code_body)))
# print(code_parser(code_body))
# print(code_parser(code_body)[2])