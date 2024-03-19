# Reddit-JSON-Parser
This repository is an attempt at parsing reddit posts' data.

In order to access archived content from Reddit, use this website: https://search.pullpush.io
and input appropriate keywords (subreddit name, before and after timestamp).
(Brazil AND election*) OR (Brazil) OR (election*)

03/14/2024
1. Downvotes were no longer accessible per Reddit API changes a few years ago. Instead, using upvote_ratio may give us a idea of how much the downvote is, e.g: ratio of 0.75 for a post with a score of 100 means there are 25 downvotes. However, this value are only presented for the OP post and not the comments. 
Therefore, I'll remove the "Downvote" column, as they are now 0s.
2. For newer reddit posts, there would be a "-- SC_OFF --" in the json file to indicate the separation between the OP code and the comments. However, for older posts, this is not the case, so I'm fixing this bug.

03/18/2024 
Everything should work now. Added a log ability for the script.