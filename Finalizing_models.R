library(tidyverse)
library(lmerTest)
library(lme4)
library(car)
library(buildmer)
library(interactions)
library(glmnet)
library(dplyr)
library(lubridate)

# Function to create the date numbering
create_date_numbering <- function(df, column, start, direction = "backward") {
  df %>%
    mutate(
      # Use !!sym() to handle column names passed as strings
      Date = as_date(!!sym(column), format = "%B %d, %Y %I:%M %p"),
      
      # Conditional logic for date indexing
      Date_Index = if(direction == "backward") {
        -as.numeric(difftime(as.Date(start), Date, units = "days"))
      } else {
        as.numeric(difftime(Date, as.Date(start), units = "days"))
      }
    )
}

# Read and process pre-data
data_pre <- read.csv("Before_Stereotypes_Proportion_LIWC_Hate.csv") %>%
  mutate(Condition_Contrast = -0.5) %>%
  create_date_numbering("Before_Dates", "2023-10-06", direction = "backward") %>% filter(Date_Index >= -365) # Ensure min index is at least -365

# Read and process post-data
data_post <- read.csv("After_Stereotypes_Proportion_LIWC_Hate.csv") %>%
  mutate(Condition_Contrast = 0.5) %>%
  create_date_numbering("After_Dates", "2023-10-07", direction = "forward")

# Optional: Verify the results
head(data_pre[, c("Before_Dates", "Date", "Date_Index")])
head(data_post[, c("After_Dates", "Date", "Date_Index")])

names(data_pre)

data = merge(data_pre, data_post, 
             by=names(data_pre)[names(data_pre) %in% names(data_post)],
             all = TRUE) %>% 
  distinct()

data = data %>%
  mutate(ethorace_israelijewish = prop_Israeli + prop_Jewish,
         ethorace_arabicmuslim = prop_Arabic + prop_Muslim) %>%
  mutate(Ethnorace = ifelse(ethorace_israelijewish > ethorace_arabicmuslim, -0.5,
                            ifelse(ethorace_arabicmuslim > ethorace_israelijewish, 0.5, NA)))

data = data %>%
  mutate(Militant = ifelse(prop_IDF > prop_Hamas, -0.5,
                            ifelse(prop_Hamas > prop_IDF, 0.5, NA)))

#Complitcated intercept
mod_negsentiment = lmer(tone_neg ~ Ethnorace*Affiliation_Contrast*Condition_Contrast + (1+Ethnorace*Condition_Contrast|Subject_ID), data=data)
summary(mod_negsentiment)

mod_negsentiment = lmer(tone_neg ~ Ethnorace*Affiliation_Contrast*Date_Index + (1+Ethnorace*Date_Index|Subject_ID), data=data)
summary(mod_negsentiment)

mod_negsentiment = lmer(tone_neg ~ Militant*Affiliation_Contrast*Condition_Contrast + (1+Militant*Condition_Contrast|Subject_ID), data=data)
summary(mod_negsentiment)

mod_negsentiment = lmer(tone_neg ~ Militant*Affiliation_Contrast*Date_Index + (1+Militant*Date_Index|Subject_ID), data=data)
summary(mod_negsentiment)

#Less Complitcated intercept
mod_negsentiment = lmer(tone_neg ~ Ethnorace*Affiliation_Contrast*Condition_Contrast + (1|Subject_ID), data=data)
summary(mod_negsentiment)

mod_negsentiment = lmer(tone_neg ~ Ethnorace*Affiliation_Contrast*Date_Index + (1|Subject_ID), data=data)
summary(mod_negsentiment)

mod_negsentiment = lmer(tone_neg ~ Militant*Affiliation_Contrast*Condition_Contrast + (1|Subject_ID), data=data)
summary(mod_negsentiment)

mod_negsentiment = lmer(tone_neg ~ Militant*Affiliation_Contrast*Date_Index + (1|Subject_ID), data=data)
summary(mod_negsentiment)



#Complitcated intercept
mod_possentiment = lmer(tone_pos ~ Ethnorace*Affiliation_Contrast*Condition_Contrast + (1+Ethnorace*Condition_Contrast|Subject_ID), data=data)
summary(mod_possentiment)

mod_possentiment = lmer(tone_pos ~ Ethnorace*Affiliation_Contrast*Date_Index + (1+Ethnorace*Date_Index|Subject_ID), data=data)
summary(mod_possentiment)

mod_possentiment = lmer(tone_pos ~ Militant*Affiliation_Contrast*Condition_Contrast + (1+Militant*Condition_Contrast|Subject_ID), data=data)
summary(mod_possentiment)

mod_possentiment = lmer(tone_pos ~ Militant*Affiliation_Contrast*Date_Index + (1+Militant*Date_Index|Subject_ID), data=data)
summary(mod_possentiment)

#Less Complitcated intercept
mod_possentiment = lmer(tone_pos ~ Ethnorace*Affiliation_Contrast*Condition_Contrast + (1|Subject_ID), data=data)
summary(mod_possentiment)

mod_possentiment = lmer(tone_pos ~ Ethnorace*Affiliation_Contrast*Date_Index + (1|Subject_ID), data=data)
summary(mod_possentiment)

mod_possentiment = lmer(tone_pos ~ Militant*Affiliation_Contrast*Condition_Contrast + (1|Subject_ID), data=data)
summary(mod_possentiment)

mod_possentiment = lmer(tone_pos ~ Militant*Affiliation_Contrast*Date_Index + (1|Subject_ID), data=data)
summary(mod_possentiment)



#Complitcated intercept
mod_warmstereotype = lmer(prop_Warm ~ Ethnorace*Affiliation_Contrast*Condition_Contrast + (1+Ethnorace*Condition_Contrast|Subject_ID), data=data)
summary(mod_warmstereotype)

mod_warmstereotype = lmer(prop_Warm ~ Ethnorace*Affiliation_Contrast*Date_Index + (1+Ethnorace*Date_Index|Subject_ID), data=data)
summary(mod_warmstereotype)

mod_warmstereotype = lmer(prop_Warm ~ Militant*Affiliation_Contrast*Condition_Contrast + (1+Militant*Condition_Contrast|Subject_ID), data=data)
summary(mod_warmstereotype)

mod_warmstereotype = lmer(prop_Warm ~ Militant*Affiliation_Contrast*Date_Index + (1+Militant*Date_Index|Subject_ID), data=data)
summary(mod_warmstereotype)

#Less Complitcated intercept
mod_warmstereotype = lmer(prop_Warm ~ Ethnorace*Affiliation_Contrast*Condition_Contrast + (1|Subject_ID), data=data)
summary(mod_warmstereotype)

mod_warmstereotype = lmer(prop_Warm ~ Ethnorace*Affiliation_Contrast*Date_Index + (1|Subject_ID), data=data)
summary(mod_warmstereotype)

mod_warmstereotype = lmer(prop_Warm ~ Militant*Affiliation_Contrast*Condition_Contrast + (1|Subject_ID), data=data)
summary(mod_warmstereotype)

mod_warmstereotype = lmer(prop_Warm ~ Militant*Affiliation_Contrast*Date_Index + (1|Subject_ID), data=data)
summary(mod_warmstereotype)


#Complitcated intercept
mod_coldstereotype = lmer(prop_Cold ~ Ethnorace*Affiliation_Contrast*Condition_Contrast + (1+Ethnorace*Condition_Contrast|Subject_ID), data=data)
summary(mod_coldstereotype)

mod_coldstereotype = lmer(prop_Cold ~ Ethnorace*Affiliation_Contrast*Date_Index + (1+Ethnorace*Date_Index|Subject_ID), data=data)
summary(mod_coldstereotype)

mod_coldstereotype = lmer(prop_Cold ~ Militant*Affiliation_Contrast*Condition_Contrast + (1+Militant*Condition_Contrast|Subject_ID), data=data)
summary(mod_coldstereotype)

mod_coldstereotype = lmer(prop_Cold ~ Militant*Affiliation_Contrast*Date_Index + (1+Militant*Date_Index|Subject_ID), data=data)
summary(mod_coldstereotype)

#Less Complitcated intercept
mod_coldstereotype = lmer(prop_Cold ~ Ethnorace*Affiliation_Contrast*Condition_Contrast + (1|Subject_ID), data=data)
summary(mod_coldstereotype)

mod_coldstereotype = lmer(prop_Cold ~ Ethnorace*Affiliation_Contrast*Date_Index + (1|Subject_ID), data=data)
summary(mod_coldstereotype)

mod_coldstereotype = lmer(prop_Cold ~ Militant*Affiliation_Contrast*Condition_Contrast + (1|Subject_ID), data=data)
summary(mod_coldstereotype)

mod_coldstereotype = lmer(prop_Cold ~ Militant*Affiliation_Contrast*Date_Index + (1|Subject_ID), data=data)
summary(mod_coldstereotype)



#Complitcated intercept
mod_compstereotype = lmer(prop_Competence ~ Ethnorace*Affiliation_Contrast*Condition_Contrast + (1+Ethnorace*Condition_Contrast|Subject_ID), data=data)
summary(mod_compstereotype)

mod_compstereotype = lmer(prop_Competence ~ Ethnorace*Affiliation_Contrast*Date_Index + (1+Ethnorace*Date_Index|Subject_ID), data=data)
summary(mod_compstereotype)

mod_compstereotype = lmer(prop_Competence ~ Militant*Affiliation_Contrast*Condition_Contrast + (1+Militant*Condition_Contrast|Subject_ID), data=data)
summary(mod_compstereotype)

mod_compstereotype = lmer(prop_Competence ~ Militant*Affiliation_Contrast*Date_Index + (1+Militant*Date_Index|Subject_ID), data=data)
summary(mod_compstereotype)

#Less Complitcated intercept
mod_compstereotype = lmer(prop_Competence ~ Ethnorace*Affiliation_Contrast*Condition_Contrast + (1|Subject_ID), data=data)
summary(mod_compstereotype)

mod_compstereotype = lmer(prop_Competence ~ Ethnorace*Affiliation_Contrast*Date_Index + (1|Subject_ID), data=data)
summary(mod_compstereotype)

mod_compstereotype = lmer(prop_Competence ~ Militant*Affiliation_Contrast*Condition_Contrast + (1|Subject_ID), data=data)
summary(mod_compstereotype)

mod_compstereotype = lmer(prop_Competence ~ Militant*Affiliation_Contrast*Date_Index + (1|Subject_ID), data=data)
summary(mod_compstereotype)


#Complitcated intercept
mod_incompstereotype = lmer(prop_Incompetence ~ Ethnorace*Affiliation_Contrast*Condition_Contrast + (1+Ethnorace*Condition_Contrast|Subject_ID), data=data)
summary(mod_incompstereotype)

mod_incompstereotype = lmer(prop_Incompetence ~ Ethnorace*Affiliation_Contrast*Date_Index + (1+Ethnorace*Date_Index|Subject_ID), data=data)
summary(mod_incompstereotype)

mod_incompstereotype = lmer(prop_Incompetence ~ Militant*Affiliation_Contrast*Condition_Contrast + (1+Militant*Condition_Contrast|Subject_ID), data=data)
summary(mod_incompstereotype)

mod_incompstereotype = lmer(prop_Incompetence ~ Militant*Affiliation_Contrast*Date_Index + (1+Militant*Date_Index|Subject_ID), data=data)
summary(mod_incompstereotype)

#Less Complitcated intercept
mod_incompstereotype = lmer(prop_Incompetence ~ Ethnorace*Affiliation_Contrast*Condition_Contrast + (1|Subject_ID), data=data)
summary(mod_incompstereotype)

mod_incompstereotype = lmer(prop_Incompetence ~ Ethnorace*Affiliation_Contrast*Date_Index + (1|Subject_ID), data=data)
summary(mod_incompstereotype)

mod_incompstereotype = lmer(prop_Incompetence ~ Militant*Affiliation_Contrast*Condition_Contrast + (1|Subject_ID), data=data)
summary(mod_incompstereotype)

mod_incompstereotype = lmer(prop_Incompetence ~ Militant*Affiliation_Contrast*Date_Index + (1|Subject_ID), data=data)
summary(mod_incompstereotype)



#Complitcated intercept
mod_hatespeech = lmer(Hate_Score ~ Ethnorace*Affiliation_Contrast*Condition_Contrast + (1+Ethnorace*Condition_Contrast|Subject_ID), data=data)
summary(mod_hatespeech)

mod_hatespeech = lmer(Hate_Score ~ Ethnorace*Affiliation_Contrast*Date_Index + (1+Ethnorace*Date_Index|Subject_ID), data=data)
summary(mod_hatespeech)

mod_hatespeech = lmer(Hate_Score ~ Militant*Affiliation_Contrast*Condition_Contrast + (1+Militant*Condition_Contrast|Subject_ID), data=data)
summary(mod_hatespeech)

mod_hatespeech = lmer(Hate_Score ~ Militant*Affiliation_Contrast*Date_Index + (1+Militant*Date_Index|Subject_ID), data=data)
summary(mod_hatespeech)
#Less Complitcated intercept
mod_hatespeech = lmer(Hate_Score ~ Ethnorace*Affiliation_Contrast*Condition_Contrast + (1|Subject_ID), data=data)
summary(mod_hatespeech)

mod_hatespeech = lmer(Hate_Score ~ Ethnorace*Affiliation_Contrast*Date_Index + (1|Subject_ID), data=data)
summary(mod_hatespeech)

mod_hatespeech = lmer(Hate_Score ~ Militant*Affiliation_Contrast*Condition_Contrast + (1|Subject_ID), data=data)
summary(mod_hatespeech)

mod_hatespeech = lmer(Hate_Score ~ Militant*Affiliation_Contrast*Date_Index + (1|Subject_ID), data=data)
summary(mod_hatespeech)


# # buildmer(Hate_Score ~ Ethnorace*Affiliation_Contrast*Condition_Contrast + (1+ Ethnorace*Affiliation_Contrast*Condition_Contrast|Subject_ID), data=data)

