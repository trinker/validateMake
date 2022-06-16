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

## Load Github Packages
# library(termco)    ## remotes::install_github('trinker/termco')


## Load project functions
source('scripts/project_functions.R')


## Set Options
options(scipen=999)



##==============================================================================
## Load Data
##==============================================================================
dat <- readRDS("data/processed/01_CLEANED_DATA.rds") %>%
    as_tibble()






##==============================================================================
## Analyze Data
##==============================================================================























