library(tidyverse)
library(jtools)
library(lme4)
library(lmerTest)
library(gtools)
library(dplyr)
library(interactions)
library(ggplot2)
library(sjPlot)
library(cowplot)


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
  create_date_numbering("Before_Dates", "2023-10-06", direction = "backward") %>%    filter(Date_Index >= -365) # Ensure min index is at least -365

# Read and process post-data
data_post <- read.csv("After_Stereotypes_Proportion_LIWC_Hate.csv") %>%
  mutate(Condition_Contrast = 0.5) %>%
  create_date_numbering("After_Dates", "2023-10-07", direction = "forward") %>%    filter(Date_Index >= -365) # Ensure min index is at least -365

# head(data_pre[, c("Before_Dates", "Date", "Date_Index")])
# head(data_post[, c("After_Dates", "Date", "Date_Index")])

# names(data_pre)

data = merge(data_pre, data_post, 
             by=names(data_pre)[names(data_pre) %in% names(data_post)],
             all = TRUE) %>% 
  distinct()

# Combine pre and post data
combined_data <- bind_rows(data_pre, data_post)

# # Debugging: print the combined data
# print("Combined Data:")
# print(combined_data)

# Calculate the lowest and highest Date_Index
min_index <- min(combined_data$Date_Index, na.rm = TRUE)
max_index <- max(combined_data$Date_Index, na.rm = TRUE)

# Calculate halfway points
halfway_negative <- min_index / 2
halfway_positive <- max_index / 2

# Find the closest data points to the calculated halfway indexes
closest_negative <- combined_data %>%
  filter(Date_Index <= 0) %>%
  filter(abs(Date_Index - halfway_negative) == min(abs(Date_Index - halfway_negative))) %>%
  distinct(Date_Index) %>%
  pull(Date_Index)

closest_positive <- combined_data %>%
  filter(Date_Index >= 0) %>%
  filter(abs(Date_Index - halfway_positive) == min(abs(Date_Index - halfway_positive))) %>%
  distinct(Date_Index) %>%
  pull(Date_Index)

# Print unique results
print(paste("Lowest time index:", min_index))
print(paste("Highest time index:", max_index))
print(paste("Index halfway between lowest time index and 0:", unique(closest_negative)))
print(paste("Index halfway between 0 and highest time index:", unique(closest_positive)))


data = data %>%
  mutate(ethorace_israelijewish = prop_Israeli + prop_Jewish + prop_IDF,
         ethorace_arabicmuslim = prop_Arabic + prop_Muslim + prop_Hamas) %>%
  mutate(Ethnorace = ifelse(ethorace_israelijewish > ethorace_arabicmuslim, -0.5,
                            ifelse(ethorace_arabicmuslim > ethorace_israelijewish, 0.5, NA)))

mod_compstereotype = lmer(prop_Competence ~ Ethnorace*Affiliation_Contrast*Date_Index + (1|Subject_ID), data=data)
summary(mod_compstereotype)

mod_incompstereotype = lmer(prop_Incompetence ~ Ethnorace*Affiliation_Contrast*Date_Index + (1|Subject_ID), data=data)
summary(mod_incompstereotype)

mod_hatespeech = lmer(Hate_Score ~ Ethnorace*Affiliation_Contrast*Date_Index + (1|Subject_ID), data=data)
summary(mod_hatespeech)

specific_dates <- list(Date_Index = c(-360,-187,0, 181,362))

# -360,-187, 0, 181, 362

hateplot <- interact_plot(mod_hatespeech, 
                          pred = Ethnorace, 
                          modx = Affiliation_Contrast,
                          interval = TRUE, 
                          int.width = 0.95,
                          # main.title = "Significantly Higher Hate Speech Content towards Arabic and/or Muslim Individuals for Right-leaning Influencers",
                          x.label = "Social Groups Mentioned",
                          y.label = "Hate Speech Content",
                          modx.labels = c("Right-leaning", "Left-leaning"),
                          pred.labels = c("Israeli and/or Jewish individuals", "Arabic and/or Muslim individuals"),
                          legend.main = "Influencers' Political Affiliation",
                          colors = c("red", "blue"))
hateplot
# Hate_Score - Ethnorace:Affiliation_Contrast


incompplot <- interact_plot(mod_incompstereotype, 
                          pred = Date_Index, 
                          modx = Ethnorace,
                          interval = TRUE, 
                          int.width = 0.95,
                          # main.title = "Significant Decrease in Usage of Incompetent Stereotype-conveying Words towards Israeli and/or Jewish Individuals",
                          x.label = "Timeline of the Conflict ",
                          y.label = "Incompetence Language Use",
                          modx.labels = c("Israeli and/or Jewish individuals", "Arabic and/or Muslim individuals"),
                          # pred.labels = c("Israeli and/or Jewish individuals", "Arabic and/or Muslim individuals"),
                          legend.main = "Social Groups Mentioned",
                          colors = c("maroon", "lightgreen"))  +
  # Add vertical line at 0
  geom_vline(xintercept = 0, color = "black") +
  # Add label for the vertical line
  annotate("text", x = 0, y = Inf, label = "October 7th", 
           vjust = 1.5, color = "black", fontface = "bold")
incompplot
# mod_incompstereotype - Affiliation_Contrast:Date_Index


ethnocompplot <- interact_plot(mod_compstereotype, 
                            pred = Date_Index, 
                            modx = Ethnorace,
                            interval = TRUE, 
                            int.width = 0.95,
                            main.title = "Interaction of Competence Language Use",
                            x.label = "Timeline of the conflict",
                            y.label = "Competence Language Use",
                            modx.labels = c("Israeli and/or Jewish individuals", "Arabic and/or Muslim individuals"),
                          # pred.labels = c("Mentions of Israeli and/or Jewish individuals", "Mentions of Arabic and/or Muslim individuals"),
                          colors = c("maroon", "lightgreen")) +
  # Add vertical line at 0
  geom_vline(xintercept = 0, color = "black") +
  # Add label for the vertical line
  annotate("text", x = 0, y = Inf, label = "October 7th", 
           vjust = 1.5, color = "black", fontface = "bold")
ethnocompplot

affcompplot <- interact_plot(mod_compstereotype, 
                          pred = Date_Index, 
                          modx = Affiliation_Contrast,
                          interval = TRUE, 
                          int.width = 0.95,
                          main.title = "Interaction of Competence Language Use",
                          x.label = "Timeline of the conflict",
                          y.label = "Competence Language Use",
                          modx.labels = c("Right-leaning", "Left-leaning"),
                          # pred.labels = c("Israeli and/or Jewish individuals", "Arabic and/or Muslim individuals"),
                          colors = c("red", "blue")) +
  # Add vertical line at 0
  geom_vline(xintercept = 0, color = "black") +
  # Add label for the vertical line
  annotate("text", x = 0, y = Inf, label = "October 7th", 
           vjust = 1.5, color = "black", fontface = "bold")
affcompplot
# mod_compstereotype - Ethnorace:Affiliation_Contrast:Date_Index

aff2compplot <- interact_plot(mod_compstereotype, 
                             pred = Affiliation_Contrast, 
                             modx = Ethnorace,
                             interval = TRUE, 
                             int.width = 0.95,
                             # main.title = "Significantly Higher Usage of Incompetent Stereotype-conveying Words Use towards Israeli and/or Jewish Individuals for Left-leaning Influencers",
                             x.label = "Timeline of the conflict",
                             y.label = "Competence Language Use",
                             modx.labels = c("Israeli and/or Jewish individuals", "Arabic and/or Muslim individuals"),
                             pred.labels = c("Right-leaning", "Left-leaning"),
                             legend.main = "Social Groups Mentioned",
                             colors = c("maroon", "lightgreen")) 
aff2compplot
# mod_compstereotype - Ethnorace:Affiliation_Contrast:Date_Index

ggsave("hatespeech_plot.png", hateplot, width = 10, height = 7)  # Adjust width and height as needed
ggsave("incompetence_plot.png", incompplot, width = 10, height = 7)  # Adjust width and height as needed
ggsave("competence_plot.png", aff2compplot, width = 10, height = 7)  # Adjust width and height as needed



# plot_model(mod_hatespeech, type = "int", terms = c(Ethnorace,Affiliation_Contrast, data$Date_Index %in% specific_dates$Date_Index), ci.lvl = 0.95)