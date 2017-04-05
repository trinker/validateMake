#version: 1.21
html_message <- "<!doctype html>\n<html>\n<head>\n<title>HTML min</title>\n</head>\n<body><p style='font-size: 200%%'>\n%s  Contact Data Science with the following items:<br><ul><li>The files that error (zip them)</li><li>'~/TestCore/bin/validate.Rout file'</li></ul></p><br><br><br><br><br><br><img src=\"http://drinkboxstudios.com/blog/wp-content/uploads/2012/02/simpsons-doh2_480x360.jpg\" width=\"540\" height=\"360\"></body>\n</html>"


#=====================
## directory variables
#=====================
error_loc <- file.path(getwd(), 'bin/errors')
map_loc <- 'bin/Core_Data_Dictionary_DS_longforms.xlsx'




#=====================
# Install dependencies
#=====================
options(repos="http://cran.rstudio.com/")
if (!require("hms")) install.packages("hms")
if (!require("dplyr")) install.packages("dplyr")
if (!require("tibble")) install.packages("tibble")
if (!require("data.table")) install.packages("data.table")
if (!require("devtools")) install.packages("devtools")
devtools::install_github("trinker/valiData")

## Check if valiData is installed
valiData_available <- require('valiData')

if (!valiData_available) {
	cat(
         sprintf(html_message , "`valiData` not installed."),
	     file = file.path(error_loc, "ERROR.html")
	)
	browseURL(file.path(error_loc, "ERROR.html"))
	stop("Error occurred")
}





#===================================================
## Check to make sure only one folder is in TestCore
#===================================================
path <- grep("(VALIDATED_DATA)|(\\./bin)", list.dirs(recursive = FALSE), invert=TRUE, value=TRUE); path

if (length(path) > 1) {
	cat(
         sprintf(html_message , "More than one directory located in 'TestCore'.<br>Remove additional file.<br><br>If that doesn't work...<br>"),
	     file = file.path(error_loc, "ERROR.html")
	)
	browseURL(file.path(error_loc, "ERROR.html"))
	stop("Error occurred")
}

## Check to make sure a folder is in TestCore
if (length(path) == 0) {
	cat(
         sprintf(html_message , "It appears there is no test directory located in 'TestCore'.<br>Put a file in TestCore.<br><br>If that doesn't work...<br>"),
	     file = file.path(error_loc, "ERROR.html")
	)
	browseURL(file.path(error_loc, "ERROR.html"))
	stop("Error occurred")
}




#================
## Import the Map
#================
map <- import_map(map_loc)





#==================================
## Run valiData and produce reports
#==================================
did_it_work1 <- try(valiData::valiData(path, map))

## Check if valiData ran otherwise give error in browser
if (inherits(did_it_work1, "try-error")) {
	cat(
        sprintf(html_message , "Some sort of error occurred in `valiData` function."),
	    file = file.path(error_loc, "ERROR.html")
	)
	browseURL(file.path(error_loc, "ERROR.html"))

	stop("Error occurred")

} else {

    ## actually makes the report
    print(did_it_work1, as.report = TRUE, delete = TRUE)

}




#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Additiional non valiData cross file checking
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

##========================================================
## Check that personID in child files is found in accounts
##========================================================
## First ensure 'Accounts/AccountImports/xxx.csv' exists
accts <- file.path(basename(path), 'Accounts/AccountImports')
acc_csvs_valid <- file.exists(accts) && length(dir(accts, pattern = ".csv$|.CSV$") > 0)
dir(accts, pattern = ".csv$|.CSV$"); file.exists(accts)

if (isTRUE(acc_csvs_valid)) {

    ## check personID against accounts.csv
    did_id_check_work2 <- try(
        valiData:::compare_column(
		path = basename(path),
		parent.column='PersonIdentifier',
		parent='AccountImports',
		child = c('Enrollment', 'FacultyRemoval', 'Instructor', 'FacultyImport', 'StudentImport'),
		ignore.case = TRUE
        )
    )

    ## If valiData:::compare_column ran then add reporting
    ## Otherwise give error in browser
    if (inherits(did_id_check_work2, "try-error")) {

        cat(
            sprintf(html_message , "Some sort of error occurred in `valiData:::compare_column` function (when checking `PersonIdentifier`)."),
    	      file = file.path(error_loc, "ERROR.html")
    	  )
    	  browseURL(file.path(error_loc, "ERROR.html"))
     	  stop("Error occurred")

    } else {

        ## actually makes the report
    	  sink(
    		file.path(basename(path), "`Reports/Cross_File_Comparisons_Report.txt"),
    		append = FALSE,
    		split = TRUE
    	  )
        valiData:::print.compare_column(did_id_check_work2)
    	  sink()

        ## Check if addition was successful
        ## Otherwise give error in browser
        if (!file.exists(file.path(basename(path), "`Reports/Cross_File_Comparisons_Report.txt"))) {

        	cat(
                sprintf(html_message , "Cross_File_Comparisons_Report not run.<br>Contact...<br>"),
        	    file = file.path(error_loc, "ERROR.html")
        	)
        	browseURL(file.path(error_loc, "ERROR.html"))
    	      stop("Error occurred")

        }
    }

} else {

    comp <- paste0("Could not find a single valid .csv file in  the following location to match personIDs against:\n", accts)
    cat(comp, file = file.path(basename(path), "`Reports/Cross_File_Comparisons_Report.txt"))

}




##======================================================================
## Check that OrgUnitID in child files is found in parent Course/OrgUnit
##======================================================================
## First ensure 'Course/OrgUnit/xxx.csv' exists
orgunits <- file.path(basename(path), 'Courses/OrgUnit')
org_csvs_valid <- file.exists(orgunits) && length(dir(orgunits, pattern = ".csv$|.CSV$") > 0)
dir(orgunits, pattern = ".csv$|.CSV$"); file.exists(orgunits)

if (isTRUE(org_csvs_valid)) {

    ## check personID against accounts.csv
    did_id_check_work3 <- try(
        valiData:::compare_column(
		path = basename(path),
		parent.column='OrgUnitIdentifier',
		parent='OrgUnit',
		child = c('Course', 'Section'),
		ignore.case = TRUE
        )
    )

    ## If valiData:::compare_column ran then add reporting
    ## Otherwise give error in browser
    if (inherits(did_id_check_work3, "try-error")) {

        cat(
            sprintf(html_message , "Some sort of error occurred in `valiData:::compare_column` function (when checking `OrgUnitIdentifier`)."),
    	      file = file.path(error_loc, "ERROR.html")
    	  )
    	  browseURL(file.path(error_loc, "ERROR.html"))
     	  stop("Error occurred")

    } else {

        if (file.exists(file.path(basename(path), "`Reports/Cross_File_Comparisons_Report.txt"))) {
            n_cfcr <- length(readLines(file.path(basename(path), "`Reports/Cross_File_Comparisons_Report.txt")))
        } else {
            n_cfcr <- 0
        }


        ## actually makes the report
    	  sink(
    		file.path(basename(path), "`Reports/Cross_File_Comparisons_Report.txt"),
    		append = isTRUE(acc_csvs_valid),
    		split = TRUE
    	  )
        valiData:::print.compare_column(did_id_check_work3)
    	  sink()

        ## Check if addition was successful
        ## Otherwise give error in browser
        if (!file.exists(file.path(basename(path), "`Reports/Cross_File_Comparisons_Report.txt"))) {

        	cat(
                sprintf(html_message , "Cross_File_Comparisons_Report not run for `Course/OrgUnitID`.<br>Contact...<br>"),
        	    file = file.path(error_loc, "ERROR.html")
        	)
        	browseURL(file.path(error_loc, "ERROR.html"))
    	      stop("Error occurred")

        }
        n_cfcr2 <- length(readLines(file.path(basename(path), "`Reports/Cross_File_Comparisons_Report.txt")))
        if (n_cfcr2 <= n_cfcr) {

        	cat(
                sprintf(html_message , "Cross_File_Comparisons_Report not run for `Courses/OrgUnit$OrgUnitID`.<br>Contact...<br>"),
        	    file = file.path(error_loc, "ERROR.html")
        	)
        	browseURL(file.path(error_loc, "ERROR.html"))
    	      stop("Error occurred")

        }
    }

} else {

    comp <- paste0("Could not find a single valid .csv file in  the following location to match personIDs against:\n", orgunits)
    cat(comp, file = file.path(basename(path), "`Reports/Cross_File_Comparisons_Report.txt"))

}



##=============================================================================
## Check that CourseIdentifier in child files is found in parent Courses/Course
##=============================================================================
## First ensure 'Courses/Course/xxx.csv' exists
courseid <- file.path(basename(path), 'Courses/OrgUnit')
course_csv_valid <- file.exists(courseid) && length(dir(courseid, pattern = ".csv$|.CSV$") > 0)
dir(courseid, pattern = ".csv$|.CSV$"); file.exists(courseid)

if (isTRUE(course_csv_valid)) {

    ## check personID against accounts.csv
    did_id_check_work4 <- try(
        valiData:::compare_column(
		path = basename(path),
		parent.column='CourseIdentifier',
		parent='Course',
		child = c('Section'),
		ignore.case = TRUE
        )
    )

    ## If valiData:::compare_column ran then add reporting
    ## Otherwise give error in browser
    if (inherits(did_id_check_work4, "try-error")) {

        cat(
            sprintf(html_message , "Some sort of error occurred in `valiData:::compare_column` function (when checking `OrgUnitIdentifier`)."),
    	      file = file.path(error_loc, "ERROR.html")
    	  )
    	  browseURL(file.path(error_loc, "ERROR.html"))
     	  stop("Error occurred")

    } else {

        if (file.exists(file.path(basename(path), "`Reports/Cross_File_Comparisons_Report.txt"))) {
            n_cfcr <- length(readLines(file.path(basename(path), "`Reports/Cross_File_Comparisons_Report.txt")))
        } else {
            n_cfcr <- 0
        }


        ## actually makes the report
    	  sink(
    		file.path(basename(path), "`Reports/Cross_File_Comparisons_Report.txt"),
    		append = isTRUE(acc_csvs_valid) | isTRUE(org_csvs_valid),
    		split = TRUE
    	  )
        valiData:::print.compare_column(did_id_check_work4)
    	  sink()

        ## Check if addition was successful
        ## Otherwise give error in browser
        if (!file.exists(file.path(basename(path), "`Reports/Cross_File_Comparisons_Report.txt"))) {

        	cat(
                sprintf(html_message , "Cross_File_Comparisons_Report not run for `Course/OrgUnitID`.<br>Contact...<br>"),
        	    file = file.path(error_loc, "ERROR.html")
        	)
        	browseURL(file.path(error_loc, "ERROR.html"))
    	      stop("Error occurred")

        }
        n_cfcr2 <- length(readLines(file.path(basename(path), "`Reports/Cross_File_Comparisons_Report.txt")))
        if (n_cfcr2 <= n_cfcr) {

        	cat(
                sprintf(html_message , "Cross_File_Comparisons_Report not run for `Courses/OrgUnit$OrgUnitID`.<br>Contact...<br>"),
        	    file = file.path(error_loc, "ERROR.html")
        	)
        	browseURL(file.path(error_loc, "ERROR.html"))
    	      stop("Error occurred")

        }
    }

} else {

    comp <- paste0("Could not find a single valid .csv file in  the following location to match personIDs against:\n", courseid)
    cat(comp, file = file.path(basename(path), "`Reports/Cross_File_Comparisons_Report.txt"))

}




#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Email Friendly Format
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
get_file <- function(x) stringi::stri_extract_first_regex(x[[1]], '(?<=Title: )(.+)(?=\n\t)')

##----------------
## meta level info
##----------------
did_it_work1$dir_lev



##----------------
## file level info
##----------------
files <- lapply(did_it_work1$per_file, function(x) {
	get_file(x[[1]])
})

file_info <- setNames(as.list(rep(NA, length(files))), files)

file_info[] <- lapply(did_it_work1$per_file, function(x) {

    ## file level
    file_level <- paste(unname(unlist(lapply(x[[2]]$file_level, function(x) {
          out <- trimws(stringi::stri_replace_all_regex(gsub('\\s+', ' ', x$message) , '^.+----\\s+', ''))
          if (out == "") return(NULL)
          out
    }))), collapse = "; ")


    ## table level
    table_level <- paste(unlist(lapply(x[[2]]$table_level, function(x) {
          trimws(stringi::stri_replace_all_regex(gsub('\\s+', ' ', x$message) , '^.+----\\s+', ''))
    })), collapse = "; ")


    ## column level
    column_level <- paste(unlist(lapply(x[[2]]$column_level, function(x) {
          messages <- unlist(lapply(x, function(y) y$message))
          trimws(stringi::stri_replace_all_regex(gsub('\\s+', ' ', messages) , '^.+----\\s+', ''))
    })), collapse = "; ")

    out <- list(file_level = file_level, table_level = table_level, column_level = column_level)
    out <- lapply(out, function(x) {
        if (x == "") return(NULL)
        x
    })
    out <- paste(unlist(out), collapse = "; ")
    if (out == "") return(NULL)
    out

})


##----------------------
## Cross file level info
##----------------------
cross_file <- unlist(list(
    setNames(lapply(did_id_check_work2[[2]], function(x) x$message), unlist(lapply(did_id_check_work2[[1]], get_file))),
    setNames(lapply(did_id_check_work3[[2]], function(x) x$message), unlist(lapply(did_id_check_work3[[1]], get_file))),
    setNames(lapply(did_id_check_work4[[2]], function(x) x$message), unlist(lapply(did_id_check_work4[[1]], get_file)))
), recursive = FALSE)

cross_file <- cross_file[!sapply(cross_file, is.null)]

if (length(cross_file) > 0){
    for (i in seq_along(cross_file)) {
        file_info[names(cross_file)[i]] <- paste(unname(unlist(list(file_info[names(cross_file)[i]], cross_file[i]))), collapse = "; ")
    }
}

file_info[sapply(file_info, is.null)] <- 'Ready to Import'


## actually makes the report
sink(
    file.path(basename(path), "`Reports/Email_Summary.txt"),
    append = FALSE,
    split = TRUE
)
cat(valiData:::header('Email', char = "="))
cat('We reviewed the files that you uploaded and found the following:\n\n\n')
cat(paste(unlist(Map(function(x, y) {paste(paste0("- ", x), y, sep = " - ")}, names(file_info), file_info)), collapse = "\n"), '\n\n\n\n\n')
cat(valiData:::header('Other Issues', char = "="))
invisible(lapply(did_it_work1$dir_lev, print))
sink()



















