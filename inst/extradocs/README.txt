#version:  033
This app is a Windows based validator program for validating data inputs against the Core Data Dictionary (CDD) of expected file and variable types.  It utilizes a .bat file to run R scripts that validate file structure, field names, and cell inputs.

For a video demonstration of these instructions go to: 
https://anthologyinc.sharepoint.com/:v:/s/DataScienceCL/ERXYDxCNtPVKsZgrQ3YSGyUBn4n4MkAsPYVKGLiNBJjLMg?e=A4ao61

-------------
Installation:
-------------

You can get the newest version from:

https://anthologyinc.sharepoint.com/:f:/s/DataScienceCL/EnBR5MPwq41GlBGTeoerzAgBgbIpxU4MQZ0Y_hm_fIBklQ?e=rDUvcq

1.  Select version the latest version .zip file (TestCor_v.###.zip) 
2. Unzip TestCore .zip in a utility program such as 7zip (Microsoft may warn you that it's a high risk because it is a .zip file; you can ignore this)
3. Place the unzipped program directory where ever you'd like
4. For both 'bin/install_r.bat' and 'button.bat' files:
    a. Right-click 
	b. Properties 
	C. Uncheck the "Unblock" option on the properties tab
	D. Apply and Save 
5. Go to '~\TestCore\bin' and press the 'install_r.bat' button (may appear as just 'install_r')
6. This will install the R program

You're ready to validate Core Data files.

------
Usage:
------

1. Move an institution core data folder inside of 'TestCore' directory
2. Click 'button.bat' (may appear as just 'button' if you don't have showing file extension enabled on your computer)

-------
Output:
-------

The institution core data file will now contain a '`Reports' file inside which houses:

	- `valiData_report.txt`
	- `Cross_File_Comparisons_Report.txt`
	- `Org_Unit_Structure.txt`
	- `Email_Summary.txt`

The first one checks that each file meets the schema expectations from the CDD.  The second file ensures cross file expectations are met.  For example, it ensures that if a `CourseIdentifier` is found in the file 'Courses/Section/xxx.csv' then these elements must also be found in the parent 'Courses/Course/xxx.csv'.  The third file prints a tree structure for the org unit from the Courses directory if this file exists and has the proper headers.  The last file is an email prepared version of the errors from the first 2 reports.
