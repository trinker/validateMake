This README provides an overview of the directories and folders located in this project and their usage.  

The user begins by creating a new project via `cl::new_project`.  A .sql or .csv flavored version can be specified through the `type` argument.  This generates a template for a data science analysis that contains:

|   README.txt
|   project.Rproj
|   
+---data
+---deliverables
+---output
+---plots
+---project_info
|       01_project_overview.txt
|       02_workflow_diagram.pptx
|       generic-data-science-workflow.png
|       workflow_diagram_example.pdf
|       
+---reports
|   |   data_description_report.Rmd
|   |   
|   \---figures
+---scripts
|   |   01_cleaning.R
|   |   02_exploration.R
|   |   03_analysis.R
|   |   project_functions.R
|   |   
|   \---sql
\---supporting_docs 


This project directory attempts to follow Hadley Wickham's description of a data scientist's workflow as summarized in the visual: project_info/generic-data-science-workflow.png'.  The next section will outline the usage of the directories and files in the project directory.

======
Usage:
======
1. The 'project_info' directory contains the meta information about the project.  This is where the information about the project, the research questions, and the general workflow are housed.  This info should be well maintained as it allows other researchers to understand the project and take over/extend as necessary.
  
    A. Fill in the information in the 'project_info/01_project_overview.txt'.  This tells readers what the project is about, things like category, product, stakeholders, research questions, deliverables, due dates (for more detail on project category see https://tinyurl.com/cl-ds-project-categories). As you learn things about the project (including the data base structure) add this info to the `Notes` field.  This file is legitimate YAML and should be maintained as such.  Only use colons as actual field separators.  

    B. The 'project_info/02_workflow_diagram.pptx' is a tool for mapping out the workflow of the project. What scripts control what data and in what sequence.  The user may use the .pptx template or   hand draw the workflow, take a pic and upload it as 'project_info/workflow_diagram.xxx' (where xxx is the pic file extension).  

2.  The xxx.rproj (where xxx is the project name) file opens the project in R studio in the root directory.  This is the preferred method of opening a project in R.

3. The 'data' folder houses the project data.  Sub-directories can be added to aid in understanding the data types (for example, adding a 'cleaned' sub-directory for housing cleaned data).  Make sure to document input and output data in the 'project_info/workflow_diagram' file.

4. The supporting docs directory is meant to be a place to house artifacts related to the project.  These may be articles, screen captures, .docx templates, etc.  

5. The 'scripts' folder contains R and SQL scripting files.  Semantic number prefixes (i.e., `##_`) should be used to indicate ordering of script use.  Make sure to document script usage in the 'project_info/workflow_diagram' file.

    A. The 'scripts/sql' directory is used to store .sql scripts that pull data for the project.

    B. The 'scripts' directory also houses .R scripts that are number prefixed.  The user may add additional scripts maintaining number prefixing [01 = cleaning data; 02 = exploration; 03 = analysis].  Lower case letters may be added to this prefixing to maintain order (i.e., `##a_`, `##b_`).  This script convention is meant to be a guide that allows for generalizability, not as handcuffs.  Tweak for the requirements of your particular project as necessary.  Note that the 'scripts/project_functions.R' file can be used to store project based functions that are utilized across the project.  Storing these in a centralized file allows for easy sourcing and possible conversion to a stand alone package.

6. As the user explores and analyzes the data they often want to create plots, output, and deliverables.  

    A. The 'plots' folder is meant to store plots that can easily be accessed for later reference.  Semantic numbering and naming that indicates the type of plot and content of the plot are useful for organizing this directory.

    B. The 'output' folder is a place to store small output data sets, text output, or other output related to the project.  For example one may output the cluster frequent terms from a document clustering analysis so that a human might provide topics for the unsupervised clusters.  This directory, like 'plots', is meant to store ancillary output.

    C. The 'deliverables' directory is where project deliverables are stored (unless the deliverable is a report/slide deck, in which case it is located in the 'reports' directory).  Finished data sets, visualizations, shiny apps, etc. are stored in this folder and are the end product of the analysis.

7. The 'reports' folder houses reports and slide decks.  The user is encouraged to utilize R's .Rmd files for generating reports and decks in that they make the research more reproducible and are easily updated.  This folder contains a generic 'reports/data_description_report.Rmd' file that can be used to overview the data.  It is meant to be a guide but may not pertain to the work at hand.  

Reports should contain a description of the research question(s)/business problem(s), the data generation process, descriptive statistics (e.g., n, mean, sd, correlations, etc.), and information about missing data.  The report should answer the research question(s)/business problem(s) in separate headings.  Data quality and limitations, future work, and implications/potential use should be discussed at the end of the report.

For longer reports it is advised that the report be summarized into a 2-4 page executive summary or small slide deck.



------------------
Altering Structure
------------------
This template is meant to provide a framework for data science projects.  It should be followed closely as it allows team members to quickly understand what is happening in a project.  At times, the framework may be too constraining or may not be useful.  Adjust and alter as needed for specific projects in the least disruptive way possible.

Example directories that are commonly added include 'models' (for saving predictive models or saving regular expression categorization models).