# Getting Started

### Install Python
[Installation Documentation](https://www.python.org/downloads/)
```
brew install python
```

### Install Microsoft Functions toolkit
[Installation Documentation](https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet)
```
brew tap azure/functions
brew install azure-functions-core-tools@3
# if upgrading on a machine that has 2.x installed
brew link --overwrite azure-functions-core-tools@3
```



## Virtual Environment
We store the virtual environment locally while the project remains on SharePoint.  Storing the virtual environment locally has the advantage in that it will not be synced to SharePoint.

### Create Virtual Environment
From the DeleteMe1/Scripts/Python directory open a terminal in VSCode & run:

Windows:
```
# cd DeleteMe1/Scripts/Python   ## If this is not your working directory in VS Code
# python -m venv C:/Data_Science_Environments/DeleteMe1/env  # If not already made
C:\Data_Science_Environments\DeleteMe1\env\Scripts\activate.bat # using cmd terminal
# C:/Data_Science_Environments/DeleteMe1/env/Scripts/activate # powershell only
pip install -r requirements.txt
```

Mac:
```
# cd DeleteMe1/Scripts/Python   ## If this is not your working directory in VS Code
python3 -m venv ~/Data_Science_Environments/DeleteMe1/env
source ~/Data_Science_Environments/DeleteMe1/env/bin/activate
pip install -r requirements.txt
```


## Running Locally

### Select Python Interpreter
[Documentation](https://code.visualstudio.com/docs/python/environments)

In VSCode you can select the python interpreter associated with the virtual environment that was created
above. On a mac you can use (command + shift + p), or windows (ctrl + shirt + p) which will pop up an input
for VSCode commands. From there you can type in "Python: Select Interpreter", once selected it will give you
the option to select an interpreter to use for the project.  You should choose the one in the virtual environment.

### Windows Select Default Shell
[Documentation](https://stackoverflow.com/questions/44435697/vscode-change-default-terminal#:~:text=You%20can%20also%20select%20your,selecting%20Terminal%3A%20Select%20Default%20Shell.)

If you're on Windows there can be some trouble when activating the virtual environment depending on
the shell used.  It is recommended to move away from Powershell in favor of CMD.

## Script and Notebook Storage
Scripts and notebooks should be stored in the 'DeleteMe1/scripts/Python/src' folder.

### Start Notebook
```
# pip install --pre jupyterlab
jupyter-lab
```

