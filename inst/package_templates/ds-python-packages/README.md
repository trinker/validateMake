# ds

## ds.connect

`ds.connect` is a collection of utilities to access various sources of data. It currently contains a `datalake` submodule focusing on retrieving data from the data lake.

## ds.clean

`ds.clean` is a collection of cleaning utilities. 
### Installation

### Create Virtual Environment
From the project root directory open a terminal in VSCode & run:

Windows:
```
# python -m venv ds\env  # If not already made
ds\env\Scripts\activate.bat        # using cmd terminal
pip install -r requirements.txt
```

Mac:
```
python3 -m venv ds/env  # If not already made
source ds/env/bin/activate
pip install -r requirements.txt
```

#### Installing 

You can install directly from the online repo: 

    pip install -e git+https://dev.azure.com/campuslabs/Data%20Science/_git/ds-python-packages

    ## OR

    git clone https://campuslabs@dev.azure.com/campuslabs/Data%20Science/_git/ds-python-packages
    cd ds-python-packages
    pip install -e .

#### Install Azure CLI

`ds.Connect` requires [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/) to access the data lake. Use the following command in PowerShell (Windows) or Terminal (MacOS) to check if you have Azure CLI installed:

    az -v

If you do not have Azure CLI installed, use the following command to install it:

Windows (PowerShell):

    $ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri https://aka.ms/installazurecliwindows -OutFile .\AzureCLI.msi; Start-Process msiexec.exe -Wait -ArgumentList '/I AzureCLI.msi /quiet'; rm .\AzureCLI.msi

MacOS:

    brew update && brew install azure-cli

After installed, run `az -v` to check if the installation was successful.

### Access to data lake

```python

from ds.connect import ConnectDatalake, Config

# You'll be prompted to enter your password
crds = Config()

dl = ConnectDatalake(crds.insight_lake)

# return all institution ids in the datalake as a list
dl.list_inst()
dl.list_inst(exclude_fakes=True)

# return all institutions owning a specified product
# The first time you run dl.who_has takes about 45 seconds as of March, 2022
dl.who_has("beacon")
dl.who_has("cei", exclude_fakes=True)
dl.who_has("cei", exclude_fakes=False)

# get products for specified institutions
dl.get_inst_prods(894)
dl.get_inst_prods([894, 6404])

# get all products for all institutions
dl.get_inst_prods(dl.list_inst())

# return info about all individual files in an institution's product folder
dl.list_inst_product_files(894, "beacon")

# return column names for a csv file as a list
dl.list_file_header("Institution/894/Beacon/CustomAttributes.csv")
dl.tree("Institution/894/")
dl.get('Institution/104/Beacon/bcnRetentionStatus/2021/12.csv')

```
### Access to SQL database

```python

from ds.connect import ConnectDatabase, Config
import pandas as pd

crds = Config()
bdb = ConnectDatabase(crds.beacon)
bdb.check()
bdb.tables()
bdb.get('StudentFile', n=100)
bdb.search('student')
bdb.count('StudentFile', 'AudienceType')
bdb.as_sql_list(['d', 'don\'t do it'])

pdb = ConnectDatabase(crds.publicdata)
pdb._has_permission('DROP TABLE')
pdb.fake_institutions()
pdb.database()

iris = pd.read_csv('https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv')
pdb.write_table(iris, 'DeleteMeIris', append = False)
pdb.tables()
pdb.get('DeleteMeIris')
pdb.delete_table('DeleteMeIris')

idb = ConnectDatabase(crds.institutions)

idb.tables()
idb.get('Institution', n = 10).columns

my_query = '''
SELECT
    i.[Id],
    i.[IpedsId],
    i.[Name],
    i.[Address],
    i.[City],
    i.[State]
FROM [dbo].[Institution] as i WITH (NOLOCK)
WHERE Deleted = 0 AND
Id IN {fakes}
'''.format(fakes=idb.fake_institutions())
print(my_query)
fakes = idb.query(my_query)
```