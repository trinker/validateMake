#' Get User's Desktop
#'
#' Find the path to a viable CL user's desktop.
#'
#' @return Returns a path.
#' @export
#' @examples
#' get_desktop()
get_desktop <- function(){

    if (.Platform$OS.type!="windows"){
        return(file.path(path.expand("~"),"Desktop"))
    }

    locs <- c('OneDrive for Business', 'OneDrive - Campus Labs')
    front <- Sys.getenv("USERPROFILE")

    paths <- file.path(front, c(file.path(locs, "Desktop"), "Desktop"))
    paths[file.exists(paths)][1]
}
