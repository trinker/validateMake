1. Install R in root directory (`C:`): https://cran.r-project.org
2. Install RTools: https://cran.r-project.org
3. From R's command line run the following script:

```
if (!require("devtools")) install.packages("devtools")
devtools::install_github(c("data-steve/valiData", 'trinker/validateMake'), dependencies = TRUE)
validateMake::validate_make()
```
