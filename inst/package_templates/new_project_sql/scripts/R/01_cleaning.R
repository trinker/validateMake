##==============================================================================
## Dependencies & Setup
##==============================================================================
## Load Campus Labs Packages
library(cl)
library(clClean)
library(clDatabases)

## Load Packages
library(magrittr)
library(tidyverse)
library(GGally)
library(skimr)

## Load Github Packages
# library(termco)    ## remotes::install_github('trinker/termco')

## Load project functions
source('scripts/project_functions.R')


## Set Options
options(scipen=999)

# ## Uncomment this chunk as needed via cntrl (cmd on Mac) + shift + C
# ## Credentials (secure way to share scripts; credentials are stored & sourced locally)
# ## Note: Supply the inputs to allow your script to still be run by those who have 
# ##       not created a config file.  See ?cl::get_config for details on setting up
# ##       a config for storing credentials securely.
# ##
# ## Replace `inputs` below:
# cr <- cl::get_config(inputs = c('User', 'Password', 'Database', 'Auth', 'Server', 'Driver'))
# 
# ## Access inputs via:
# cr$User
# 
# ## Make the connection
# db <- clDatabases::connect(cr$DB_NAME_HERE)


##==============================================================================
## Read In Data
##==============================================================================
## Load Data
dat <- readRDS("data/raw/01_INITIAL_PULL_DATA.rds")
    clClean::drop_missing_rows() %>%  # Remove all missing rows
    clClean::drop_missing_cols()      # Drop all totally missing columns

    
##==============================================================================
## Inspect Data
##============================================================================== 
## Describe (understand text values, missing variables, variable relationships)
clClean::inspect_character(dat)               # text values
skimr::skim(dat)                              # distributions and missingness
GGally::ggpairs(dat, get_defined_types(dat))  # relationships (works best on smaller data sets)


##==============================================================================
## Cleaning
##==============================================================================
cleaned_dat <- dat %>%
    dplyr::mutate()



##==============================================================================
## Saved Cleaned Data
##==============================================================================
saveRDS(cleaned_dat, "data/processed/01_CLEANED_DATA.rds")



