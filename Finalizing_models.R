library(tidyverse)
library(lmerTest)
library(lme4)
library(car)
library(buildmer)
library(interactions)
library(glmnet)
library(lubridate)
library(dplyr, warn.conflicts = FALSE)
library(broom)


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
  mutate(ethnorace_israelijewish = prop_Israeli + prop_Jewish,
         ethnorace_arabicmuslim = prop_Arabic + prop_Muslim) %>%
  mutate(Ethnorace = ifelse(ethnorace_israelijewish > ethnorace_arabicmuslim, -0.5,
                            ifelse(ethnorace_arabicmuslim > ethnorace_israelijewish, 0.5, NA)))

#ONly compare data in the after period as IDF was not mentioned
data <- data %>%
  mutate(Militant = ifelse(Condition_Contrast == 0.5 & prop_IDF > prop_Hamas, -0.5,
                           ifelse(Condition_Contrast == 0.5 & prop_Hamas > prop_IDF, 0.5, 
                                  NA)))

data = data %>%
  mutate(Civilian = ifelse(prop_IDF > ethnorace_israelijewish, -0.5,
                           ifelse(prop_Hamas > ethnorace_arabicmuslim, -0.5,
                                  ifelse(ethnorace_israelijewish > prop_IDF, 0.5,
                                         ifelse(ethnorace_arabicmuslim > prop_Hamas, 0.5, NA)))))

#Complitcated intercept
mod_negsentiment = lmer(tone_neg ~ Ethnorace*Affiliation_Contrast*Condition_Contrast + (1+Ethnorace*Condition_Contrast|Subject_ID), data=data)
summary(mod_negsentiment)

mod_negsentiment = lmer(tone_neg ~ Ethnorace*Affiliation_Contrast*Date_Index + (1+Ethnorace*Date_Index|Subject_ID), data=data)
summary(mod_negsentiment)

# mod_negsentiment = lmer(tone_neg ~ Militant*Affiliation_Contrast*Condition_Contrast*Civilian + (1+Militant*Condition_Contrast|Subject_ID), data=data)
# summary(mod_negsentiment)

mod_negsentiment = lmer(tone_neg ~ Militant*Affiliation_Contrast*Date_Index*Civilian + (1+Militant*Date_Index|Subject_ID), data=data)
summary(mod_negsentiment)


#Less Complitcated intercept
mod_negsentiment = lmer(tone_neg ~ Ethnorace*Affiliation_Contrast*Condition_Contrast*Civilian + (1|Subject_ID), data=data)
summary(mod_negsentiment)

mod_negsentiment = lmer(tone_neg ~ Ethnorace*Affiliation_Contrast*Date_Index*Civilian + (1|Subject_ID), data=data)
summary(mod_negsentiment)

# mod_negsentiment = lmer(tone_neg ~ Militant*Affiliation_Contrast*Condition_Contrast*Civilian + (1|Subject_ID), data=data)
# summary(mod_negsentiment)

mod_negsentiment = lmer(tone_neg ~ Militant*Affiliation_Contrast*Date_Index*Civilian + (1|Subject_ID), data=data)
summary(mod_negsentiment)



#Complitcated intercept
mod_possentiment = lmer(tone_pos ~ Ethnorace*Affiliation_Contrast*Condition_Contrast*Civilian + (1+Ethnorace*Condition_Contrast|Subject_ID), data=data)
summary(mod_possentiment)

mod_possentiment = lmer(tone_pos ~ Ethnorace*Affiliation_Contrast*Date_Index*Civilian + (1+Ethnorace*Date_Index|Subject_ID), data=data)
summary(mod_possentiment)

# mod_possentiment = lmer(tone_pos ~ Militant*Affiliation_Contrast*Condition_Contrast*Civilian + (1+Militant*Condition_Contrast|Subject_ID), data=data)
# summary(mod_possentiment)

mod_possentiment = lmer(tone_pos ~ Militant*Affiliation_Contrast*Date_Index + (1+Militant*Date_Index|Subject_ID), data=data)
summary(mod_possentiment)

#Less Complitcated intercept
mod_possentiment = lmer(tone_pos ~ Ethnorace*Affiliation_Contrast*Condition_Contrast + (1|Subject_ID), data=data)
summary(mod_possentiment)

mod_possentiment = lmer(tone_pos ~ Ethnorace*Affiliation_Contrast*Date_Index + (1|Subject_ID), data=data)
summary(mod_possentiment)

# mod_possentiment = lmer(tone_pos ~ Militant*Affiliation_Contrast*Condition_Contrast*Civilian + (1|Subject_ID), data=data)
# summary(mod_possentiment)

mod_possentiment = lmer(tone_pos ~ Militant*Affiliation_Contrast*Date_Index*Civilian + (1|Subject_ID), data=data)
summary(mod_possentiment)



#Complitcated intercept
mod_warmstereotype = lmer(prop_Warm ~ Ethnorace*Affiliation_Contrast*Condition_Contrast + (1+Ethnorace*Condition_Contrast|Subject_ID), data=data)
summary(mod_warmstereotype)

mod_warmstereotype = lmer(prop_Warm ~ Ethnorace*Affiliation_Contrast*Date_Index + (1+Ethnorace*Date_Index|Subject_ID), data=data)
summary(mod_warmstereotype)

# mod_warmstereotype = lmer(prop_Warm ~ Militant*Affiliation_Contrast*Condition_Contrast + (1+Militant*Condition_Contrast|Subject_ID), data=data)
# summary(mod_warmstereotype)

mod_warmstereotype = lmer(prop_Warm ~ Militant*Affiliation_Contrast*Date_Index + (1+Militant*Date_Index|Subject_ID), data=data)
summary(mod_warmstereotype)

#Less Complitcated intercept
mod_warmstereotype = lmer(prop_Warm ~ Ethnorace*Affiliation_Contrast*Condition_Contrast + (1|Subject_ID), data=data)
summary(mod_warmstereotype)

mod_warmstereotype = lmer(prop_Warm ~ Ethnorace*Affiliation_Contrast*Date_Index + (1|Subject_ID), data=data)
summary(mod_warmstereotype)

# mod_warmstereotype = lmer(prop_Warm ~ Militant*Affiliation_Contrast*Condition_Contrast + (1|Subject_ID), data=data)
# summary(mod_warmstereotype)

mod_warmstereotype = lmer(prop_Warm ~ Militant*Affiliation_Contrast*Date_Index + (1|Subject_ID), data=data)
summary(mod_warmstereotype)


#Complitcated intercept
mod_coldstereotype = lmer(prop_Cold ~ Ethnorace*Affiliation_Contrast*Condition_Contrast + (1+Ethnorace*Condition_Contrast|Subject_ID), data=data)
summary(mod_coldstereotype)

mod_coldstereotype = lmer(prop_Cold ~ Ethnorace*Affiliation_Contrast*Date_Index + (1+Ethnorace*Date_Index|Subject_ID), data=data)
summary(mod_coldstereotype)

# mod_coldstereotype = lmer(prop_Cold ~ Militant*Affiliation_Contrast*Condition_Contrast + (1+Militant*Condition_Contrast|Subject_ID), data=data)
# summary(mod_coldstereotype)

mod_coldstereotype = lmer(prop_Cold ~ Militant*Affiliation_Contrast*Date_Index + (1+Militant*Date_Index|Subject_ID), data=data)
summary(mod_coldstereotype)

#Less Complitcated intercept
mod_coldstereotype = lmer(prop_Cold ~ Ethnorace*Affiliation_Contrast*Condition_Contrast + (1|Subject_ID), data=data)
summary(mod_coldstereotype)

mod_coldstereotype = lmer(prop_Cold ~ Ethnorace*Affiliation_Contrast*Date_Index + (1|Subject_ID), data=data)
summary(mod_coldstereotype)

# mod_coldstereotype = lmer(prop_Cold ~ Militant*Affiliation_Contrast*Condition_Contrast + (1|Subject_ID), data=data)
# summary(mod_coldstereotype)

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

# Remove NA values or handle them appropriately
data_cleaned <- data[!is.na(data$Militant), ]

# Categorize Militant variable
data_cleaned$Militant_Cat <- ifelse(data_cleaned$Militant == -0.5, 
                                    "Tweets Mentioning IDF", 
                                    "Tweets Mentioning Hamas")


# Create the interaction plot with the cleaned data
p <- interact_plot(mod_compstereotype, 
                   pred = "Date_Index", 
                   modx = "Affiliation_Contrast", 
                   mod2 = "Militant_Cat",
                   plot.points = TRUE,
                   point.alpha = 0.3,  # Make points less opaque
                   colors = c("red", "blue"),  # Specific colors for Affiliation_Contrast levels
                   legend.main = "Affiliation Contrast",
                   data = data_cleaned) +
  
  # Add vertical line at 0 with date label
  geom_vline(xintercept = 0, linetype = "dashed", color = "gray50") +
  annotate("text", x = 0, y = Inf, label = "Oct 7th, 2023", 
           vjust = 1.5, hjust = 0.5, color = "gray50") +
  
  # Customize point appearance
  geom_point(alpha = 0.3) +
  
  # Improve overall aesthetics
  theme_minimal() +
  labs(title = "",
       x = "Date Index",
       y = "Proportion of Competence-conveying Words",
       color = "Affiliation Contrast")

# Print the plot
print(p)

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

# mod_hatespeech = lmer(Hate_Score ~ Militant*Affiliation_Contrast*Condition_Contrast + (1+Militant*Condition_Contrast|Subject_ID), data=data)
# summary(mod_hatespeech)

mod_hatespeech = lmer(Hate_Score ~ Militant*Affiliation_Contrast*Date_Index + (1+Militant*Date_Index|Subject_ID), data=data)
summary(mod_hatespeech)
#Less Complitcated intercept
mod_hatespeech = lmer(Hate_Score ~ Ethnorace*Affiliation_Contrast*Condition_Contrast + (1|Subject_ID), data=data)
summary(mod_hatespeech)

mod_hatespeech = lmer(Hate_Score ~ Ethnorace*Affiliation_Contrast*Date_Index + (1|Subject_ID), data=data)
summary(mod_hatespeech)

# mod_hatespeech = lmer(Hate_Score ~ Militant*Affiliation_Contrast*Condition_Contrast + (1|Subject_ID), data=data)
# summary(mod_hatespeech)

mod_hatespeech = lmer(Hate_Score ~ Militant*Affiliation_Contrast*Date_Index + (1|Subject_ID), data=data)
summary(mod_hatespeech)


# # buildmer(Hate_Score ~ Ethnorace*Affiliation_Contrast*Condition_Contrast + (1+ Ethnorace*Affiliation_Contrast*Condition_Contrast|Subject_ID), data=data)

