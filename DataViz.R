library(tidyverse)

df = read.csv("Cleaned Data/New_After_NN_Cleaned.csv")

df = df %>%
  select(c("Subject_ID", "Affiliation", "Followers", "Tweet_ID", "Affiliation_Contrast", "After_Dates", "After_Corpus", "After_Likes", "After_Retweets", "After_Replies", "After_Views"))

names(df) = c("Subject_ID", "Affiliation", "Number_Followers", "Tweet_ID", "Affiliation_Contrast", "Date", "Tweet", "Likes", "Retweets", "Replies", "Views")

df = df %>% 
  mutate(Tweet_split = strsplit(as.character(Tweet),
                                "\\.{1,}\\s{0,}|\\?{1,}\\s{0,}|\\!{1,}\\s{0,}")) %>%
  rowwise() %>%
  mutate(Tweet_split_number = list(1:length(Tweet_split))) %>%
  ungroup() %>%
  unnest(c(Tweet_split, Tweet_split_number)) %>%
  mutate(Segment_ID = Tweet_split_number-1) %>%
  distinct()

df_grouped = df %>% 
  group_by(Affiliation, Subject_ID, Tweet_ID) %>% 
  summarise(Sentences = n())

# df_grouped %>% 
#   ggplot(aes(x = Sentences, color = Affiliation, fill = Affiliation)) +
#   geom_density(alpha = 0.5)

# png("TweetLengthDensity.png", units="in", width=14, height=10, res=800)
# df_grouped %>%
#   ggplot(aes(x = Sentences, color = Affiliation, fill = Affiliation)) +
#   geom_density(alpha = 0.5)
# dev.off()
# 
# png("TweetLengthDensity_boxplot.png", units="in", width=14, height=10, res=800)
# df %>% 
#   group_by(Affiliation, Subject_ID, Tweet_ID) %>%
#   summarise(Sentences = n()) %>%
#   ggplot(aes(x = Affiliation, y = Sentences)) +
#   geom_boxplot(alpha = 0.5)
# dev.off()

quantile(df_grouped$Sentences)
# 75th is 4 overall

quantile(df_grouped$Sentences[df_grouped$Affiliation == "Republican Party"])
# 75th is 4 within Republicans

quantile(df_grouped$Sentences[df_grouped$Affiliation == "Democratic Party"])
# 75th is 3 within Democrats

mean(df_grouped$Sentences) + 2*sd(df_grouped$Sentences)
# 2 SDs above mean is 19.9992 or above
# 1 SDs above mean is 11.6344 or above

remain = df_grouped %>%
  filter(Sentences <= 19.9992)
counts = remain %>% group_by(Affiliation) %>% summarise(Count = n())

counts

png("TweetLengthDensity.png", units="in", width=14, height=10, res=800)
remain %>%
  ggplot(aes(x = Sentences, color = Affiliation, fill = Affiliation)) +
  geom_density(alpha = 0.5)
dev.off()

png("TweetLengthDensity_boxplot.png", units="in", width=14, height=10, res=800)
remain %>%
  # group_by(Affiliation, Subject_ID, Tweet_ID) %>%
  summarise(Sentences = n()) %>%
  ggplot(aes(x = Affiliation, y = Sentences)) +
  geom_boxplot(alpha = 0.5)
dev.off()

remain %>% 
  ggplot(aes(x = Sentences, color = Affiliation, fill = Affiliation)) +
  geom_density(alpha = 0.5)

# #randomly creates a vector of 66 numbers from 1-90
# index = sample(1:90, 66)
# 
# index
# 
# remain_gop = remain %>% filter(Affiliation == "Republican Party") %>% arrange(Sentences)
# 
# retain = c(remain_gop$Subject_ID[index], remain$Subject_ID[remain$Affiliation == "Democratic Party"])
# 
# retain
# 
# remain %>%
#   filter(Subject_ID %in% retain) %>%
#   ggplot(aes(x = Sentences, color = Affiliation, fill = Affiliation)) +
#   geom_density(alpha = 0.5)

summary(lm(Sentences ~ Affiliation, data = remain %>% 
             filter(Subject_ID %in% retain)))
