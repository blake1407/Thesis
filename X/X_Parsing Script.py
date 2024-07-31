from bs4 import BeautifulSoup
import csv
import json
from datetime import datetime
import re
import sys, os


def extract_usernames(text):
    pattern = r'@\w+'
    usernames = re.findall(pattern, text)
    return usernames

with open(r'symposium.json', encoding='utf-8') as f:
    data = json.load(f)

for x in data:
    print(x)


# Prepare CSV filename
csv_filename = 'symposium.csv'
usernames = list(data.keys())
# print(len(usernames))

list_of_usernames = []
for name in usernames:
    for tweet_html in data[name]: 
        soup = BeautifulSoup(tweet_html, 'html.parser')
        # print(soup.prettify())
        x = extract_usernames(soup.get_text())
        for y in x:
            if y[1:] not in list_of_usernames:
                list_of_usernames.append(y[1:])
# print(list_of_usernames)

# Prepare CSV file and write headers
with open(csv_filename, 'w', newline='', encoding='utf-8') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(['Poster', 'Date', 'Tweet', 'No of Likes', 'No of Retweets', 'No of Replies', 'No of Views'])

    for name in list_of_usernames:
        try: 
            for tweet_html in data: 
                soup = BeautifulSoup(tweet_html, 'html.parser')
                # Extract all tweet texts
                tweets = soup.find_all(attrs={"data-testid": "tweetText"})
                tweet_texts = [tweet.get_text(strip=True) for tweet in tweets]
                # 35
                t = tweet_texts[0].strip() if tweet_texts else ''

                # Select the time value
                time_element = soup.find('time')
                if time_element:
                    #35
                    datetime_value = time_element['datetime']
                    dt = datetime.fromisoformat(datetime_value.replace("Z", "+00:00")) 
                    readable_time = dt.strftime("%B %d, %Y %I:%M %p")
                else:
                    readable_time = ''

                # Find all <div> elements with aria-label for likes, comments, and retweets
                div_elements = soup.find_all('div', attrs={"aria-label": True})
                likes = retweets = replies = 0
                views = 'N/A' 
                count = 0

                for div_element in div_elements:
                    aria_label_value = div_element['aria-label']
                    # print(aria_label_value)
                    if 'likes' in aria_label_value or ('bookmarks' in aria_label_value or 'views' in aria_label_value):
                        # print(aria_label_value)
                        values = aria_label_value.split(', ')
                        try:
                            replies = values[0].split(' ')[0]
                        except IndexError:
                            replies = 'N/A'
                        try:
                            retweets = values[1].split(' ')[0]
                        except IndexError:
                            retweets = 'N/A'
                        try:
                            likes = values[2].split(' ')[0]
                        except IndexError:
                            likes = 'N/A'
                        for v in values:
                            if 'views' in v:
                                views = v.split(' ')[0]
                        break

                # Write to CSV
                writer.writerow([name, readable_time, t, likes, retweets, replies, views])
        except Exception as e:
            print(f"Error processing tweet for user: {name}")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            continue

