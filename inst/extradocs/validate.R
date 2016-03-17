#version: 1.01
setwd(file.path(Sys.getenv("USERPROFILE"), "Desktop/TestCore"))
html_message <- "<!doctype html>\n<html>\n<head>\n<title>HTML min</title>\n</head>\n<body>\n%s  Contact Steve -n- Tyler. <br><br><br><br><br><br><img src=\"http://cbsmix1041.files.wordpress.com/2012/07/steven-tyler.jpg\" width=\"540\" height=\"360\"></body>\n</html>"

## Install clean valiData
options(repos="http://cran.rstudio.com/")
if (!require("devtools")) install.packages("devtools")
devtools::install_github("steventsimpson/valiData")

check_gf <- require('googleformr')
if (!check_gf) install.packages('googleformr'); check_gf <- require('googleformr')

## Check if valiData is installed
valiData_available <- require('valiData')

if (!valiData_available) {
	cat(
         sprintf(html_message , "`valiData` not installed."),
	     file = file.path(Sys.getenv("USERPROFILE"),'Desktop/ERROR.html')
	)
	browseURL(file.path(Sys.getenv("USERPROFILE"),'Desktop/ERROR.html'))
	stop("Error occurred")
}


## Check to make sure only one folder is in TestCore
path <- list.dirs(recursive = FALSE)

if (length(path) > 1) {
	cat(
         sprintf(html_message , "More than one directory located in 'TestCore'.<br>Remove additional file.<br><br>If that doesn't work...<br>"),
	     file = file.path(Sys.getenv("USERPROFILE"),'Desktop/ERROR.html')
	)
	browseURL(file.path(Sys.getenv("USERPROFILE"),'Desktop/ERROR.html'))
	stop("Error occurred")
}

## Check to make sure a folder is in TestCore
if (length(path) == 0) {
	cat(
         sprintf(html_message , "It appears there is no test directory located in 'TestCore'.<br>Put a file in TestCore.<br><br>If that doesn't work...<br>"),
	     file = file.path(Sys.getenv("USERPROFILE"),'Desktop/ERROR.html')
	)
	browseURL(file.path(Sys.getenv("USERPROFILE"),'Desktop/ERROR.html'))
	stop("Error occurred")
}

## Check if the map is available and read in
map_loc <- "L:/swiper/DataScience/data_quality/core_data_mapping/core_data_map.rds"
if (!file.exists(map_loc)) {
	cat(
         sprintf(html_message , "The Data Map appears to be missing."),
	     file = file.path(Sys.getenv("USERPROFILE"),'Desktop/ERROR.html')
	)
	browseURL(file.path(Sys.getenv("USERPROFILE"),'Desktop/ERROR.html'))
	stop("Error occurred")
}


core_data_map <- readRDS(map_loc)


## Check if the column map is available and read in
col_map_loc <- "L:/swiper/DataScience/data_quality/core_data_mapping/column_mapping.rds"
if (!file.exists(col_map_loc)) {
	cat(
         sprintf(html_message , "The Column Tests Map appears to be missing."),
	     file = file.path(Sys.getenv("USERPROFILE"),'Desktop/ERROR.html')
	)
	browseURL(file.path(Sys.getenv("USERPROFILE"),'Desktop/ERROR.html'))
	stop("Error occurred")
}


col_map <- readRDS(col_map_loc)



## Run valiData and produce reports
did_it_work <- try(valiData::valiData(path, core_data_map, col_map))

## If valiData ran then try to move the files over to Desktop
## Otherwise give error in browser
if (inherits(did_it_work, "try-error")) {
	cat(
        sprintf(html_message , "Some sort of error occurred in `valiData` function."),
	    file = file.path(Sys.getenv("USERPROFILE"),'Desktop/ERROR.html')
	)
	browseURL(file.path(Sys.getenv("USERPROFILE"),'Desktop/ERROR.html'))
	stop("Error occurred")
} else {

	## make VALIDATED_DATA folder on Desktop and move over folder from TestCore
	dir.create(file.path(Sys.getenv("USERPROFILE"), "Desktop/VALIDATED_DATA"))
    file.copy(path, file.path(Sys.getenv("USERPROFILE"), "Desktop/VALIDATED_DATA"), recursive = TRUE)

    ## If move was successful delete folder from TEstCore
    ## Otherwise give error in browser
    if (file.exists(file.path(Sys.getenv("USERPROFILE"), "Desktop/VALIDATED_DATA", basename(path)))) {
        unlink(path, recursive = TRUE, force = FALSE)
    } else {
    	cat(
            sprintf(html_message , "Folder not moved to Desktop.<br>Please manually move folder out of TestCore.<br><br>If this problem persists..<br>"),
    	    file = file.path(Sys.getenv("USERPROFILE"),'Desktop/ERROR.html')
    	)
    	browseURL(file.path(Sys.getenv("USERPROFILE"),'Desktop/ERROR.html'))
	    stop("Error occurred")
    }
}

## send user name and time stamp for user research
if (check_gf){

    form <- "https://docs.google.com/forms/d/1t4g3F2f1bXUO5Xr00iRR6Kah07WAJK3WSJvm5ja7kOE/viewform"
    valiData_user_research <- googleformr::gformr(form)
    valiData_user_research(Sys.info()[['user']])

}
