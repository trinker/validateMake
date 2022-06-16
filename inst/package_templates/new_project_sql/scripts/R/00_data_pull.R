# Dependencies & Setup ----
## Load Campus Labs Packages ----
library(cl)
library(clClean)
library(clDatabases)

## Load Packages ----
library(magrittr)
library(tidyverse)


## Load Github Packages ----
# library(termco)    ## remotes::install_github('trinker/termco')


## Load project functions ----
source('scripts/project_functions.R')


## Set Options ----
options(scipen=999)


# Connect to the Database(s) ----
## Get credentials ----
## secure way to share scripts; credentials are stored & sourced locally
cr <- cl::get_config(inputs = c('User', 'Password', 'Database', 'Auth', 'Server', 'Driver'))


## Make the connection ----
db <- clDatabases::connect(cr$DB_NAME_HERE)



# Query the Database(s) ----
## The query ----
query <- glue::glue("
SELECT * 
    FROM INFORMATION_SCHEMA.TABLES 
    WHERE TABLE_TYPE='BASE TABLE'
")


## Query the Database ----
dat <- db$query(query)



# Saved Data ----
saveRDS(dat, "data/raw/01_INITIAL_PULL_DATA.rds")




