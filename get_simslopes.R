###################################### Example ######################################
# simslopes = get_simslopes(model = mod1, confints = "Yes",
#                           variables = c("Benevolence_GenerousvsMalevolent", "Competence"),
#                           levels = list(c(-0.5, 0, 0.5), c(-0.5, 0.5)),
#                           labels = list(c("Malevolent", "Neutral", "Generous"), c("LowCompetence", "HighCompetence")),
#                           categorical = c(TRUE, TRUE))

# model: your model
# confints: do you want to get the confidence intervals?
# variables: what are the variables in interaction?
# levels: what are the levels of each variable at which you want to test the simple slope? For categorical variables, enter all levels. For continuous variables, pick your favorite points. Input must be ordered in the order of the "variables" input.
# labels: what are the labels for each level of each variable? Input must be ordered in the order of the "variables" input.
# categorical: are the variables in interaction categorical? Input must be ordered in the order of the "variables" input.

####################################### Code #######################################
library(tidyverse)
library(jtools)
library(lme4)
library(lmerTest)
library(gtools)
library(dplyr)


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


get_simslopes = function(model, confints = "No", variables = NULL,
                         levels = NULL, labels = NULL, categorical = NULL) {

  `%notin%` = Negate(`%in%`)
  get_sig = function(summary) {
    subset(summary$coefficients, summary$coefficients[,"Pr(>|t|)"] < 0.05 & rownames(summary$coefficients) != "(Intercept)")
  }

  suppressWarnings({
  # figure out how many variables are in the interaction
  # check that length of variables is the same as length of levels, labels, and categoricals
  if (!is.null(levels) & length(variables) != length(levels)) {
    print("Length of levels listed must be the same as the length of variables supplied")
  } else if (!is.null(categorical) & length(variables) != length(categorical)) {
    print("Length of categoricals supplied must be the same as the length of variables supplied")
  } else if (!is.null(labels) & length(variables) != length(labels)) {
    print("Length of labels listed must be the same as the length of variables supplied")
  }

  if (is.null(labels)) {
    labels = list()
    for (var in 1:length(variables)) {
      if (categorical[var] == TRUE) {
        labels = levels[[var]]
      } else {
        if (exists("labels")) {
          labels = append(labels, c("Minus1SD", "Mean", "Plus1SD"))
        } else {
          labels = list(c("Minus1SD", "Mean", "Plus1SD"))
        }
      }
    }
  }

  # get df
  df = get_data(model = model)

  # get formula
  formula = as.character(get_formula(model = model))

  # this will be our output significant slopes table
  if (tolower(confints) == "yes") {
    significant_simslopes = matrix(NA, nrow = 0, ncol = 9)
  } else {
    significant_simslopes = matrix(NA, nrow = 0, ncol = 7)
  }

  ## START
  n_variables = length(variables)

  # get numbver of categorical cells
  # create dummy codes and re-centered variables
  n_categorical = 0
  for (i in 1:n_variables) {
    variable = variables[i]
    variable.levels = levels[[i]]
    variable.labels = labels[[i]]
    variable.categorical = categorical[i]
    variable.length = length(variable.levels)
    # if variable is categorical then dummy-code
    if (variable.categorical == TRUE) {
      for (j in 1:variable.length) {
        name = paste0(variable, "_", variable.labels[j])
        other.variables = variable.levels[-j]
        df[name] = ifelse(df[variable] == variable.levels[j], 0, 1)
        n_categorical = n_categorical + 1
      }
      # if variable is continuous then re-center
    } else {
      for (j in 1:variable.length) {
        name = paste0(variable, "_", variable.labels[j])
        df[name] = df[variable] - variable.levels[j]
      }
    }
  }
  rm(name, other.variables, variable, variable.categorical, variable.labels, variable.length, variable.levels, i, j)
  print(paste0("Total number of categorical cells: ", n_categorical))

  # Create all possible variable combos
  var_combos = combn(length(variables), length(variables) - 1)
  # Go through each column of combos
  for (combo_col in 1:ncol(var_combos)) {
    # Get our groups of interest
    dummy_vars = var_combos[,combo_col]
    print(paste0("Groups of interest: ", variables[dummy_vars]))
    # Get the variable we are testing within our groups of interest
    var = which(variables %notin% variables[dummy_vars])
    print(paste0("Testing: ", variables[var]))

    # If we have more than a 2 x 2 we need to sub-select groups instead of dummy coding them
    if (n_categorical > 4) {
      print("Complex model, will perform subselection instead of dummy-coding.")
      for (dummy_var in dummy_vars) {
        dummy_var_levels = levels[[dummy_var]]
        # Create a matrix of all possible combos for our groups of interest
        if (exists("dummy_var_combos")) {
          temp = matrix(dummy_var_levels, nrow = length(dummy_var_levels), ncol = 1, byrow = FALSE)
          temp = as.data.frame(temp)
          colnames(temp) = variables[dummy_var]
          temp$index = 1
          dummy_var_combos$index = 1
          dummy_var_combos = merge(dummy_var_combos, temp, by="index", all = TRUE)
          dummy_var_combos$index = NULL
          temp = NULL
        } else {
          temp = matrix(dummy_var_levels, nrow = length(dummy_var_levels), ncol = 1, byrow = FALSE)
          dummy_var_combos = as.data.frame(temp)
          colnames(dummy_var_combos) = variables[dummy_var]
          temp = NULL
        }
      }

      # Go through each row of combos
      for (i in 1:nrow(dummy_var_combos)) {
        form = formula[3]
        sub_df = df

        # Get the name of the variable from the colname
        for (j in colnames(dummy_var_combos)) {
          # Get the index for that variable in our inputs
          ind = which(variables == j)
          # Create the name of the group
          name = paste0(variables[ind], "_", labels[[ind]][which(levels[[ind]] == dummy_var_combos[i,j])])
          if (!exists("ref_name")) {
            ref_name = name
          } else {
            ref_name = paste0(ref_name, " ", name)
          }
          # If the variable is categorical
          if (categorical[ind] == TRUE) {
            # Subset the df
            sub_df = sub_df[sub_df[name] == 0, ]

            # Create/Edit the formula
            # If we have more than one orthogonalized contrasts for the dummy var, remove the orthogonalized contrast
            # Number of contrasts is always number of levels - 1
            # Therefore, the only variables that would have multiple contrasts are categorical variables with more than 2 levels
            if (length(levels[[ind]]) > 2) {
              form = gsub(paste0("\\(.*?\\+\\s*",variables[ind], "\\)|\\(", variables[ind], "\\s*\\+.*?\\)"), name, form)
              print(form)
            } else {
              form = str_replace_all(form, variables[ind], name)
              print(form)
            }
          } else {
            form = str_replace_all(form, variables[ind], name)
            print(form)
          }
          # Just in case we missed any of the multi-contrast substrings
          while (grepl(paste0("\\(\\s*\\+\\s*",variables[ind], "\\)|\\(", variables[ind], "\\s*\\+\\s*\\)"), form)) {
            form = gsub("\\(\\s\\+\\s.*?\\)|\\(.*?\\s\\+\\s\\)", "", form)
          }
        }

        # Correct any possible issues in the formula due to variable deletions
        # Remove any instances of ( + or + ). These may happen for categorical variables
        # with more than two levels
        while (grepl("\\(\\s\\+\\s|\\s\\+\\s\\)", form)) {
          form = gsub("\\(\\s\\+\\s.*?\\)|\\(.*?\\s\\+\\s\\)", "", form)
        }
        # Remove any instances of * *
        while (grepl("\\*\\s*\\*", form)) {
          form = gsub("\\*\\s*\\*", "*", form)
        }
        # Remove any instances of the formula starting with a * or +
        while (grepl("^\\s*\\*|^\\s*\\+", form)) {
          form = gsub("^\\s*\\*|^\\s*\\+", "", form)
        }
        # Correct any instances of the formula having a * and a + consecutively to +
        while (grepl("\\*\\s*\\+|\\+\\s*\\*", form)) {
          form = gsub("\\*\\s*\\+|\\+\\s*\\*", "+", form)
        }
        print(form)

        # If the contrast being tested is categorical and has more than two levels, we need to subset
        # And compare each possible combo
        if (categorical[var] == TRUE & length(levels[[var]]) > 2) {
          print("Testing categorical variable with more than 2 levels, will subset the data instead of using the full df.")
          # Create a matrix of all possible pairwise combos
          pairwise_combos = combn(length(levels[[var]]), length(levels[[var]]) - 1)
          # Go through each column of pairwise combos
          for (pair in 1:ncol(pairwise_combos)) {
            group1 = pairwise_combos[1,pair]
            group2 = pairwise_combos[2,pair]
            print(paste0("Testing: ", labels[[var]][group1], " and ", labels[[var]][group2], " for ", ref_name))

            # Subset the df to only contain the two groups we are testing as a contrast
            pair_df = sub_df[sub_df[variables[var]] == levels[[var]][group1] | sub_df[variables[var]] == levels[[var]][group2], ]
            # Make sure the two groups are a proper contrast
            pair_df$pair_contrast = ifelse(pair_df[variables[var]] == levels[[var]][group1], -0.5, 0.5)

            # Any categorical variable with more than two levels will have multiple orthogonalized contrasts
            # Remove the contrast from the formula and substitute it with pair_contrast
            if (grepl(paste0("\\(", variables[var], "\\s+\\+\\s+.*?\\)"), form)) {
              form_pair = gsub(paste0("\\(", variables[var], "\\s+\\+\\s+.*?\\)"), "", form)
            }
            # Remove any instances of the formula starting with a * or a +
            while (grepl("^\\s*\\*|^\\s*\\+", form_pair)) {
              form_pair = gsub("^\\s*\\*|^\\s*\\+", "", form_pair)
            }
            # Check to see if the first term is an interaction
            first_term = gsub("(^\\s*)([A-Za-z0-9_\\(\\)\\+]+?)(\\s*\\+\\s*)(\\([0-9]*\\s*\\|.*\\))$", "\\2", form_pair)
            if (grepl("\\*", first_term)) {
              form_pair = gsub("^", "pair_contrast * ", form_pair)
            } else if (grepl("\\+", first_term)) {
              form_pair = gsub("^", "pair_contrast + ", form_pair)
            } else {
              form_pair = gsub("^", "pair_contrast + ", form_pair)
            }
            # Remove any instances of * *
            while (grepl("\\*\\s*\\*", form_pair)) {
              form_pair = gsub("\\*\\s*\\*", "*", form_pair)
            }
            # Remove any instances of the formula starting with a * or +
            while (grepl("^\\s*\\*|^\\s*\\+", form_pair)) {
              form_pair = gsub("^\\s*\\*|^\\s*\\+", "", form_pair)
            }
            # Correct any instances of the formula having a * and a + consecutively to +
            while (grepl("\\*\\s*\\+|\\+\\s*\\*", form_pair)) {
              form_pair = gsub("\\*\\s*\\+|\\+\\s*\\*", "+", form_pair)
            }

            form_pair = paste0(formula[2], formula[1], form_pair)
            print(form_pair)

            mod = lmer(as.formula(form_pair), data=pair_df)

            summary_mod = summary(mod)

            # Run the linear model
            if (grepl('lmer', class(mod))) {
              print("Model class recognized.")
              warnings = summary_mod$optinfo$conv$lme4$messages
              if (!is.null(warnings)) {
                while (grepl('failed to converge', warnings)) {
                  buildmer = buildmer(as.formula(form), data=pair_df)
                  summary_buildmer = summary(buildmer)
                  suggested_formula = as.character(summary_buildmer$call)[2]
                  cat(paste0("Model failed to converge. \nBuildmer suggested formula:\n", suggested_formula))
                  form_boolean = readline(prompt="Accept this formula? Yes/No  ")
                  form_boolean = tolower(as.character(form_boolean))
                  if (form_boolean == "no") {
                    form = readline(prompt="Please enter new formula within quotes. E.g., 'y ~ x*z + (1|s)'  ")
                    print(form)
                    mod = lmer(as.formula(form), data=pair_df)
                    summary_mod = summary(mod)
                    warnings = summary_mod$optinfo$conv$lme4$messages
                    if (is.null(warnings)) {
                      warnings = "All good"
                    }
                  } else {
                    mod = lmer(summary_buildmer$call, data=pair_df)
                    summary_mod = summary_buildmer
                    warnings = summary_mod$optinfo$conv$lme4$messages
                    if (is.null(warnings)) {
                      warnings = "All good"
                    }
                  }
                }
              } else {
                print("Model converged.")
              }
            } else if (grepl('lm', class(mod))) {
              print("Model class recognized.")
            } else {
              print("Model class unrecognized (neither lmer nor lm).")
            }

            # Subset the results to only contain the contrast we are looking for
            sigs = subset(summary_mod$coefficients, rownames(summary_mod$coefficients) == 'pair_contrast')

            # If we also want confidence intervals then run confint
            if (tolower(confints) == "yes") {
              conf.int = tryCatch({
                confint(mod, oldNames=FALSE)
              })
              # If the result is null, create null rows to rbind
              if (is.null(conf.int)) {
                conf.int = matrix(c('NA', 'NA'), nrow=1, ncol=2, byrow=TRUE)
              } else {
                print("Confidence intervals computed.")
                # If the result is not null, subset result to only contain the contrast we are looking for
                conf.int = subset(conf.int, rownames(conf.int) == 'pair_contrast')
              }
              # Remove all the rownames
              rownames(conf.int) = NULL

              # Create a name containing the pairwise combo we tested
              contrst_name = paste0(labels[[var]][group1], " vs ", labels[[var]][group2])
              # Bind the name of the exact group combo and pairwise combo to the results from the
              # linear model and confidence intervals
              sigs = cbind("Reference" = ref_name, "Contrast" = contrst_name, sigs, conf.int)
              # Remove the rownames
              rownames(sigs) = NULL
              # Add the rows to our existing matrix
              significant_simslopes = rbind(significant_simslopes, sigs)
            } else {
              # Confints not requested, bind the name of the group and the contrast
              sigs = cbind("Reference" = ref_name, "Contrast" = contrst_name, sigs)
              # Remove the rownames
              rownames(sigs) = NULL
              # Add the rows to our existing matrix
              significant_simslopes = rbind(significant_simslopes, sigs)
            }
            rm(form_pair, pair_df, contrst_name, group1, group2)
          }
        } else {
          print("Testing variable is continuous or contains 2 or fewer levels, will use full data.")
          form_cont = paste0(formula[2], formula[1], form)
          print(form_cont)
          mod = lmer(as.formula(form_cont), data=sub_df)

          summary_mod = summary(mod)

          # Run the linear model
          if (grepl('lmer', class(mod))) {
            print("Model class recognized.")
            warnings = summary_mod$optinfo$conv$lme4$messages
            if (!is.null(warnings)) {
              while (grepl('failed to converge', warnings)) {
                buildmer = buildmer(as.formula(form_cont), data=sub_df)
                summary_buildmer = summary(buildmer)
                suggested_formula = as.character(summary_buildmer$call)[2]
                cat(paste0("Model failed to converge. \nBuildmer suggested formula:\n", suggested_formula))
                form_boolean = readline(prompt="Accept this formula? Yes/No  ")
                form_boolean = tolower(as.character(form_boolean))
                if (form_boolean == "no") {
                  form_cont = readline(prompt="Please enter new formula within quotes. E.g., 'y ~ x*z + (1|s)'  ")
                  print(form_cont)
                  mod = lmer(as.formula(form_cont), data=sub_df)
                  summary_mod = summary(mod)
                  warnings = summary_mod$optinfo$conv$lme4$messages
                  if (is.null(warnings)) {
                    warnings = "All good"
                  }
                } else {
                  mod = lmer(summary_buildmer$call, data=sub_df)
                  summary_mod = summary_buildmer
                  warnings = summary_mod$optinfo$conv$lme4$messages
                  if (is.null(warnings)) {
                    warnings = "All good"
                  }
                }
              }
            } else {
              print("Model converged.")
            }
          } else if (grepl('lm', class(mod))) {
            print("Model class recognized.")
          } else {
            print("Model class unrecognized (neither lmer nor lm).")
          }

          # Subset the results to only contain the contrast we are testing
          sigs = subset(round(summary_mod$coefficients, 3), rownames(summary_mod$coefficients) == variables[var])

          # If confidence intervals are requested, get confints
          if (tolower(confints) == "yes") {
            conf.int = tryCatch({
              confint(mod, oldNames=FALSE)
            })
            # If confint results are null, create a null column
            if (is.null(conf.int)) {
              conf.int = matrix(c('NA', 'NA'), nrow=1, ncol=2, byrow=TRUE)
            } else {
              # If not, subset to contain the contrast we are testing
              conf.int = subset(round(conf.int, 3), rownames(conf.int) == variables[var])
            }
            # Remove the rownames
            rownames(conf.int) = NULL
            # Bind the group of interest and contrast of interest to the results from
            # linear model and confint
            sigs = cbind("Reference" = ref_name, "Contrast" = variables[var], sigs, conf.int)
            # Remove the rownames
            rownames(sigs) = NULL
            # Add to pre-existing matrix of results
            significant_simslopes = rbind(significant_simslopes, sigs)
          } else {
            # Confints not requested, bind group of interest and contrast of interest
            # to results from linear model
            sigs = cbind("Reference" = ref_name, "Contrast" = variables[var], sigs)
            # Remove the rownames
            rownames(sigs) = NULL
            # Add to pre-existing matrix of results
            significant_simslopes = rbind(significant_simslopes, sigs)
          }
          rm(form, form_cont, sub_df, ref_name)
        }
        rm(ref_name, sub_df)
      }
      rm(dummy_var_combos)
    } else {
      print("Simple model, will perform dummy-coding instead of subselection.")
      for (dummy_var in dummy_vars) {
        dummy_var_levels = levels[[dummy_var]]
        # Create all possible combos of our groups of interest
        if (exists("dummy_var_combos")) {
          temp = matrix(dummy_var_levels, nrow = length(dummy_var_levels), ncol = 1, byrow = FALSE)
          temp = as.data.frame(temp)
          colnames(temp) = variables[dummy_var]
          temp$index = 1
          dummy_var_combos$index = 1
          dummy_var_combos = merge(dummy_var_combos, temp, by="index", all = TRUE)
          dummy_var_combos$index = NULL
          temp = NULL
        } else {
          temp = matrix(dummy_var_levels, nrow = length(dummy_var_levels), ncol = 1, byrow = FALSE)
          dummy_var_combos = as.data.frame(temp)
          colnames(dummy_var_combos) = variables[dummy_var]
          temp = NULL
        }
      }

      # Go through each row of combos
      for (i in 1:nrow(dummy_var_combos)) {
        form = formula[3]
        sub_df = df

        # Get the name of the variable from the colname
        for (j in colnames(dummy_var_combos)) {
          # Get the index for that variable in our inputs
          ind = which(variables == j)
          # Create the name of the group
          name = paste0(variables[ind], "_", labels[[ind]][which(levels[[ind]] == dummy_var_combos[i,j])])
          if (!exists("ref_name")) {
            ref_name = name
          } else {
            ref_name = paste0(ref_name, " ", name)
          }
          # If the variable is categorical
          if (categorical[ind] == TRUE) {
            # Subset the df
            sub_df = sub_df[sub_df[name] == 0, ]

            # Create/Edit the formula
            # If we have more than one orthogonalized contrasts for the dummy var, remove the orthogonalized contrast
            # Number of contrasts is always number of levels - 1
            # Therefore, the only variables that would have multiple contrasts are categorical variables with more than 2 levels
            if (length(levels[[ind]]) > 2) {
              form = gsub(paste0("\\(.*?\\+\\s*",variables[ind], "\\)|\\(", variables[ind], "\\s*\\+.*?\\)"), name, form)
              print(form)
            } else {
              form = str_replace_all(form, variables[ind], name)
              print(form)
            }
          } else {
            form = str_replace_all(form, variables[ind], name)
            print(form)
          }
          # Just in case we missed any of the multi-contrast substrings
          while (grepl(paste0("\\(\\s*\\+\\s*",variables[ind], "\\)|\\(", variables[ind], "\\s*\\+\\s*\\)"), form)) {
            form = gsub("\\(\\s\\+\\s.*?\\)|\\(.*?\\s\\+\\s\\)", "", form)
          }
        }

        # Correct any possible issues in the formula due to variable deletions
        # Remove any instances of ( + or + ). These may happen for categorical variables
        # with more than two levels
        while (grepl("\\(\\s\\+\\s|\\s\\+\\s\\)", form)) {
          form = gsub("\\(\\s\\+\\s.*?\\)|\\(.*?\\s\\+\\s\\)", "", form)
        }
        # Remove any instances of * *
        while (grepl("\\*\\s*\\*", form)) {
          form = gsub("\\*\\s*\\*", "*", form)
        }
        # Remove any instances of the formula starting with a * or +
        while (grepl("^\\s*\\*|^\\s*\\+", form)) {
          form = gsub("^\\s*\\*|^\\s*\\+", "", form)
        }
        # Correct any instances of the formula having a * and a + consecutively to +
        while (grepl("\\*\\s*\\+|\\+\\s*\\*", form)) {
          form = gsub("\\*\\s*\\+|\\+\\s*\\*", "+", form)
        }

        # If our variable is categorical and has more than 3 levels, subset the df to compare pairwise
        if (categorical[var] == TRUE & length(levels[[var]]) > 2) {
          print("Testing categorical variable with more than 2 levels, will subset the data instead of using the full df.")
          # Create all pairwise combos
          pairwise_combos = combn(length(levels[[var]]), length(levels[[var]]) - 1)
          # Go through each column of pairwise combos
          for (pair in 1:ncol(pairwise_combos)) {
            group1 = pairwise_combos[1,pair]
            group2 = pairwise_combos[2,pair]
            print(paste0("Testing: ", labels[[var]][group1], " and ", labels[[var]][group2]))

            pair_df = df[df[variables[var]] == levels[[var]][group1] | df[variables[var]] == levels[[var]][group2], ]
            pair_df$pair_contrast = ifelse(pair_df[variables[var]] == levels[[var]][group1], -0.5, 0.5)

            # Any categorical variable with more than two levels will have multiple orthogonalized contrasts
            # Remove the contrast from the formula and substitute it with pair_contrast
            if (grepl(paste0("\\(", variables[var], "\\s+\\+\\s+.*?\\)"), form)) {
              form_pair = gsub(paste0("\\(", variables[var], "\\s+\\+\\s+.*?\\)"), "", form)
            }
            # Remove any instances of the formula starting with a * or a +
            while (grepl("^\\s*\\*|^\\s*\\+", form_pair)) {
              form_pair = gsub("^\\s*\\*|^\\s*\\+", "", form_pair)
            }
            # Check to see if the first term is an interaction
            first_term = gsub("(^\\s*)([A-Za-z0-9_\\(\\)\\+]+?)(\\s*\\+\\s*)(\\([0-9]*\\s*\\|.*\\))$", "\\2", form_pair)
            if (grepl("\\*", first_term)) {
              form_pair = gsub("^", "pair_contrast * ", form_pair)
            } else if (grepl("\\+", first_term)) {
              form_pair = gsub("^", "pair_contrast + ", form_pair)
            } else {
              form_pair = gsub("^", "pair_contrast + ", form_pair)
            }
            # Remove any instances of * *
            while (grepl("\\*\\s*\\*", form_pair)) {
              form_pair = gsub("\\*\\s*\\*", "*", form_pair)
            }
            # Remove any instances of the formula starting with a * or +
            while (grepl("^\\s*\\*|^\\s*\\+", form_pair)) {
              form_pair = gsub("^\\s*\\*|^\\s*\\+", "", form_pair)
            }
            # Correct any instances of the formula having a * and a + consecutively to +
            while (grepl("\\*\\s*\\+|\\+\\s*\\*", form_pair)) {
              form_pair = gsub("\\*\\s*\\+|\\+\\s*\\*", "+", form_pair)
            }

            form_pair = paste0(formula[2], formula[1], form_pair)
            print(form_pair)

            # Run the linear model
            mod = lmer(as.formula(form_pair), data=pair_df)
            # Save the summary
            summary_mod = summary(mod)
            # Check to make sure everything happened as expected
            if (grepl('lmer', class(mod))) {
              print("Model class recognized.")
              warnings = summary_mod$optinfo$conv$lme4$messages
              if (!is.null(warnings)) {
                while (grepl('failed to converge', warnings)) {
                  buildmer = buildmer(as.formula(form_pair), data=pair_df)
                  summary_buildmer = summary(buildmer)
                  suggested_formula = as.character(summary_buildmer$call)[2]
                  cat(paste0("Model failed to converge. \nBuildmer suggested formula:\n", suggested_formula))
                  form_boolean = readline(prompt="Accept this formula? Yes/No  ")
                  form_boolean = tolower(as.character(form_boolean))
                  if (form_boolean == "no") {
                    form_pair = readline(prompt="Please enter new formula within quotes. E.g., 'y ~ x*z + (1|s)'  ")
                    print(form_pair)
                    mod = lmer(as.formula(form_pair), data=pair_df)
                    summary_mod = summary(mod)
                    warnings = summary_mod$optinfo$conv$lme4$messages
                    if (is.null(warnings)) {
                      warnings = "All good"
                    }
                  } else {
                    mod = lmer(summary_buildmer$call, data=pair_df)
                    summary_mod = summary_buildmer
                    warnings = summary_mod$optinfo$conv$lme4$messages
                    if (is.null(warnings)) {
                      warnings = "All good"
                    }
                  }
                }
              } else {
                print("Model converged.")
              }
            } else if (grepl('lm', class(mod))) {
              print("Model class recognized.")
            } else {
              print("Model class unrecognized (neither lmer nor lm).")
            }
            # Select rows for our pair contrast
            sigs = subset(summary_mod$coefficients, rownames(summary_mod$coefficients) == 'pair_contrast')
            # If confints were requested, get them
            if (tolower(confints) == "yes") {
              conf.int = tryCatch({
                confint(mod, oldNames=FALSE)
              })
              # If the result was null, create a null row to bind
              if (is.null(conf.int)) {
                conf.int = matrix(c('NA', 'NA'), nrow=1, ncol=2, byrow=TRUE)
              } else {
                # Select rows for our pair contrast
                conf.int = subset(conf.int, rownames(conf.int) == 'pair_contrast')
              }
              # Remove rownames
              rownames(conf.int) = NULL
              # Create a contrast name for the pairwise combo we tested
              contrst_name = paste0(labels[[var]][group1], " vs ", labels[[var]][group2])
              # Bind the reference group name and the pairwise contrast name to the results from the
              # linear model and confint
              sigs = cbind("Reference" = ref_name, "Contrast" = contrst_name, sigs, conf.int)
              # Remove rownames
              rownames(sigs) = NULL
              # Bind to our pre-existing results matrix
              significant_simslopes = rbind(significant_simslopes, sigs)
            } else {
              # Bind the reference group name and the pairwise contrast name to the results from the
              # linear model
              sigs = cbind("Reference" = ref_name, "Contrast" = contrst_name, sigs)
              # Remove rownames
              rownames(sigs) = NULL
              # Bind to our pre-existing results matrix
              significant_simslopes = rbind(significant_simslopes, sigs)
            }
            rm(form, form_pair, pair_df, sub_df, contrst_name, ref_name, group1, group2)
          }
          rm(pairwise_combos)
        } else {
          print("Testing variable continuous or contains 2 or fewer levels, will use full data.")

          form_cont = paste0(formula[2], formula[1], form)
          print(form_cont)
          mod = lmer(as.formula(form_cont), data=sub_df)

          summary_mod = summary(mod)

          if (grepl('lmer', class(mod))) {
            print("Model class recognized.")
            warnings = summary_mod$optinfo$conv$lme4$messages
            if (!is.null(warnings)) {
              while (grepl('failed to converge', warnings)) {
                buildmer = buildmer(as.formula(form_cont), data=sub_df)
                summary_buildmer = summary(buildmer)
                suggested_formula = as.character(summary_buildmer$call)[2]
                cat(paste0("Model failed to converge. \nBuildmer suggested formula:\n", suggested_formula))
                form_boolean = readline(prompt="Accept this formula? Yes/No  ")
                form_boolean = tolower(as.character(form_boolean))
                if (form_boolean == "no") {
                  form_cont = readline(prompt="Please enter new formula within quotes. E.g., 'y ~ x*z + (1|s)'  ")
                  print(form_cont)
                  mod = lmer(as.formula(form_cont), data=sub_df)
                  summary_mod = summary(mod)
                  warnings = summary_mod$optinfo$conv$lme4$messages
                  if (is.null(warnings)) {
                    warnings = "All good"
                  }
                } else {
                  mod = lmer(summary_buildmer$call, data=sub_df)
                  summary_mod = summary_buildmer
                  warnings = summary_mod$optinfo$conv$lme4$messages
                  if (is.null(warnings)) {
                    warnings = "All good"
                  }
                }
              }
            } else {
              print("Model converged.")
            }
          } else if (grepl('lm', class(mod))) {
            print("Model class recognized.")
          } else {
            print("Model class unrecognized (neither lmer nor lm).")
          }
          # Select results for our contrast of interest
          sigs = subset(round(summary_mod$coefficients, 3), rownames(summary_mod$coefficients) == variables[var])
          # If confints were requested, get confints
          if (tolower(confints) == "yes") {
            conf.int = tryCatch({
              confint(mod, oldNames=FALSE)
            })
            # If results are null, create a null row to bind
            if (is.null(conf.int)) {
              conf.int = matrix(c('NA', 'NA'), nrow=1, ncol=2, byrow=TRUE)
            } else {
              # Select the rows for our contrast of interest
              conf.int = subset(round(conf.int, 3), rownames(conf.int) == variables[var])
            }
            # Remove rownames
            rownames(conf.int) = NULL
            # Bind the group's name and contrast with results from the
            # linear model and confint
            sigs = cbind("Reference" = ref_name, "Contrast" = variables[var], sigs, conf.int)
            # Remove rownames
            rownames(sigs) = NULL
            # Bind with our pre-existing results matrix
            significant_simslopes = rbind(significant_simslopes, sigs)
          } else {
            # Bind the group's name and contrast with results from the
            # linear model
            sigs = cbind("Reference" = ref_name, "Contrast" = variables[var], sigs)
            # Remove rownames
            rownames(sigs) = NULL
            # Bind with our pre-existing results matrix
            significant_simslopes = rbind(significant_simslopes, sigs)
          }
          rm(form, form_cont, ref_name, sub_df)
        }
      }
      rm(dummy_var_combos)
    }
  }

  significant_simslopes = as.data.frame(significant_simslopes)

  if (tolower(confints) == "yes") {
    significant_simslopes = significant_simslopes %>%
      mutate(B = round(as.numeric(Estimate), 3),
             SE = round(as.numeric(`Std. Error`), 3),
             df = as.numeric(df),
             `t-value` = round(as.numeric(`t value`), 3),
             `p-value` = round(as.numeric(`Pr(>|t|)`), 3),
             `2.5 %` = round(as.numeric(`2.5 %`), 3),
             `97.5 %` = round(as.numeric(`97.5 %`), 3)) %>%
      mutate(`95% CI` = paste0("[", `2.5 %`, ", ", `97.5 %`, "]")) %>%
      select(Reference, Contrast, B, SE, df, `95% CI`, `t-value`, `p-value`)
  } else {
    significant_simslopes = significant_simslopes %>%
      mutate(B = round(as.numeric(Estimate), 3),
             SE = round(as.numeric(`Std. Error`), 3),
             df = as.numeric(df),
             `t-value` = round(as.numeric(`t value`), 3),
             `p-value` = round(as.numeric(`Pr(>|t|)`), 3)) %>%
      select(Reference, Contrast, B, SE, df, `t-value`, `p-value`)
  }

  return(list("df" = df, "significant_slopes" = significant_simslopes))
  })
}

comp_results = get_simslopes(model = mod_compstereotype, 
              confints = "Yes",
              variables = c("Ethnorace", "Affiliation_Contrast", "Date_Index"),
              levels = list(c(-0.5, 0.5), 
                            c(-0.5, 0.5), 
                            c(-365, -187, 0, 181, 366)),
              # labels = list(c("Israeli/Jewish/IDF", "Arabic/Muslim/Hamas"), 
              #               c("Right-leaning", "Left-leaning"), 
              #               c("Earliest", "Mid", "0", "Mid", "Latest")),
              categorical = c(FALSE, FALSE, FALSE)
)

write.csv(comp_results$significant_slopes,file="Competence_stats_results.csv", row.names=FALSE, na=)

# mod_compstereotype - Ethnorace:Affiliation_Contrast:Date_Index
# prop_Incompetence - Affiliation_Contrast:Date_Index
# Hate_Score - Ethnorace:Affiliation_Contrast