"MINVERA_AdvancedScrape_X" script is used to scrape tweets from selected X accounts by day, outputed in a JSON file per scrape.
"Parsing Script for Raw HTML" script is used parse raw JSON files into readable tweets and relevant stats for each accounts (i.e., likes, replies, retweets, views).
Then, tweets are then anonymized and concatenated by time period (before and after 10/07/23), supplemented with BERT word embeddings for each corpus.
"WEAT" script, obtained from Charlesworth et al., (2021), is used to perform Single-Category Word Embeddings Association Test (Caliskan et al., 2017) for implicit associations of stereotypes in tweets. 
