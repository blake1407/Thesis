from bs4 import BeautifulSoup
import csv
import json
from datetime import datetime
import re
import sys, os
import emoji
import time
import os
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
    #remove emojis
    x = deEmojify(x)
    x = emoji.replace_emoji(x, replace='')
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
    x = x.replace('\n', ' ')
    #remove user handles
    # x = re.sub('@[^\s]+','',x)
    #regex to remove URLs
    x = re.sub(r'(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?', '', x)
    #remove unk tokens
    # x = re.sub('unk', '', x)
    x = x.replace("()", "")
    #removing anything that's not alphabets
    # x = re.sub('[^A-Z a-z]+', '', x)
    x = x.strip()
    return x

def extract_usernames(text):
    pattern = r'@\w+'
    usernames = re.findall(pattern, text)
    return usernames

#replace as needed
folder_name = "X"
parsed_folder = "Parsed Data"
followers_path = os.path.join(folder_name, "followers_US.txt")

followers_US = []
# with open(r'''X\followers_US.txt''', 'r') as f: # PC
with open(followers_path,'r') as f:
    for line in f:
        if "@" in line:
            follower = line.strip()[1:]
            if follower not in followers_US:
                # print(follower)
                followers_US.append(follower)
f.close()

print(f"Number of followers to process: {len(followers_US)}")

count = 1

#Creating file paths
raw_html = os.path.join(folder_name, "US_tweets.json")
output_path = os.path.join(parsed_folder, "parsed_US.csv")

try: 
    with open(raw_html, encoding='utf-8') as f:
        data = json.load(f)
    
    # Prepare CSV filename
    usernames = list(data.keys())
    # print(len(usernames)

    # Prepare CSV file and write headers
    # csv_filename = r'''X\US_parsed.csv''' #PC
    with open(output_path, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Poster', 'Date', 'Tweet', 'No of Likes', 'No of Retweets', 'No of Replies', 'No of Views'])
        for name in followers_US: 
            try:
                for tweet_html in data[name]: 
                    print(f"Processing user: {name}")
                    all_username = []
                    all_time = []
                    all_likes = []
                    all_comments = []
                    all_retweets = []
                    all_views = []
                    
                    soup = BeautifulSoup(tweet_html, 'html.parser')

                    # Find all usernames
                    usernames = soup.find_all('a', attrs = {'aria-hidden': 'true'})
                    for username in usernames:
                        href_value = username.get('href', None)
                        if href_value and href_value not in all_username:
                            all_username.append(href_value[1:])
                        else:
                            print('No name found')

                    # Extract all tweet texts
                    tweets = soup.find_all(attrs={"data-testid": "tweetText"})
                    tweet_texts = [remove_extras(tweet.get_text(strip=False)) for tweet in tweets]

                    # Select the time value
                    time_element = soup.find_all('time')
                    for t in time_element:
                        # print(f'{key}: {len(time_element)}')
                        datetime_value = t['datetime']
                        dt = datetime.fromisoformat(datetime_value.replace("Z", "+00:00")) 
                        readable_time = dt.strftime("%B %d, %Y %I:%M %p")
                        all_time.append(readable_time)
                    # else:
                    #     readable_time = ''

                    # Find all <div> elements with aria-label for likes, comments, and retweets
                    div_elements = soup.find_all('div', attrs={"aria-label": True})

                    for div_element in div_elements:
                        aria_label_value = div_element['aria-label']
                        if 'likes' in aria_label_value or ('bookmarks' in aria_label_value or 'views' in aria_label_value):
                            values = aria_label_value.split(', ')

                            try:
                                replies = values[0].split(' ')[0]
                                all_comments.append(replies)
                            except IndexError:
                                replies = 'N/A'
                            try:
                                retweets = values[1].split(' ')[0]
                                all_retweets.append(retweets)
                            except IndexError:
                                retweets = 'N/A'
                            try:
                                likes = values[2].split(' ')[0]
                                all_likes.append(likes)
                            except IndexError:
                                likes = 'N/A'

                            for v in values:
                                if 'views' in v:
                                    views = v.split(' ')[0]
                                    all_views.append(views)
                                else:
                                    all_views.append('N/A')

                    # Write to CSV
                    for user, time, tweet, likes, retweets, comments, views in zip(all_username, all_time, tweet_texts, all_likes, all_retweets, all_comments, all_views):
                        writer.writerow([user, time, tweet, likes, retweets, comments, views])
                    print(f"Sucessfully processed user {name}")

            except Exception as e:
                print(f"Error processing user: {str(e)}")
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                continue
            finally:
                print(f'Current count: {count}')
                count+=1
                # if count > 100:
                #     break
except Exception as e:
    print(f"Error: {str(e)}")
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)