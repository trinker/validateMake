#version: 002

This app is a validator program for validating data inputs against a Campus Labs Core Data Dictionary (CDD) of expected file and variable types.


Usage:

1. Move an institution core data file inside of 'TestCore' directory
2. Click 'button.bat' (may appear as just 'button')


Output:

The institution core data file will now contain a '`Reports' file inside which houses:

- `valiData_report.txt`
- `Cross_File_Comparisons_Report.txt`

The first one checks that each file meets the schema expectations from the CDD.  The second file ensures cross file expectations are met.  For example, it ensures that if a `CourseIdentifier` is found in the file 'Courses/Section/xxx.csv' then these elements must also be found in the parent 'Courses/Course/xxx.csv'.
