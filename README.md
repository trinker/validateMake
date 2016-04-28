1. Install R in root directory (`C:`): https://cran.r-project.org
2. Install RTools: https://cran.r-project.org
3. From R's command line run the following script:

```
install.packages(c('devtools', 'pacman'))
if (!require("pacman")) install.packages("pacman")
pacman::p_install_gh(c("data-steve/valiData", 'trinker/validateMake'))
validateMake::validate_make()
```
