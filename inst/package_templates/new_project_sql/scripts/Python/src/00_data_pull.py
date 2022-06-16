##==============================================================================
## Dependencies & Setup
##==============================================================================
import pandas as pd
import numpy as np
import re, os, pickle, sys
from ds.connect import Config, ConnectDatabase
import ds.clean as cl
#import random
#import ipdb

## Get your credentials
cr = Config()

## Connect to the Database
idb = ConnectDatabase(cr.institutions)
idb.tables()

##==============================================================================
## Read In Data
##==============================================================================
raw_dat = idb.query('''
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
)

raw_dat


##==============================================================================
## Save Raw Data
##==============================================================================
raw_dat.to_pickle('../../data/raw/raw_dat.pickle')




