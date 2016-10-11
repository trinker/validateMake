setwd(file.path(validateMake::get_desktop(), "TestCore"))

## Install clean valiData
options(repos="http://cran.rstudio.com/")
if (!require("curl")) install.packages("curl")


validate_url <- 'https://raw.githubusercontent.com/trinker/validateMake/master/inst/extradocs/validate.R'

tmp <- tempfile()
curl::curl_download(validate_url, tmp)
new_version <- as.numeric(gsub("^[^0-9]+:\\s*", "",  readLines(tmp)[1]))
old_version <- as.numeric(gsub("^[^0-9]+:\\s*", "",  readLines('validate.R')[1]))

if (new_version > old_version){
    cat(readLines(tmp), sep = "\n", file = 'validate.R')
}


