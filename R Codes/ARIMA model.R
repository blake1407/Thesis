# Load the necessary libraries
library(tidyverse)
library(forecast)
library(strucchange)
library(tseries)


# Read the data
data <- read.csv("After_Stereotypes_Proportion.csv")

# Convert the 'After_Dates' column to a proper date format
data <- data %>%
  mutate(After_Dates = as.Date(After_Dates, format = "%B %d, %Y %I:%M %p"))

# Subset the data for the variables you want to model
prop_variables <- c("prop_Warm", "prop_Incompetence", "prop_Cold", "prop_Competence",
                    "prop_Jewish", "prop_Muslim", "prop_Arabic", "prop_Israeli", "prop_IDF", "prop_Hamas")

# Create a time series for each variable
ts_data <- data %>%
  select(After_Dates, all_of(prop_variables)) %>%
  pivot_longer(-After_Dates, names_to = "variable", values_to = "value")

# Check if the variables are stationary using Dickey-Fuller test
for (var in prop_variables) {
  ts <- ts_data %>%
    filter(variable == var) %>%
    arrange(After_Dates) %>%
    pull(value)
  
  print(var)
  print(summary(adf.test(ts)))
}

# Identify structural changes (breakpoints) in the time series
for (var in prop_variables) {
  ts <- ts_data %>%
    filter(variable == var) %>%
    arrange(After_Dates) %>%
    pull(value)
  
  print(var)
  print(breakpoints(ts ~ 1))
}

# Fit the ARIMA model for each variable
for (var in prop_variables) {
  ts <- ts_data %>%
    filter(variable == var) %>%
    arrange(After_Dates) %>%
    pull(value)
  
  fit <- auto.arima(ts)
  
  # Print the model summary
  print(var)
  print(summary(fit))
  
  # Visualize the time series and the fitted model
  plot(ts, main = var)
  lines(fitted(fit), col = "red")
}