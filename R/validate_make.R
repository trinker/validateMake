#' Generate a validate program
#'
#' Generate a validate program
#'
#' @param path TestCore path
#' @export
validate_make <- function(path = file.path(Sys.getenv("USERPROFILE"), "Desktop/TestCore")){
    if (.Platform$OS.type!="windows"){
        path <- file.path(path.expand("~"),"Desktop/TestCore")
    }
    if (path == Sys.getenv("R_HOME"))
        stop("path can not be `R_HOME`")
    if (file.exists(path)) {
        message(paste0("\"", path, "\" already exists:\nDo you want to overwrite?\n"))
        ans <- menu(c("Yes", "No"))
        if (ans == "2") {
            stop("project aborted")
        } else {
            unlink(path, recursive = TRUE, force = FALSE)
        }
    }

    suppressWarnings(invisible(dir.create(path, recursive = TRUE)))
    if (.Platform$OS.type=="windows"){

        button <- paste0('@echo off', '\n', shQuote(file.path(R.home(), "bin", "R")),
                         ' CMD BATCH --no-save --no-restore ',
                         '"C:\\Users\\%username%\\Desktop\\TestCore\\update.R" "L:\\Products\\Data_Science\\Data_Valiadtion\\Validation_Outputs\\%username%.Rout"',
                         '\n\n', shQuote(file.path(R.home(), "bin", "R")),
                         ' CMD BATCH --no-save --no-restore ',
                         '"C:\\Users\\%username%\\Desktop\\TestCore\\validate.R" "L:\\Products\\Data_Science\\Data_Valiadtion\\Validation_Outputs\\%username%.Rout"',
                         '\n'
        )

        # make button.bat
        cat(button, file=file.path(path, 'button.bat'))
        } else {
        button <- paste0('#! /bin/bash', '\n', 
             'Rscript /Volumes/shared/swiper/CoreData/valiData_user_research/valiData_use.R  --no-save --no-restore',
             " '", file.path(path,"update.R")," ", paste0('/Volumes/shared/Products/Data_Science/Data_Valiadtion/Validation_Outputs/',Sys.getenv("USER"),".Rout"),"'",
             '\n\n', , 
             'Rscript /Volumes/shared/swiper/CoreData/valiData_user_research/valiData_use.R  --no-save --no-restore',
             " '", file.path(path,"validate.R"),  paste0('/Volumes/shared/Products/Data_Science/Data_Valiadtion/Validation_Outputs/',Sys.getenv("USER"),".Rout"),"'",
             '\n'
        )

        # make button.command
        cat(button, file=file.path(path, 'button.command'))
        system("cd ~/Desktop/TestCore;chmod 755 button.command;")
        }

    #copy update.R, validate.R script, and README
    script <- system.file("extradocs", package = "validateMake")
    file.copy(dir(script, full.names = TRUE), file.path(path, dir(script)), TRUE)

    verify <- sum(c("button.bat", "button.command", "README.txt", "validate.R", "update.R") %in% dir(path, all.files = TRUE))==4

    if (isTRUE(verify)) {
        message("Looks like everything went according to plan...")
    } else {
        message("Major bummer :-\\ \nLooks like some components of the project validateTemplate are missing...")
    }
}


