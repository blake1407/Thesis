## Overview
This repository contains a suite of scripts designed for scraping, processing, and analyzing tweets from selected X (formerly Twitter) accounts. The full thesis is available [here](https://udspace.udel.edu/items/692735ef-30b7-4223-b711-d0a60b6ff014). The workflow involves:

0. **Supplementary Materials Preparation**:
- ```NYT Metadata/NYT API - Metadata Scraper.ipynb``` collects metadata (e.g., people, places, and organizations mentioned) from articles published by NYT, created using the NYT API. Then, ```NYT Metadata/Creating List of Keywords.ipynb``` is used to display the top 10 most mentioned people, places, and organizations. This is crucial to further filter out irrelevant articles from other types of genre (e.g., economics, stocks reporting).
- ```X Trending Before and After/Selenium for Archive Twitter.ipynb``` scrapes top 5 trending terms and hashtags on X within a certain timeframe, automated using Selenium and BeautifulSoup. All information are scraped via [https://archive.twitter-trending.com](https://archive.twitter-trending.com).

1. **Tweet Scraping**:
- ```MINVERA_AdvancedScrape_X.ipynb``` scrapes tweets from provided X accounts, containing specified keywords and minimum number of likes within a certain frame. 
- Each scrape outputs a structured JSON file.

2. **Data Parsing and Anonymization**:
- ```Parsing_Script_for_Raw_HTML.ipynb``` extracts and processes relevant tweet data (likes, replies, retweets, views) from raw JSON files.
- Tweets are then anonymized and concatenated into two time periods: before and after 10/07/23.

3. **Tokenize Text**:
- ```Generating Tokens Details.ipynb``` further removes mentioned usernames, punctuations, stop words and apply sentence markers. Tweets are then tokenized and supplemented with tokens IDs (unique ID for each word in a corpus) and segment IDs (unique ID for each sentence in a corpus).
- ```Tokenized Data/BERT - Getting Embeddings.ipynb``` and ```Tokenized Data/BERT - Getting Embeddings.ipynb``` are then used to generate BERT and word2vec embeddings, using the pre-trained model available on [Hugging Face](https://huggingface.co/google-bert/bert-base-uncased).

4. **Sentiment Analysis**:
- Dictionary creation of stereotype-indicating words: ```Create Dictionary/Data compiling.ipynb``` is a modified SADCAT script that was adapted from R to Python (Gautam et al., under review).
  > From the list of base stereotypes created by Kurdi et al. (2019), words within the category of “warm”, “cold”, “incompetence”, “competence”, “Jewish”, “Muslim”, “Arabic”, and “Israeli” were processed to find their synonyms and antonyms using SADCAT (Semi-Automated Dictionary Creation for Analyzing Text; Nicolas et al., 2019; Nicolas et al., 2021; [https://github.com/gandalfnicolas/SADCAT](https://github.com/gandalfnicolas/SADCAT).
- Sentiment proportion generation: Positive and negative words are identified using the Linguistic Inquiry and Word Count toolbox (LIWC; Cohn et al., 2004).
- ```R Codes/Finalizing_models.R``` are to create hierarchical models to predict interactions of influencers' political affiliationa and their expressed sentiments and biases  throughout the timeline of the conflict.
- Models with significant interactions are decomposed and analyzed using ```R Codes/get_simslopes.R```, developed by Richa Gautam. 

5. **Implicit Association Analysis**:
- ```WEAT.ipynb``` (Word Embedding Association Test), sourced from Charlesworth et al. (2021), applies the method from Caliskan et al. (2017) to examine implicit biases and stereotype associations in tweets.
  
## Dependencies
- Python 3.x
- Selenium, BeautifulSoup (for scraping)
- Transformers (for BERT embeddings)
- WEAT implementation from Charlesworth et al. (2021)

## Usage
1. Run ```MINVERA_AdvancedScrape_X.ipynb``` to collect tweets. To start the script, fill in your X login information in ```your_email```, ```your_username```, ```your_password``` in the the 5th code block.
- Already scraped tweets that are relevant to the 2023 Israel-Hamas Conflict from selected political influencers are available in the ```Raw Data``` folder.
- Full list of influencers used are available in ```Supplementary Materials/Followers List & Categories - Accounts Kept.csv```.
3. Use ```Parsing_Script_for_Raw_HTML.ipynb``` to extract and anonymize data.
4. Tokenize text (using ```Generating Tokens Details.ipynb```) and generate BERT/word2vec word embeddings via ```Tokenized Data/BERT - Getting Embeddings.ipynb``` or ```Tokenized Data/BERT - Getting Embeddings.ipynb```. 
5. Apply WEAT to analyze implicit associations in the processed text.

## References
1. Caliskan, A., Bryson, J. J., & Narayanan, A. (2017). Semantics derived automatically from language corpora contain human-like biases. Science, 356(6334), 183–186. [https://doi.org/10.1126/science.aal4230](https://doi.org/10.1126/science.aal4230)
2. Charlesworth, T. E. S., Yang, V., Mann, T. C., Kurdi, B., & Banaji, M. R. (2021). Gender Stereotypes in Natural Language: Word Embeddings Show Robust Consistency Across Child and Adult Language Corpora of More Than 65 Million Words. Psychological Science, 32(2), 218–240. [https://doi.org/10.1177/0956797620963619](https://doi.org/10.1177/0956797620963619)
3. Cohn, M. A., Mehl, M. R., & Pennebaker, J. W. (2004). Linguistic Markers of Psychological Change Surrounding September 11, 2001. Psychological Science, 15(10), 687–693. [https://doi.org/10.1111/j.0956-7976.2004.00741.x](https://doi.org/10.1111/j.0956-7976.2004.00741.x)
4. Nicolas, G., Bai X, & Fiske, S. (2019). Automated Dictionary Creation for Analyzing Text: An Illustration from Stereotype Content. PsyArXiv (OSF Preprints). [https://doi.org/10.31234/osf.io/afm8k](https://doi.org/10.31234/osf.io/afm8k).
5. Nicolas, G., Bai, X., & Fiske, S. T. (2021). Comprehensive stereotype content dictionaries using a semi‐automated method. European Journal of Social Psychology, 51(1), 178–196. [https://doi.org/10.1002/ejsp.2724](https://doi.org/10.1002/ejsp.2724).
6. Kurdi, B., Mann, T. C., Charlesworth, T. E. S., & Banaji, M. R. (2019). The relationship between implicit intergroup attitudes and beliefs. Proceedings of the National Academy of Sciences, 116(13), 5862–5871. [https://doi.org/10.1073/pnas.1820240116](https://doi.org/10.1073/pnas.1820240116)
