#setwd(file.path(validateMake::get_desktop(), "TestCore"))

## Install clean valiData
options(repos="http://cran.rstudio.com/")
if (!require("curl")) install.packages("curl")

validate_url <- 'https://raw.githubusercontent.com/trinker/validateMake/master/inst/extradocs/validate.R'

tmp <- tempfile()
curl::curl_download(validate_url, tmp)
new_version <- as.numeric(gsub("^[^0-9]+:\\s*", "",  readLines(tmp)[1]))
old_version <- as.numeric(gsub("^[^0-9]+:\\s*", "",  readLines('bin/validate.R')[1]))

if (new_version > old_version){
    cat(readLines(tmp), sep = "\n", file = 'bin/validate.R')
}

#########################################
update_loc <- file.path(getwd(), 'bin/errors')


readme_url <- 'https://raw.githubusercontent.com/trinker/validateMake/master/inst/extradocs/README.txt'

tmp2 <- tempfile()
curl::curl_download(readme_url, tmp2)
new_version2 <- as.numeric(gsub("^[^0-9]+:\\s*", "",  readLines(tmp2)[1]))
old_version2 <- as.numeric(gsub("^[^0-9]+:\\s*", "",  readLines('README.txt')[1]))


url <- 'https://campuslabsinc.sharepoint.com/sites/DataScience/Shared%%20Documents/Data%%20Validating/TestCore_v.%s.zip'
ver <- paste0(paste(rep('0', 3 - nchar(as.character(new_version2))), collapse = ''), as.character(new_version2))

message <- paste0('<a href="', sprintf(url, ver), '">', sprintf(url, ver), '</a>')
html_message <- "<!doctype html>\n<html>\n<head>\n<title>HTML min</title>\n</head>\n<body><p style='font-size: 200%%'>\n%sPlease download the latest version via:</p><br>%s<br><br><br><br><br><br><img src=\"http://i.imgur.com/obiWXJ2.jpg\" width=\"540\" height=\"360\"></body>\n</html>"


if (new_version2 > old_version2) {
	cat(
         sprintf(html_message , "A newer version of the validation program exists.<br>", message),
	     file = file.path(update_loc, "UPGRADE.html")
	)
	browseURL(file.path(update_loc, "UPGRADE.html"))
}
##########################################