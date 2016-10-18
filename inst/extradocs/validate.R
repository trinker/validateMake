#version: 1.15
html_message <- "<!doctype html>\n<html>\n<head>\n<title>HTML min</title>\n</head>\n<body><p style='font-size: 200%%'>\n%s  Contact Steve -n- Tyler.</p><br><br><br><br><br><br><img src=\"http://cbsmix1041.files.wordpress.com/2012/07/steven-tyler.jpg\" width=\"540\" height=\"360\"></body>\n</html>"

desktop <- validateMake::get_desktop()

setwd(file.path(desktop, "TestCore"))


## Install clean valiData
options(repos="http://cran.rstudio.com/")
if (!require("devtools")) install.packages("devtools")
devtools::install_github("data-steve/valiData")

check_gf <- require('googleformr')
if (!check_gf) install.packages('googleformr'); check_gf <- require('googleformr')

## Check if valiData is installed
valiData_available <- require('valiData')

if (!valiData_available) {
	cat(
         sprintf(html_message , "`valiData` not installed."),
	     file = file.path(desktop, "ERROR.html")
	)
	browseURL(file.path(desktop, "ERROR.html"))
	stop("Error occurred")
}


## Check to make sure only one folder is in TestCore
path <- list.dirs(recursive = FALSE)

path

if (length(path) > 1) {
	cat(
         sprintf(html_message , "More than one directory located in 'TestCore'.<br>Remove additional file.<br><br>If that doesn't work...<br>"),
	     file = file.path(desktop, "ERROR.html")
	)
	browseURL(file.path(desktop, "ERROR.html"))
	stop("Error occurred")
}

## Check to make sure a folder is in TestCore
if (length(path) == 0) {
	cat(
         sprintf(html_message , "It appears there is no test directory located in 'TestCore'.<br>Put a file in TestCore.<br><br>If that doesn't work...<br>"),
	     file = file.path(desktop, "ERROR.html")
	)
	browseURL(file.path(desktop, "ERROR.html"))
	stop("Error occurred")
}

## Check if the map is available and read in
l_drive_go <- function (where_to = "") {
    file.path(ifelse(Sys.info()["sysname"] == "Windows", "L:",
        "/Volumes/shared"), where_to)
}

map_loc <- l_drive_go("swiper/valiData/Core_Data_Dictionary_DS_longforms.xlsx")
if (!file.exists(map_loc)) {
	cat(
         sprintf(html_message , "The Data Map appears to be missing."),
	     file = file.path(desktop, "ERROR.html")
	)
	browseURL(file.path(desktop, "ERROR.html"))
	stop("Error occurred")
}


map <- import_map(map_loc)


## Run valiData and produce reports
did_it_work <- try(valiData::valiData(path, map))

## If valiData ran then try to move the files over to Desktop
## Otherwise give error in browser
if (inherits(did_it_work, "try-error")) {
	cat(
        sprintf(html_message , "Some sort of error occurred in `valiData` function."),
	    file = file.path(desktop, "ERROR.html")
	)
	browseURL(file.path(desktop, "ERROR.html"))

    pers_dir <- file.path(l_drive_go("swiper/valiData/Data_Valiadtion/Error_Data"), Sys.info()[['user']])
    unlink(pers_dir, recursive = TRUE, force = TRUE)
    suppressWarnings(dir.create(pers_dir))

    file.copy(
        path,
        pers_dir,
        overwrite = TRUE,
        recursive = TRUE
    )


	stop("Error occurred")
} else {

    ## actually makes the report
    print(did_it_work, as.report = TRUE, delete = TRUE)

    ## make VALIDATED_DATA folder on Desktop and move over folder from TestCore
    dir.create(file.path(desktop, "VALIDATED_DATA"))
    file.copy(path, file.path(desktop, "VALIDATED_DATA"), recursive = TRUE)

    ## If move was successful delete folder from TEstCore
    ## Otherwise give error in browser
    if (file.exists(file.path(desktop, "VALIDATED_DATA", basename(path)))) {
        unlink(path, recursive = TRUE, force = FALSE)
    } else {
    	cat(
            sprintf(html_message , "Folder not moved to Desktop.<br>Please manually move folder out of TestCore.<br><br>If this problem persists..<br>"),
    	    file = file.path(desktop, "ERROR.html")
    	)
    	browseURL(file.path(desktop, "ERROR.html"))
	    stop("Error occurred")
    }
}

## send user name and time stamp for user research
if (check_gf){
    if(!Sys.info()[['user']] %in% c("trinker", "ssimpson")){
        form <- "https://docs.google.com/forms/d/1t4g3F2f1bXUO5Xr00iRR6Kah07WAJK3WSJvm5ja7kOE/viewform"
        valiData_user_research <- googleformr::gformr(form)
        valiData_user_research(Sys.info()[['user']])
    }

}

## send validated report as .rds
if(!Sys.info()[['user']] %in% c("trinker", "ssimpson")){
    storage_loc <- file.path(
        l_drive_go("swiper/valiData/data_store"),
        paste0(
            paste(basename(path), gsub("\\s+", "_", gsub(":", ".", Sys.time())), Sys.info()[['user']], sep="__"),
            '.rds'
        )
    )

    saveRDS(did_it_work, storage_loc)
}


## Check that personID in child files is found in accounts
##   First ensure 'Accounts/AccountImports/xxx.csv' exists
accts <- file.path(file.path(desktop, "VALIDATED_DATA", basename(path)), 'Accounts/AccountImports')
acc_csvs_valid <- file.exists(accts) && length(dir(accts, pattern = ".csv$|.CSV$") > 0)
dir(accts, pattern = ".csv$|.CSV$")  # left for debugging purposes
file.exists(accts)             # left for debugging purposes
if (acc_csvs_valid) {


    ## check personID against accounts.csv
    did_id_check_work <- try(
        valiData:::compare_column(
		path = file.path(desktop, "VALIDATED_DATA", basename(path)),
		column='PersonIdentifier',
		parent='AccountImports',
		child = c('Enrollment', 'FacultyRemoval', 'Instructor', 'FacultyImport', 'StudentImport'),
		ignore.case = TRUE
        )
    )


    ## If valiData:::compare_column ran then try to move the files over to Desktop
    ## Otherwise give error in browser
    if (inherits(did_id_check_work, "try-error")) {
    	cat(
            sprintf(html_message , "Some sort of error occurred in `valiData:::compare_column` function."),
    	    file = file.path(desktop, "ERROR.html")
    	)
    	browseURL(file.path(desktop, "ERROR.html"))
    	stop("Error occurred")
    } else {

        ## actually makes the report
    	sink(
    		file.path(desktop, "VALIDATED_DATA/", basename(path), "`Reports/PersonIdentifier_Report.txt"),
    		append = FALSE,
    		split = TRUE
    	)

        valiData:::print.compare_column(did_id_check_work)

    	sink()

        ## If move was successful delete folder from TEstCore
        ## Otherwise give error in browser
        if (!file.path(desktop, "VALIDATED_DATA/", basename(path), "`Reports/PersonIdentifier_Report.txt")) {
        	cat(
                sprintf(html_message , "PersonIdentifier_Report not run.<br>Contact...<br>"),
        	    file = file.path(desktop, "ERROR.html")
        	)
        	browseURL(file.path(desktop, "ERROR.html"))
    	    stop("Error occurred")
        }
    }
} else {

    comp <- paste0("Could not find a single valid .csv file in  the following location to match personIDs against:\n", accts)
    cat(comp, file = file.path(desktop, "VALIDATED_DATA/", basename(path), "`Reports/PersonIdentifier_Report.txt"))

}




