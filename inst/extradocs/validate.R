#version: 1.43
html_message <- "<!doctype html>\n<html>\n<head>\n<title>HTML min</title>\n</head>\n<body><p style='font-size: 200%%'>\n%s  Contact Data Science with the following items:<br><ul><li>The institution files that were tested (zip them)</li><li>'~/TestCore/bin/validate.Rout file'</li></ul></p><br><br><br><br><br><br><img src=\"http://drinkboxstudios.com/blog/wp-content/uploads/2012/02/simpsons-doh2_480x360.jpg\" width=\"540\" height=\"360\"></body>\n</html>"


#=====================
## directory variables
#=====================
error_loc <- file.path(getwd(), 'bin/errors')
map_loc <- 'bin/Core_Data_Dictionary_DS_longforms.xlsx'




#=====================
# Install dependencies
#=====================
options(repos="http://cran.rstudio.com/")
#if (!require("rlang") | utils::packageVersion('rlang') < '0.2.0') install.packages("rlang")
if (!require("DiagrammeR")) install.packages("DiagrammeR")
if (!require("data.tree")) install.packages("data.tree", type = 'binary')
if (!require("cellranger")) install.packages("cellranger")
if (!require("hms")) install.packages("hms")
if (!require("dplyr")) install.packages("dplyr")
if (!require("tibble")) install.packages("tibble")
if (!require("data.table")) install.packages("data.table")
if (!require("devtools")) install.packages("devtools")
if (!require("readr")) install.packages("readr")
if (!require("textshape")) install.packages("textshape")
devtools::install_github("trinker/valiData")

update.packages(ask = FALSE, checkBuilt = TRUE)


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
# Additional non valiData cross file checking
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
did_id_check_work2 <- NULL
did_id_check_work3 <- NULL
did_id_check_work4 <- NULL
did_id_check_work5 <- NULL
did_id_check_work6 <- NULL
did_id_check_work7 <- NULL
did_id_check_work8 <- NULL

##========================================================
## Check that personID in child files is found in accounts
##========================================================
## First ensure 'Accounts/AccountImports/xxx.csv' exists
accts <- file.path(basename(path), 'Accounts/AccountImports')
acc_csvs_valid <- file.exists(accts) && length(dir(accts, pattern = ".csv$|.CSV$")) > 0
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
        if(!is.null(did_id_check_work2$call) && did_id_check_work2$call == "vt_duplicated_rows"){
            print(did_id_check_work2)
        } else {
            valiData:::print.compare_column(did_id_check_work2)
        }
        sink()

        ## Check if addition was successful
        ## Otherwise give error in browser
        if (!file.exists(file.path(basename(path), "`Reports/Cross_File_Comparisons_Report.txt"))) {

            cat(
                sprintf(html_message , "Cross_File_Comparisons_Report not run.<br><br>"),
                file = file.path(error_loc, "ERROR.html")
            )
            browseURL(file.path(error_loc, "ERROR.html"))
              stop("Error occurred")

        }
    }

} else {

    comp <- paste0("Could not find a single valid .csv file in  the following location to match personIDs against:\n", accts, '\n\n\n')
    cat(comp, file = file.path(basename(path), "`Reports/Cross_File_Comparisons_Report.txt"))

}




##======================================================================
## Check that OrgUnitID in child files is found in parent Course/OrgUnit
##======================================================================
## First ensure 'Course/OrgUnit/xxx.csv' exists
orgunits <- file.path(basename(path), 'Courses/OrgUnit')
org_csvs_valid <- file.exists(orgunits) && length(dir(orgunits, pattern = ".csv$|.CSV$")) > 0
dir(orgunits, pattern = ".csv$|.CSV$"); file.exists(orgunits)

if (isTRUE(org_csvs_valid)) {

    ## check personID against accounts.csv
    did_id_check_work3 <- try(
        valiData:::compare_column(
            path = basename(path),
            parent.column='OrgUnitIdentifier',
            parent='OrgUnit',
            child = c('Course', 'Section'),
            ignore.case = TRUE,
            ignore.element.case = TRUE
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

        if(!is.null(did_id_check_work3$call) && did_id_check_work3$call == "vt_duplicated_rows"){
            print(did_id_check_work3)
        } else {
            valiData:::print.compare_column(did_id_check_work3)
        }
          sink()

        ## Check if addition was successful
        ## Otherwise give error in browser
        if (!file.exists(file.path(basename(path), "`Reports/Cross_File_Comparisons_Report.txt"))) {

            cat(
                sprintf(html_message , "Cross_File_Comparisons_Report not run for `Course/OrgUnitID`.<br><br>"),
                file = file.path(error_loc, "ERROR.html")
            )
            browseURL(file.path(error_loc, "ERROR.html"))
              stop("Error occurred")

        }
        n_cfcr2 <- length(readLines(file.path(basename(path), "`Reports/Cross_File_Comparisons_Report.txt")))
        if (length(did_id_check_work3$validated) > 0 && n_cfcr2 <= n_cfcr) {

            cat(
                sprintf(html_message , "Cross_File_Comparisons_Report not run for `Courses/OrgUnit$OrgUnitID`.<br><br>"),
                file = file.path(error_loc, "ERROR.html")
            )
            browseURL(file.path(error_loc, "ERROR.html"))
              stop("Error occurred")

        }
    }

} else {

    comp <- paste0("Could not find a single valid .csv file in  the following location to match personIDs against:\n", orgunits, '\n\n\n')

    sink(
        file.path(basename(path), "`Reports/Cross_File_Comparisons_Report.txt"),
        append = isTRUE(acc_csvs_valid),
        split = TRUE
    )

    cat(comp)

    sink()
}



##=============================================================================
## Check that CourseIdentifier in child files is found in parent Courses/Course
##=============================================================================
## First ensure 'Courses/Course/xxx.csv' exists
courseid <- file.path(basename(path), 'Courses/Course')
course_csv_valid <- file.exists(courseid) && length(dir(courseid, pattern = ".csv$|.CSV$")) > 0
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
        if(!is.null(did_id_check_work4$call) && did_id_check_work4$call == "vt_duplicated_rows"){
            print(did_id_check_work4)
        } else {
            valiData:::print.compare_column(did_id_check_work4)
        }
          sink()

        ## Check if addition was successful
        ## Otherwise give error in browser
        if (!file.exists(file.path(basename(path), "`Reports/Cross_File_Comparisons_Report.txt"))) {

            cat(
                sprintf(html_message , "Cross_File_Comparisons_Report not run for `Course/OrgUnitID`.<br><br>"),
                file = file.path(error_loc, "ERROR.html")
            )
            browseURL(file.path(error_loc, "ERROR.html"))
              stop("Error occurred")

        }
        n_cfcr2 <- length(readLines(file.path(basename(path), "`Reports/Cross_File_Comparisons_Report.txt")))
        if (length(did_id_check_work4$validated) > 0 && n_cfcr2 <= n_cfcr) {

            cat(
                sprintf(html_message , "Cross_File_Comparisons_Report not run for `Courses/OrgUnit$OrgUnitID`.<br><br>"),
                file = file.path(error_loc, "ERROR.html")
            )
            browseURL(file.path(error_loc, "ERROR.html"))
              stop("Error occurred")

        }
    }

} else {

    comp <- paste0("Could not find a single valid .csv file in  the following location to match personIDs against:\n", courseid, '\n\n\n')

    sink(
        file.path(basename(path), "`Reports/Cross_File_Comparisons_Report.txt"),
        append = isTRUE(acc_csvs_valid),
        split = TRUE
    )

    cat(comp)

    sink()
}



##======================================================================
## Check that SectionIdentifier in child files is found in parent Section (round 1)
##======================================================================
## First ensure 'Course/Section/xxx.csv' exists
sect <- file.path(basename(path), 'Courses/Section')
sect_csvs_valid <- file.exists(sect) && length(dir(sect, pattern = ".csv$|.CSV$")) > 0
dir(sect, pattern = ".csv$|.CSV$"); file.exists(sect)

if (isTRUE(sect_csvs_valid)) {

    ## check personID against accounts.csv
    did_id_check_work5 <- try(
        valiData:::compare_column(
        path = basename(path),
        parent.column='SectionIdentifier',
            child.column = 'Identifier',
        parent='Section',
        child = c('SectionAttribute'),
        ignore.case = TRUE
        )
    )

    ## If valiData:::compare_column ran then add reporting
    ## Otherwise give error in browser
    if (inherits(did_id_check_work5, "try-error")) {

        cat(
            sprintf(html_message , "Some sort of error occurred in `valiData:::compare_column` function (when checking `SectionIdentifier` (round 1))."),
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
            append = isTRUE(acc_csvs_valid) | isTRUE(org_csvs_valid) | isTRUE(course_csv_valid),
            split = TRUE
          )
        if(!is.null(did_id_check_work5$call) && did_id_check_work5$call == "vt_duplicated_rows"){
            print(did_id_check_work5)
        } else {
            valiData:::print.compare_column(did_id_check_work5)
        }
          sink()

        ## Check if addition was successful
        ## Otherwise give error in browser
        if (!file.exists(file.path(basename(path), "`Reports/Cross_File_Comparisons_Report.txt"))) {

            cat(
                sprintf(html_message , "Cross_File_Comparisons_Report not run for `Course/OrgUnitID`.<br><br>"),
                file = file.path(error_loc, "ERROR.html")
            )
            browseURL(file.path(error_loc, "ERROR.html"))
              stop("Error occurred")

        }
        n_cfcr2 <- length(readLines(file.path(basename(path), "`Reports/Cross_File_Comparisons_Report.txt")))
        if (length(did_id_check_work5$validated) > 0 && n_cfcr2 <= n_cfcr) {

            cat(
                sprintf(html_message , "Cross_File_Comparisons_Report not run for `Courses/Section$SectionID (round 1)`.<br><br>"),
                file = file.path(error_loc, "ERROR.html")
            )
            browseURL(file.path(error_loc, "ERROR.html"))
              stop("Error occurred")

        }
    }

} else {

    comp <- paste0("Could not find a single valid .csv file in  the following location to match personIDs against:\n", sect, '\n\n\n')

    sink(
        file.path(basename(path), "`Reports/Cross_File_Comparisons_Report.txt"),
        append = isTRUE(acc_csvs_valid),
        split = TRUE
    )

    cat(comp)

    sink()
}


##======================================================================
## Check that SectionIdentifier in child files is found in parent Section (round 2)
##======================================================================
## First ensure 'Course/Section/xxx.csv' exists
if (isTRUE(sect_csvs_valid)) {

    ## check personID against accounts.csv
    did_id_check_work6 <- try(
        valiData:::compare_column(
        path = basename(path),
        parent.column='SectionIdentifier',
        parent='Section',
        child = c('Instructor', 'Enrollment'),
        ignore.case = TRUE
        )
    )

    ## If valiData:::compare_column ran then add reporting
    ## Otherwise give error in browser
    if (inherits(did_id_check_work6, "try-error")) {

        cat(
            sprintf(html_message , "Some sort of error occurred in `valiData:::compare_column` function (when checking `SectionIdentifier` (round 2))."),
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
            append = isTRUE(acc_csvs_valid) | isTRUE(org_csvs_valid) | isTRUE(course_csv_valid) | isTRUE(sect_csvs_valid),
            split = TRUE
          )
        if(!is.null(did_id_check_work6$call) && did_id_check_work6$call == "vt_duplicated_rows"){
            print(did_id_check_work6)
        } else {
            valiData:::print.compare_column(did_id_check_work6)
        }
          sink()

        ## Check if addition was successful
        ## Otherwise give error in browser
        if (!file.exists(file.path(basename(path), "`Reports/Cross_File_Comparisons_Report.txt"))) {

            cat(
                sprintf(html_message , "Cross_File_Comparisons_Report not run for `Courses/Section$SectionID (round 2)`.<br><br>"),
                file = file.path(error_loc, "ERROR.html")
            )
            browseURL(file.path(error_loc, "ERROR.html"))
              stop("Error occurred")

        }
        n_cfcr2 <- length(readLines(file.path(basename(path), "`Reports/Cross_File_Comparisons_Report.txt")))
        if (length(did_id_check_work6$validated) > 0 && n_cfcr2 <= n_cfcr) {

            cat(
                sprintf(html_message , "Cross_File_Comparisons_Report not run for `Courses/Section$SectionID`.<br><br>"),
                file = file.path(error_loc, "ERROR.html")
            )
            browseURL(file.path(error_loc, "ERROR.html"))
              stop("Error occurred")

        }
    }

}

##======================================================================
## Check that Section/TermIdentifier in child files is found in parent AcademicTerm/TermIdentifier
##======================================================================
## Ensure parent exists 'Section/AcademicTerm/xxx.csv' exists
acadident <- file.path(basename(path), 'Courses/AcademicTerm')
acad_csvs_valid <- file.exists(acadident) && length(dir(acadident, pattern = ".csv$|.CSV$")) > 0
dir(acadident, pattern = ".csv$|.CSV$"); file.exists(acadident)

termident <- file.path(basename(path), 'Courses/Section')
term_csvs_valid <- file.exists(termident) && length(dir(termident, pattern = ".csv$|.CSV$")) > 0
dir(termident, pattern = ".csv$|.CSV$"); file.exists(termident)


if (!isTRUE(acad_csvs_valid)) {

    comp <- paste0("No valid .csv file in  the following location to match personIDs against:\n", acadident, '\n\n\n')

    sink(
        file.path(basename(path), "`Reports/Cross_File_Comparisons_Report.txt"),
        append = isTRUE(acad_csvs_valid),
        split = TRUE
    )

    cat(comp)

    sink()

    term_csvs_valid <- acad_csvs_valid

} else {

    ## First ensure 'Section/TermIdentifier/xxx.csv' exists
    termident<- file.path(basename(path), 'Courses/Section')
    term_csvs_valid <- file.exists(termident) && length(dir(termident, pattern = ".csv$|.CSV$")) > 0
    dir(termident, pattern = ".csv$|.CSV$"); file.exists(termident)

    if (isTRUE(term_csvs_valid)) {

        ## check personID against accounts.csv
        did_id_check_work7 <- try(
            valiData:::compare_column(
            path = basename(path),
            parent.column='TermIdentifier',
            parent='AcademicTerm',
            child = c('Section'),
            ignore.case = TRUE
            )
        )

        ## If valiData:::compare_column ran then add reporting
        ## Otherwise give error in browser
        if (inherits(did_id_check_work7, "try-error")) {

            cat(
                sprintf(html_message , "Some sort of error occurred in `valiData:::compare_column` function (when checking TermIdentifier`)."),
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
                append = isTRUE(acc_csvs_valid) | isTRUE(org_csvs_valid) | isTRUE(course_csv_valid) | isTRUE(sect_csvs_valid),
                split = TRUE
              )
            if(!is.null(did_id_check_work7$call) && did_id_check_work7$call == "vt_duplicated_rows"){
                print(did_id_check_work7)
            } else {
                valiData:::print.compare_column(did_id_check_work7)
            }
              sink()

            ## Check if addition was successful
            ## Otherwise give error in browser
            if (!file.exists(file.path(basename(path), "`Reports/Cross_File_Comparisons_Report.txt"))) {

                cat(
                    sprintf(html_message , "Cross_File_Comparisons_Report not run for `AcademicTerm/TermIdentifier`.<br><br>"),
                    file = file.path(error_loc, "ERROR.html")
                )
                browseURL(file.path(error_loc, "ERROR.html"))
                  stop("Error occurred")

            }
            n_cfcr2 <- length(readLines(file.path(basename(path), "`Reports/Cross_File_Comparisons_Report.txt")))
            if (length(did_id_check_work7$validated) > 0 && n_cfcr2 <= n_cfcr) {

                cat(
                    sprintf(html_message , "Cross_File_Comparisons_Report not run for `AcademicTerm/TermIdentifier`.<br><br>"),
                    file = file.path(error_loc, "ERROR.html")
                )
                browseURL(file.path(error_loc, "ERROR.html"))
                  stop("Error occurred")

            }
        }

    } else {

        comp <- paste0("Could not find a single valid .csv file in  the following location to match personIDs against:\n", termident, '\n\n\n')

        sink(
            file.path(basename(path), "`Reports/Cross_File_Comparisons_Report.txt"),
            append = isTRUE(acc_csvs_valid),
            split = TRUE
        )

        cat(comp)

        sink()
    }
}


##======================================================================
## Check that OrgUnit/ParentIdenitifer in child files is found in parent OrgUnit/OrgUnit
##======================================================================
## First ensure 'Section/TermIdentifier/xxx.csv' exists
orgident<- file.path(basename(path), 'Courses/OrgUnit')
org_csvs_valid <- file.exists(orgident) && length(dir(orgident, pattern = ".csv$|.CSV$")) > 0
dir(orgident, pattern = ".csv$|.CSV$"); file.exists(orgident)

if (isTRUE(org_csvs_valid)) {

    ## check personID against accounts.csv
    did_id_check_work8 <- try(
        valiData:::compare_column(
            path = basename(path),
            parent.column='OrgUnitIdentifier',
            parent='OrgUnit',
            child = c('OrgUnit'),
            child.column = 'ParentIdentifier',
            ignore.case = TRUE,
            ignore.element.case = TRUE
        )
    )

    ## If valiData:::compare_column ran then add reporting
    ## Otherwise give error in browser
    if (inherits(did_id_check_work8, "try-error")) {

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
            append = isTRUE(acc_csvs_valid) | isTRUE(org_csvs_valid) | isTRUE(course_csv_valid) | isTRUE(sect_csvs_valid) | isTRUE(term_csvs_valid),
            split = TRUE
          )
        if(!is.null(did_id_check_work8$call) && did_id_check_work8$call == "vt_duplicated_rows"){
            print(did_id_check_work8)
        } else {
            valiData:::print.compare_column(did_id_check_work8)
        }
          sink()

        ## Check if addition was successful
        ## Otherwise give error in browser
        if (!file.exists(file.path(basename(path), "`Reports/Cross_File_Comparisons_Report.txt"))) {

            cat(
                sprintf(html_message , "Cross_File_Comparisons_Report not run for `AcademicTerm/TermIdentifier`.<br><br>"),
                file = file.path(error_loc, "ERROR.html")
            )
            browseURL(file.path(error_loc, "ERROR.html"))
              stop("Error occurred")

        }
        n_cfcr2 <- length(readLines(file.path(basename(path), "`Reports/Cross_File_Comparisons_Report.txt")))
        if (length(did_id_check_work8$validated) > 0 && n_cfcr2 <= n_cfcr) {

            cat(
                sprintf(html_message , "Cross_File_Comparisons_Report not run for `Courses/OrgUnitIdentifier`.<br><br>"),
                file = file.path(error_loc, "ERROR.html")
            )
            browseURL(file.path(error_loc, "ERROR.html"))
              stop("Error occurred")

        }
    }

} else {

    comp <- paste0("Could not find a single valid .csv file in  the following location to match OrgUnitIdentifiers against:\n", orgident, '\n\n\n')

    sink(
        file.path(basename(path), "`Reports/Cross_File_Comparisons_Report.txt"),
        append = isTRUE(acc_csvs_valid),
        split = TRUE
    )

    cat(comp)

    sink()
}


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Email Friendly Format
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
get_file <- function(x) {

    if (!grepl('Title:', x)) return(x)
    stringi::stri_extract_first_regex(x[[1]], '(?<=Title: )(.+)(?=\n\t)')

}

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
    file_level <- paste(trimws(unname(unlist(lapply(x[[2]]$file_level, function(x) {
          out <- trimws(stringi::stri_replace_all_regex(gsub('\\s+', ' ', x$message) , '^.+----\\s+', ''))
          if (out == "") return(NULL)
          out
    })))), collapse = "; ")


    ## table level
    table_level <- paste(unlist(lapply(x[[2]]$table_level, function(z) {
        if (!is.null(z) && !isTRUE(z$valid)) {
          message <- paste(trimws(stringi::stri_replace_all_regex(gsub('\\s+', ' ', capture.output(print(z))) , '^.+----\\s+', '')), collapse = " ")
          trimws(gsub("^[^']+", "", message))
        } else {

            NULL
        }
    })), collapse = "; ")


    ## column level
    column_level <- paste(trimws(unlist(lapply(x[[2]]$column_level, function(x) {
          messages <- unlist(lapply(x, function(y) y$message))
          trimws(stringi::stri_replace_all_regex(gsub('\\s+', ' ', messages) , '^.+----\\s+', ''))
    }))), collapse = "; ")

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
if (inherits(did_id_check_work2, 'try-error') || is.null(did_id_check_work2)) did_id_check_work2 <- list(NULL, NULL)
if (inherits(did_id_check_work3, 'try-error') || is.null(did_id_check_work3)) did_id_check_work3 <- list(NULL, NULL)
if (inherits(did_id_check_work4, 'try-error') || is.null(did_id_check_work4)) did_id_check_work4 <- list(NULL, NULL)
if (inherits(did_id_check_work5, 'try-error') || is.null(did_id_check_work5)) did_id_check_work5 <- list(NULL, NULL)
if (inherits(did_id_check_work6, 'try-error') || is.null(did_id_check_work6)) did_id_check_work6 <- list(NULL, NULL)
if (inherits(did_id_check_work7, 'try-error') || is.null(did_id_check_work7)) did_id_check_work7 <- list(NULL, NULL)
if (inherits(did_id_check_work8, 'try-error') || is.null(did_id_check_work8)) did_id_check_work8 <- list(NULL, NULL)


check_dupes <- function(x){

    if (is.null(x$call)) return(x)
    if(x$call == "vt_duplicated_rows") {
        list(
            list(file_name = x$file_name),
            mess=list(mess = list(message=paste0("The following rows of the parent key were duplicated and cross file checking with this file could not be completed: ", x$locations)))

        )
    } else {
        x
    }
}

did_id_check_work2 <- check_dupes(did_id_check_work2)
did_id_check_work3 <- check_dupes(did_id_check_work3)
did_id_check_work4 <- check_dupes(did_id_check_work4)
did_id_check_work5 <- check_dupes(did_id_check_work5)
did_id_check_work6 <- check_dupes(did_id_check_work6)
did_id_check_work7 <- check_dupes(did_id_check_work7)
did_id_check_work8 <- check_dupes(did_id_check_work8)


cross_file <- unlist(list(
    setNames(lapply(did_id_check_work2[[2]], function(x) x$message), unlist(lapply(did_id_check_work2[[1]], get_file))),
    setNames(lapply(did_id_check_work3[[2]], function(x) x$message), unlist(lapply(did_id_check_work3[[1]], get_file))),
    setNames(lapply(did_id_check_work4[[2]], function(x) x$message), unlist(lapply(did_id_check_work4[[1]], get_file))),
    setNames(lapply(did_id_check_work5[[2]], function(x) x$message), unlist(lapply(did_id_check_work5[[1]], get_file))),
    setNames(lapply(did_id_check_work6[[2]], function(x) x$message), unlist(lapply(did_id_check_work6[[1]], get_file))),
    setNames(lapply(did_id_check_work7[[2]], function(x) x$message), unlist(lapply(did_id_check_work7[[1]], get_file))),
    setNames(lapply(did_id_check_work8[[2]], function(x) x$message), unlist(lapply(did_id_check_work8[[1]], get_file)))
), recursive = FALSE)

cross_file <- lapply(cross_file[!sapply(cross_file, is.null)], function(x) gsub('\\s+', ' ', x))

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



## Check if email report ran otherwise give error in browser
if (!file.exists(file.path(basename(path), "`Reports/Email_Summary.txt"))) {
    cat(
        sprintf(html_message, "The `Email_Summary.txt` report does not appear to have been generated."),
        file = file.path(error_loc, "ERROR.html")
    )
    browseURL(file.path(error_loc, "ERROR.html"))

    stop("Error occurred")

}


##=====================
## Print Org Unit Chart
##=====================
## First ensure 'Courses/OrgUnit/xxx.csv' exists
orgident <- file.path(basename(path), 'Courses/OrgUnit')
org_csvs_valid <- file.exists(orgident) && length(dir(orgident, pattern = ".csv$|.CSV$")) > 0
dir(orgident, pattern = ".csv$|.CSV$"); file.exists(orgident)

filter_all_na <- function(dat) {
  dat %>% filter(Reduce(`+`, lapply(., is.na)) != ncol(.))
}


## if else prints org tree or no valid csv
if (isTRUE(org_csvs_valid)) {

    org <- readr::read_csv(dir(orgident, pattern = ".csv$|.CSV$", full.names = TRUE)) %>%
        stats::setNames(tolower(names(.))) %>%
        mutate(
            parentidentifier = tolower(parentidentifier),
            orgunitidentifier = tolower(orgunitidentifier)
        )

    colnames_exist <- all(c("orgunitidentifier", "name", "parentidentifier") %in% colnames(org))

    if (colnames_exist) {

        org <- filter_all_na(org[c("orgunitidentifier", "name", "parentidentifier")])

        nas <- sum(is.na(org[['parentidentifier']]))

        if (nas == 1) {

            key <- org %>%
                dplyr::select(orgunitidentifier, name) %>%
                stats::setNames(c('id', 'name'))

            key2 <- org %>%
                dplyr::select(orgunitidentifier, parentidentifier)

            struct <- apply(key2, 1, function(x){

                if (is.na(x[['parentidentifier']])) return(x[['orgunitidentifier']])
                par <- x[['parentidentifier']]
                path4errors <- path2 <- unlist(x)
                i <- length(path2) + 1
                iterations <- 100
                can_recurse <- TRUE

                while(!is.na(par) & can_recurse){

                    if (!par %in% key2[['orgunitidentifier']]){
                        can_recurse <- FALSE
                        break
                    }

                    if (length(path2) > iterations){
                        can_recurse <- FALSE
                        break
                    }
                    path2[i] <- key2[['parentidentifier']][match(par, key2[['orgunitidentifier']])]
                    par <- path2[i]
                    i <- i + 1

                }

                if (!can_recurse) {
                    return(NULL)
                }

                return(rev(c(stats::na.omit(unname(path2)))))
            })

            non_recurse_locs <- unlist(lapply(struct, function(x) any(is.null(x))))
            if (sum(non_recurse_locs) > 0 ) {
                cat(paste0(
                    'Can\'t recurse the tree in some locations.\n\nOrphaned Organizational Units Found in Org Chart at:\n',
                    paste(which(non_recurse_locs) + 1, collapse = ', ')
                    ),
                    '\n', file = file.path(path, "`Reports/Org_Unit_Structure.txt")
                )
                stop("Orphaned Organizational Units Found in Org Chart")
            }

            tree <- struct  %>%
                textshape::tidy_list('org', 'path') %>%
                dplyr::left_join(key, by = c('path' = 'id')) %>%
                dplyr::group_by(org) %>%
                dplyr::summarize(pathString = paste(unlist(name), collapse = '<<>>')) %>%
                dplyr::arrange(pathString) %>%
                data.tree::as.Node(pathDelimiter = '<<>>')

            ptree <- gsub("\\G\\d", ' ', capture.output(print(tree, limit = NULL)), perl = TRUE)[-1]
            rep <- paste('^', gsub('(^\\s+)(\\s\\S.+$)', '\\1', ptree[1]))

            cat(paste0(
                valiData:::header('Org Chart', char = "="),
                paste(
                    gsub(rep, '', ptree),
                    collapse = '\n')), '\n',
                file = file.path(basename(path), "`Reports/Org_Unit_Structure.txt")
            )

        } else {

            end <- ifelse(
                nas == 0,
                "' does not contain a single empty value.",
                "' contains multiple empty values.\nShould only be one empty for the top of the org chart."
            )
            comp <- paste0("The CSV file in '", orgident, end)
            cat(comp, '\n', file = file.path(basename(path), "`Reports/Org_Unit_Structure.txt"))

        }

    } else {

        comp <- paste0("The CSV file in '", orgident, "' does not have the correct column headers; no org chart made")
        cat(comp, '\n', file = file.path(basename(path), "`Reports/Org_Unit_Structure.txt"))


    }

} else {

    comp <- paste0("Could not find a single valid .csv file in  the following location to produce an org chart:\n", orgident)
    cat(comp, '\n', file = file.path(basename(path), "`Reports/Org_Unit_Structure.txt"))

}


print('finished')




