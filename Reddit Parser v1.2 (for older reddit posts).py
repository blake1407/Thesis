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

# store the URL in url as  
# parameter for urlopen

take_input = input("Please enter the url of the Reddit thread:")

url = take_input.strip() + ".json"

"""For testing
# links = ['https://www.reddit.com/r/worldnews/comments/10anyyz/brazil_police_find_draft_decree_intended_to/ ', 'https://www.reddit.com/r/politics/comments/108e1yb/steve_bannon_and_maga_allies_promoted_fake_stolen/ ', 'https://www.reddit.com/r/EnoughMuskSpam/comments/107bes8/so_now_every_election_in_every_country_where/ ', 'https://www.reddit.com/r/worldnews/comments/zhcbik/it_hurts_my_soul_brazils_bolsonaro_ends/ ', 'https://www.reddit.com/r/worldnews/comments/zgx4o2/lula_ticket_sues_bolsonaro_and_sons_for_abuses/ ', 'https://www.reddit.com/r/UpliftingNews/comments/z3q10l/brazil_court_rejects_bolsonaros_election/ ', 'https://www.reddit.com/r/news/comments/z367ui/brazil_judge_fines_bolsonaro_allies_millions/ ', 'https://www.reddit.com/r/worldnews/comments/z35ika/brazils_electoral_court_rejects_bolsonaro/ ', 'https://www.reddit.com/r/anime_titties/comments/z35cpe/brazils_electoral_court_rejects_bolsonaro/ ', 'https://www.reddit.com/r/news/comments/z35byl/brazils_electoral_court_rejects_bolsonaro/ ', 'https://www.reddit.com/r/news/comments/z2itdj/bolsonaro_contests_brazil_election_loss_wants/ ', 'https://www.reddit.com/r/worldnews/comments/z23rem/brazils_bolsonaro_files_complaint_to_challenge/ ', 'https://www.reddit.com/r/MapPorn/comments/ytbkjy/what_if_brazil_had_an_electoral_college_like_the/ ', 'https://www.reddit.com/r/ActualPublicFreakouts/comments/ytarjk/forced_to_apologize_for_supporting_bolsonaro_in/ ', 'https://www.reddit.com/r/worldnews/comments/yr0d48/brazil_military_finds_no_evidence_of_election/ ', 'https://www.reddit.com/r/worldnews/comments/ympzxm/brazil_indonesia_and_drc_in_talks_to_form_opec_of/ ', 'https://www.reddit.com/r/tooktoomuch/comments/yl9amy/cocaine_or_just_not_very_happy_with_the_result_of/ ', 'https://www.reddit.com/r/worldnews/comments/yk8y7y/its_over_jair_bolsonaro_reportedly_accepts_defeat/ ', 'https://www.reddit.com/r/news/comments/yk51ik/its_over_jair_bolsonaro_reportedly_accepts_defeat/ ', 'https://www.reddit.com/r/worldnews/comments/yjlqup/brazil_election_bolsonaro_thanks_supporters/ ', 'https://www.reddit.com/r/news/comments/yjcjqz/brazils_bolsonaro_to_accept_election_loss_in/ ', 'https://www.reddit.com/r/worldnews/comments/yjcg07/brazils_bolsonaro_to_speak_today_wont_contest/ ', 'https://www.reddit.com/r/worldnews/comments/yj9f5m/bolsonaro_supporters_block_brazil_roads_for_a_2nd/ ', 'https://www.reddit.com/r/worldnews/comments/yj8ybt/brazil_judge_orders_police_to_clear_roadblocks_by/ ', 'https://www.reddit.com/r/soccer/comments/yj0mnf/juan_arango_i_get_sick_when_i_see_rightwing/ ', 'https://www.reddit.com/r/worldnews/comments/yirown/trucker_blockades_in_brazil_increase_in_wake_of/ ', 'https://www.reddit.com/r/walkaway/comments/yioy3k/was_the_election_stolen_in_brazil/ ', 'https://www.reddit.com/r/environment/comments/yioc7h/lula_cheered_for_new_climate_policies_after/ ', 'https://www.reddit.com/r/CrazyFuckingVideos/comments/yio1hr/elections_in_brazil/ ', 'https://www.reddit.com/r/worldnews/comments/yilfn0/brazils_bolsonaro_maintains_silence_after_lulas/ ', 'https://www.reddit.com/r/worldnews/comments/yiesf1/brazils_bolsonaro_yet_to_concede_after_lulas/ ', 'https://www.reddit.com/r/privacy/comments/yi3tbc/meta_and_tiktok_busted_for_actively_pushing_stop/ ', 'https://www.reddit.com/r/worldnews/comments/yi26ml/stop_the_steal_leader_ali_alexander_calls_for_a/ ', 'https://www.reddit.com/r/anime_titties/comments/yi17vw/biden_congratulates_lula_for_winning_free_fair/ ', 'https://www.reddit.com/r/politics/comments/yhxr0d/biden_congratulates_lula_on_brazil_election_win/ ', 'https://www.reddit.com/r/worldnews/comments/yhxmpt/brazil_election_bolsonaro_defeated_as_lula_makes/ ']

# url = links[36].strip() + ".json"
# print(url)
# url = "https://www.reddit.com/r/AmItheAsshole/comments/wyjbjs/aita_for_not_taking_down_my_video_that_was_a_gift/.json"
# url = "https://www.reddit.com/r/ForTheKing/comments/bup98d/lore_store_unlocks_verified/.json"
"""

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
    #remove emojis
    x = deEmojify(x)
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


new_op_body = ""
if body.startswith('"'):
    body = body[1:]
new_op_body += body
if not body.endswith('"'):
    new_op_body += '"'
if body.endswith('""'):
    new_op_body = new_op_body[:-2]

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
    for code in codes:
        wanted_value = code.split(":")
        if wanted_value[0] == " 'author'":
            a = wanted_value[1].replace("'", "").strip()
            op_name = a

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

        elif wanted_value[0] == " 'url'":
            url = "https:" + str(wanted_value[-1].strip())
            if url[-1] == "'":
                url = url[:-1]
        
    og = parsed_values(subreddit_name, a, a_f, n, p_i, converted_time, 0, u, d, '"'  + url + " " + new_op_body)
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
                    a = wanted_value[1].strip()
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

        one_person = parsed_values(subreddit_name, a, a_f, n, p_i, converted_time, depth, u, 0, "")
        everyone.append([one_person])
    return everyone

sorted_into_class = filtering_values(code_body)

def fill_in_bodies(filtered: list) -> list:
    all_comments = []
    for code in code_body:
        all_comments.append(get_comments_body(code).replace('\n\n', ""))
    for people, comments in zip(filtered[1:-1], all_comments[1:-1]):
        for person in people:
            if not person.body.startswith('"') and not comments.startswith('"'): 
                person.body += '"'
            person.body += comments
            if not person.body.endswith('"'):
                person.body += '"'

sorted_into_class = filtering_values(code_body)
fill_in_bodies(sorted_into_class)

#filter for only comments with a score of >=1000!!
def filter_for_1000_score (old_list: list) -> list:
    new_list = []
    for items in old_list:
        for item in items:
            if bool(item.score) and int(item.score) >= 1000:
                new_list.append(items)
    return new_list

above_1000_list = filter_for_1000_score(sorted_into_class)


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
            one_person.append(v.depth)
            one_person.append(v.score)
            one_person.append(v.upvote_ratio)
            one_person.append(v.body)
        everyone.append(one_person)
    return everyone


columns = ["Subreddit Name", "Author", "Author Fullname", "Name", "Parent ID", "Created Time", "Depth", "Score", "Upvote Ratio", "Body"]

rows = prep_for_rows(above_1000_list)

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

highest_depth_likes = 0
#find for highest depth
def find_highest_depth (above1000: list) -> int:
    global highest_depth_likes
    highest = 0
    for items in above1000:
        for item in items:
            if int(item.depth) > highest:
                highest = int(item.depth)
                highest_depth_likes = int(item.score)
    return highest
    
highest_depth = find_highest_depth(above_1000_list)

def update_log(log_file):
    # Get current date and time
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")

    # Check if log file exists
    file_exists = os.path.isfile(log_file)

    # Open log file in append mode
    with open(log_file, 'a', newline='') as file:
        writer = csv.writer(file)

        # Write header if log file is newly created
        if not file_exists:
            writer.writerow(["Scrape Time", "Subreddit Name", "Post Title", "Post Link", "Poster Account", "Poster ID", "Date Posted", "OP no of Likes", "Total Comments", "No of Comments >1000", "Highest Depth", "Highest Depth no of Likes"])

        # Write current date and time along with an event description
        # writer.writerow([current_time, subreddit_name, title, take_input + " ", op_name, op_id, op_date_posted, op_likes, len(sorted_into_class), len(above_1000_list), highest_depth, highest_depth_likes])
        writer.writerow([current_time, subreddit_name, title, url + " ", op_name, op_id, op_date_posted, op_likes, len(sorted_into_class), len(above_1000_list), highest_depth, highest_depth_likes])

    print("Log file updated successfully.")

if __name__ == "__main__":
    log_file = "log.csv"
    update_log(log_file)

f.close()