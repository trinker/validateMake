#version:  030
This app is a validator program for validating data inputs against a Campus Labs Core Data Dictionary (CDD) of expected file and variable types.

For a video demonstration of these instructions go to: 
https://campuslabsinc.sharepoint.com/sites/DataScience/_layouts/15/guestaccess.aspx?guestaccesstoken=7yVAkpyj%2b9Zyae3cGcB5YntO2bUCESpHLpOGwq8ntgI%3d&docid=2_02a65d72c341b41caaa0f47aa01b6a81c&rev=1

-------------
Installation:
-------------

You can get the newest version from:

https://campuslabsinc.sharepoint.com/sites/DataScience/Shared%20Documents/Data%20Validating/TestCore_v.030.zip

1. Unzip TestCore .zip in a utility program such as 7zip (Microsoft may warn you that it's a high risk because it is a .zip file; you can ignore this)
2. Place the unzipped program directory where ever you'd like
3. Go to '~\TestCore\bin' and press the 'install_r.bat' button (may appear as just 'install_r')
4. This will install the R program

You're ready to validate Core Data files.

------
Usage:
------

1. Move an institution core data folder inside of 'TestCore' directory
2. Click 'button.bat' (may appear as just 'button')

-------
Output:
-------

The institution core data file will now contain a '`Reports' file inside which houses:

	- `valiData_report.txt`
	- `Cross_File_Comparisons_Report.txt`
	- `Org_Unit_Structure.txt`
	- `Email_Summary.txt`

The first one checks that each file meets the schema expectations from the CDD.  The second file ensures cross file expectations are met.  For example, it ensures that if a `CourseIdentifier` is found in the file 'Courses/Section/xxx.csv' then these elements must also be found in the parent 'Courses/Course/xxx.csv'.  The third file prints a tree structure for the org unit from the Courses directory if this file exists and has the proper headers.  The last file is an email prepared version of the errors from the first 2 reports.
