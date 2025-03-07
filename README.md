## Overview
This repository contains a suite of scripts designed for scraping, processing, and analyzing tweets from selected X (formerly Twitter) accounts. The workflow involves:

1. **Tweet Scraping**:
- MINVERA_AdvancedScrape_X.py scrapes tweets from specified X accounts on a daily basis.
- Each scrape outputs a structured JSON file.

2. **Data Parsing and Anonymization**:
- Parsing_Script_for_Raw_HTML.py extracts and processes relevant tweet data (likes, replies, retweets, views) from raw JSON files.
- Tweets are then anonymized and concatenated into two time periods: before and after 10/07/23.
- Each corpus is supplemented with BERT word embeddings for further analysis.

3. **Implicit Association Analysis**:
- The WEAT (Word Embedding Association Test) script, sourced from Charlesworth et al. (2021), applies the method from Caliskan et al. (2017) to examine implicit biases and stereotype associations in tweets.
  
## Dependencies
- Python 3.x
- Selenium, BeautifulSoup (for scraping)
- Transformers (for BERT embeddings)
- WEAT implementation from Charlesworth et al. (2021)

## Usage
1. Run MINVERA_AdvancedScrape_X.py to collect tweets.
2. Use Parsing_Script_for_Raw_HTML.py to extract and anonymize data.
3. Apply WEAT to analyze implicit associations in the processed text.

## References
1. Caliskan, A., Bryson, J. J., & Narayanan, A. (2017). Semantics derived automatically from language corpora contain human-like biases. Science, 356(6334), 183–186. [https://doi.org/10.1126/science.aal4230](https://doi.org/10.1126/science.aal4230)
2. Charlesworth, T. E. S., Yang, V., Mann, T. C., Kurdi, B., & Banaji, M. R. (2021). Gender Stereotypes in Natural Language: Word Embeddings Show Robust Consistency Across Child and Adult Language Corpora of More Than 65 Million Words. Psychological Science, 32(2), 218–240. [https://doi.org/10.1177/0956797620963619](https://doi.org/10.1177/0956797620963619)
