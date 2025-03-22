This repository contains a suite of scripts designed for scraping, processing, and analyzing tweets from selected X (formerly Twitter) accounts focusing on the 2023 Israel-Hamas Conflict. The project aims to analyze sentiment and implicit bias in social media discourse. The full thesis is available [here](https://udspace.udel.edu/items/692735ef-30b7-4223-b711-d0a60b6ff014). An in-depth overview of the data analysis pipeline and results is available [here](https://blaketrn.notion.site/A-Psycholinguistic-Analysis-Of-Changes-In-Stereotypes-And-Hate-Speech-Associated-With-Muslim-And-Or--1beb8fab88a7800998a1db848f6e43c9).

## 📋 Overview
The workflow consists of several integrated components:
1. **Data Collection** - Scraping tweets and supplementary data
2. **Data Processing** - Parsing, anonymizing, and tokenizing text
3. **Semantic Analysis** - Generating embeddings and analyzing sentiment
4. **Bias Assessment** - Calculate implicit associations in discourse

## 🔧 Components
1. **Supplementary Materials Preparation**:
- **NYT Metadata Collection**
  - ```NYT Metadata/NYT API - Metadata Scraper.ipynb``` - Collects metadata from NYT articles using NYT API
  - ```NYT Metadata/Creating List of Keywords.ipynb``` - Identifies top mentioned entities for filtering
- **NYT Metadata Collection**
  - ```X Trending Before and After/Selenium for Archive Twitter.ipynb``` - Scrapes trending terms using Selenium and BeautifulSoup from [https://archive.twitter-trending.com](https://archive.twitter-trending.com)

2. **Tweet Collection**:
- ```MINVERA_AdvancedScrape_X.ipynb``` - Scrapes tweets containing specified keywords with minimum engagement metrics
  - Outputs structured JSON files for further processing

3. **Data Processing**:
- ```Parsing_Script_for_Raw_HTML.ipynb``` - Extracts and processes tweet data (likes, replies, retweets, views)
  - Anonymizes content and organizes by time period (before/after Oct 7, 2023)
- ```Generating Tokens Details.ipynb``` - Text preprocessing pipeline:
  - Removes usernames, punctuation, and stop words
  - Applies sentence markers
  - Tokenizes text with unique token and segment IDs

4. **Embedding Generation**:
- ```Tokenized Data/BERT - Getting Embeddings.ipynb``` - Generates BERT embeddings, using the pre-trained model available on [Hugging Face](https://huggingface.co/google-bert/bert-base-uncased).
- ```Tokenized Data/word2vec - Getting Embeddings.ipynb``` - Generates word2vec embeddings

5. **Sentiment Analysis**:
- **Dictionary Creation**
  - ```Create Dictionary/Data compiling.ipynb``` is a modified SADCAT script (Semi-Automated Dictionary Creation for Analyzing Text; Nicolas et al., 2019; Nicolas et al., 2021; [https://github.com/gandalfnicolas/SADCAT](https://github.com/gandalfnicolas/SADCAT)) that was adapted from R to Python (Gautam et al., under review).
  - Based on Kurdi et al. (2019) stereotype categories: warm, cold, incompetence, competence, Jewish, Muslim, Arabic, Israeli.
- **Sentiment proportion generation**
  - Positive and negative words are identified using the Linguistic Inquiry and Word Count toolbox (LIWC; Cohn et al., 2004).
- **Satistical Modeling**
  - ```R Codes/Finalizing_models.R``` - Creates hierarchical models to analyze sentiment patterns
  - ```R Codes/get_simslopes.R``` - Decomposes significant interactions (developed by Richa Gautam)

6. **Implicit Association Analysis**:
- ```WEAT.ipynb``` - Implements Word Embedding Association Test based on Caliskan et al. (2017) and Charlesworth et al. (2021)
  - Examines implicit biases and stereotype associations in tweet content
    
## 📦 Dependencies
- Python 3.x
- Data colection: Selenium, BeautifulSoup
- NLP processing: Transformers (for BERT embeddings)
- Statistical analysis: R libraries for hierarchical modeling
- WEAT implementation from Charlesworth et al. (2021)

## 🚀 Usage
1. **Data Collection**
- Run ```MINVERA_AdvancedScrape_X.ipynb``` to collect tweets
- Configure X login credentials in the 5th code block (``your_email``, ```your_username```, ```your_password```)
2. **Data Processing**
- Use ```Parsing_Script_for_Raw_HTML.ipynb``` to extract and anonymize collected data
- Process text with ```Generating Tokens Details.ipynb```
3. **Generate Embeddings**
- Use either BERT or word2vec embedding notebooks
4. **Analysis**
- Apply WEAT for implicit association analysis
- Use R scripts for statistical modeling of sentiment patterns

## 📁 Available Resources
- Pre-scraped tweets related to the 2023 Israel-Hamas Conflict are available in the ```Raw Data``` folder
- Full list of analyzed influencers available in ```Supplementary Materials/Followers List & Categories - Accounts Kept.csv```

## 📚 References
1. Caliskan, A., Bryson, J. J., & Narayanan, A. (2017). Semantics derived automatically from language corpora contain human-like biases. Science, 356(6334), 183–186. [https://doi.org/10.1126/science.aal4230](https://doi.org/10.1126/science.aal4230)
2. Charlesworth, T. E. S., Yang, V., Mann, T. C., Kurdi, B., & Banaji, M. R. (2021). Gender Stereotypes in Natural Language: Word Embeddings Show Robust Consistency Across Child and Adult Language Corpora of More Than 65 Million Words. Psychological Science, 32(2), 218–240. [https://doi.org/10.1177/0956797620963619](https://doi.org/10.1177/0956797620963619)
3. Cohn, M. A., Mehl, M. R., & Pennebaker, J. W. (2004). Linguistic Markers of Psychological Change Surrounding September 11, 2001. Psychological Science, 15(10), 687–693. [https://doi.org/10.1111/j.0956-7976.2004.00741.x](https://doi.org/10.1111/j.0956-7976.2004.00741.x)
4. Nicolas, G., Bai X, & Fiske, S. (2019). Automated Dictionary Creation for Analyzing Text: An Illustration from Stereotype Content. PsyArXiv (OSF Preprints). [https://doi.org/10.31234/osf.io/afm8k](https://doi.org/10.31234/osf.io/afm8k).
5. Nicolas, G., Bai, X., & Fiske, S. T. (2021). Comprehensive stereotype content dictionaries using a semi‐automated method. European Journal of Social Psychology, 51(1), 178–196. [https://doi.org/10.1002/ejsp.2724](https://doi.org/10.1002/ejsp.2724).
6. Kurdi, B., Mann, T. C., Charlesworth, T. E. S., & Banaji, M. R. (2019). The relationship between implicit intergroup attitudes and beliefs. Proceedings of the National Academy of Sciences, 116(13), 5862–5871. [https://doi.org/10.1073/pnas.1820240116](https://doi.org/10.1073/pnas.1820240116)
