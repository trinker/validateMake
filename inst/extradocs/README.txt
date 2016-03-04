1. Install R in your C directory: https://cran.r-project.org/bin/windows/base/
    - Looks like: C:\R\R-3.2.3\bin\x64\R.exe
2. Install RTools in your C directory: https://cran.r-project.org/bin/windows/Rtools/
3. Move the `TestCore` file to your Desktop (e.g., C:\Users\trinker\Desktop\TestCore)
    - Use validateMake package for easy install:
        if (!require("pacman")) install.packages("pacman")
        pacman::p_install_gh('trinker/validateMake')
        validateMake::validate_make()
4. Move an institution core data file inside of TestCore
5. Click button.bat/button file

The institution core data file will be moved to the Desktop with a '`Reports' file inside that contains the validation report for that institution.
