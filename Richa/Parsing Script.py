from bs4 import BeautifulSoup
import csv
import json
from datetime import datetime

# Load JSON data
with open(r'Richa\Brazil_tweets.json', encoding='utf-8') as f:
    data = json.load(f)

usernames = list(data.keys())  # Assuming keys are usernames
print(usernames)
# Prepare CSV filename
csv_filename = 'Brazil_parsed_data.csv'  # Name of the CSV file

# Prepare CSV file and write headers
with open(csv_filename, 'w', newline='', encoding='utf-8') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(['Poster', 'Date', 'Tweet', 'Likes', 'Retweets', 'Comments', 'Views'])

    for name in usernames:
        for tweet_html in data[name]:  # Assuming data[name] contains HTML strings
            soup = BeautifulSoup(tweet_html, 'html.parser')

            # Select elements with data-testid="tweetText"
            tweet_texts = soup.find_all(attrs={"data-testid": "tweetText"})
            tweets_and_replies = tweet_texts.get_text()
            # t = tweet_texts[0].get_text() if tweet_texts else ''

            # Select the time value
            time_element = soup.find('time')
            if time_element:
                datetime_value = time_element['datetime']
                dt = datetime.fromisoformat(datetime_value.replace("Z", "+00:00")) 
                readable_time = dt.strftime("%B %d, %Y %I:%M %p")
            else:
                readable_time = ''

            # Find all <div> elements with aria-label for likes, comments, and retweets
            div_elements = soup.find_all('div', attrs={"aria-label": True})
            likes = retweets = replies = views = 0 

            for div_element in div_elements:
                aria_label_value = div_element['aria-label']
                if 'likes' in aria_label_value:
                    values = aria_label_value.split(', ')
                    replies = values[0].split(' ')[0]
                    retweets = values[1].split(' ')[0] if len(values) > 1 else 0
                    likes = values[2].split(' ')[0] if len(values) > 2 else 0
                    views = values[3].split(' ')[0] if len(values) > 3 else 0

            # Write to CSV
            writer.writerow([name, readable_time, t, likes, retweets, replies, views])  # Pass as a list

print("CSV file written successfully.")



"""
f = open('Richa\Brazil_tweets.json',)

data = json.load(f)

usernames = []

for i in data:
    usernames.append(i)


# Prepare CSV filename
csv_filename = 'Brazil_parsed_data.csv'  # Name of the CSV file

# Prepare CSV file and write headers
with open(csv_filename, 'w', newline='', encoding='utf-8') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(['Poster', 'Date', 'Tweet', 'Likes', 'Retweets', 'Comments', 'Views'])

    for name in usernames:
        for i in data[name]:
            soup = BeautifulSoup(i, 'html.parser')

            # Select elements with data-testid="tweetText"
            tweet_texts = soup.find_all(attrs={"data-testid": "tweetText"})
            #Get all tweets including comments
            for tweet in tweet_texts:
                # print(tweet.get_text())
                t = tweet.get_text()
            
            #Select all time values
            time_element = soup.find('time')
            # Extract the datetime attribute
            if time_element:
                datetime_value = time_element['datetime']
                dt = datetime.fromisoformat(datetime_value.replace("Z", "+00:00")) 
                readable_time = dt.strftime("%B %d, %Y %I:%M %p")
                # print(readable_time)

            # Find all <div> elements with aria-label for likes, comments, and retweets
            div_elements = soup.find_all('div', attrs={"aria-label": True})
            likes = retweets = replies = views = 0
            for div_element in div_elements:
                aria_label_value = div_element['aria-label']
                if 'likes' in aria_label_value:
                    values = aria_label_value.split(', ')
                    replies = values[0].split(' ')[0]
                    retweets = values[1].split(' ')[0] if len(values) > 1 else 0
                    likes = values[2].split(' ')[0] if len(values) > 2 else 0
                    views = values[3].split(' ')[0] if len(values) > 3 else 0

                    # print(values)                
            # print('\n')

            writer.writerow([name, readable_time, t, likes, retweets, replies, views])   

f.close()


"""