1. Install R in root directory (`C:`): https://cran.r-project.org
2. Install RTools: https://cran.r-project.org
3. From R's command line run the following script:

```
if (!require("pacman")) install.packages("pacman")
pacman::p_load_current_gh(c("data-steve/valiData", 'trinker/validateMake'), dependencies = TRUE)
validateMake::validate_make()
```
