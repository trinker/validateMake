import pandas as pd
from collections import defaultdict
import numpy as np
import re
from pyperclip import copy
from sneetches.utils import camel_to_snake
import os
import warnings

## Instructions to add normalize classes:
## 
##   1. Import template function:
## 
##      from ds.clean.normalize import _norm_cls_template
## 
##   2. Supply the name for the normalizer and optionally copy the result to the clipboard:
## 
##      _norm_cls_template('{NORMALIZER NAME}', copy_to_clip = True)
## 
##   3. Paste these results to normalize.py and then find the 3 places with {{ADD_HERE}} 
##      (your `map`, `normalize` function guts, and Examples in the doc string) and replace 
##      with your functionality
##       
##      a. `self.normalize` method with `x` input (usually not other arguments)
##      b. `self.map` is an attribute DataFrame with first column named 'normed' 
##         matching (key value pairs) output from `normalize` method.  These columns
##         names should be in snake case (lower case and underscore connected) and 
##         easily understood
##         
##   4. Then add your class to `Normalize` class as self.{xxx} = Norm{Xxx}()




## One class to suck up all the normalizers
class Normalize:
    """General Class of Normalizers
    
    Used to normalize unstandardized categories of data and convert between other common formats

    Normalizers:
        - cip    
        - sex

    Examples::

        import pandas as pd
        from sneetches import Normalize

        ## the data set
        dat = pd.DataFrame({'sex': ['m', 0, 1, 'female', 'F', 'Male', 'male', None, 'prefer not to say']})
        dat

        ## Initialize the normalizer
        nm = Normalize()

        ## Normalize
        dat['sex_normed'] = nm.sex.normalize(dat['sex'])
        dat

        ## Mapping to other formats using map_to() method (returns DataFrame)
        nm.sex.map_to(dat['sex_normed'])  # Returns all
        nm.sex.map_to(dat['sex_normed'], ['integer'])
        nm.sex.map_to(dat['sex_normed'], ['label_strict', 'sign'])

        ## Mapping to other formats using to_XXX() methods (returns a Series)
        nm.sex.to_integer(dat['sex_normed'])
        nm.sex.to_sign(dat['sex_normed'])
    """
    def __init__(self):  
        self.sex = NormSex()
        self.race = NormRace()


################################################################################################

class NormSex:
    """Normalize & Convert Sex

    A class that provides methods to (1) normalize sex data into a consistant form and (2) convert between formats.  Workflow is to:
        1. Use the `normalize() method to get the data consistent
        2. Use the to_XXX() and/or map_to() methods on the normalized data (the result from step one) to convert to other formats

    Attributes:
        map: A mapping between various sex formats

    Methods:
        normalize: Returns a pandas Series.  This is a method to take inconsistently formatted sex categories and normalize it to a common format.
        map_to: Returns a pandas DataFrame.  This is a method to convert the normalized sex categories to other common formats. This is 
                usefull if you want several formats as new columns over the to_XXX() methods.
        to_XXX: Returns a pandas Series.  There are a number of methods that convert a normalized data source into other formats (formats indicated 
                by _XXX).  Use `dir()` on the instance or class to see these methods.

    Examples::

        import pandas as pd
        from sneetches import Normalize

        ## the data set
        dat = pd.DataFrame({'sex': ['m', 0, 1, 'female', 'F', 'Male', 'male', None, 'prefer not to say']})
        dat

        ## Initialize the normalizer
        nm = Normalize()

        ## Normalize
        dat['sex_normed'] = nm.sex.normalize(dat['sex'])
        dat

        ## Mapping to other formats using map_to() method (returns DataFrame)
        nm.sex.map_to(dat['sex_normed'])  # Returns all
        nm.sex.map_to(dat['sex_normed'], ['integer'])
        nm.sex.map_to(dat['sex_normed'], ['label_strict', 'sign'])

        ## Mapping to other formats using to_XXX() methods (returns a Series)
        nm.sex.to_integer(dat['sex_normed'])
        nm.sex.to_sign(dat['sex_normed'])
    """
    def __init__(self):  

        ## This map will be dependent upon the thing we're normalizing but is a 
        ## DataFrame with the first column called 'normed' and the other columns to 
        ## be the other types you want to convert to
        self.map = pd.DataFrame({
            'normed': ['Male', 'Female', 'Unknown'], 
            'label_strict': ['Male', 'Female', None], 
            'is_female': [0, 1, None],
            'sign': ['♂', '♀', 'Unknown']
        }).convert_dtypes()

        ## This allows us to use the map and map_to tools to dynamically set the methods
        for i in self.map.columns[1:]:
            setattr(self, 'to_' + i, self._make_map_fn(i))

    ## This method will be dependent upon the thing we're normalizing but returns a series
    def normalize(self, x):
        """Normalize inconsistently formatted sex categories into a common format
        
        Args:
            x: A pandas Series or list that has sex categories

        Returns:
            A pandas Series.  
        """
        input = pd.Series(x).fillna(value=np.nan).map(str, na_action = 'ignore').str.lower()
        
        dict_sex = defaultdict(
            lambda: 'Unknown',
            {"man": 'Male', 'woman': 'Female', "m": 'Male', 'f': 'Female', "male": 'Male', 'female': 'Female', np.nan: np.nan}
        )

        return input.map(dict_sex, na_action = 'ignore')   
        
    ## generic mapping function
    def map_to(self, x, to:list= None):
        """Convert the normalized sex categories to other common formats
        
        Args:
            x: A pandas Series or list that has normalized sex categories (generated by the normalize() method)

        Returns:
            A pandas Series.  
        """
        cols = self.map.columns[1:]

        if np.isscalar(to):
            to = list(to)
        
        if to is not None:
            to = [x for x in to if x != 'normed']

            if any([x not in cols for x in to]):
                raise Exception('The following are not available `to` formats: {}'.format(', '.join(["'" + x + "'" for x in to if x not in cols])))

        if to is None:
            my_map = self.map
        else:

            my_map = self.map[['normed'] + to]

        return pd.merge(x.to_frame('normed'), my_map, how = 'left', on='normed')

    ## Function factor helper used to dynamically assign methods
    def _make_map_fn(self, cname): # factory function
        def fn(x): # result function
            return self.map_to(x = x, to = [cname]).iloc[:,1]
        return fn






class NormRace:
    """Normalize & Convert Race

    A class that provides methods to (1) normalize race data into a consistant form and (2) convert between formats.  Workflow is to:
        1. Use the `normalize() method to get the data consistent
        2. Use the to_XXX() and/or map_to() methods on the normalized data (the result from step one) to convert to other formats

    Attributes:
        map: A mapping between various race formats

    Methods:
        normalize: Returns a pandas Series.  This is a method to take inconsistently formatted race categories and normalize it to a common format.
        map_to: Returns a pandas DataFrame.  This is a method to convert the normalized race categories to other common formats. This is 
                usefull if you want several formats as new columns over the to_XXX() methods.
        to_XXX: Returns a pandas Series.  There are a number of methods that convert a normalized data source into other formats (formats indicated 
                by _XXX).  Use `dir()` on the instance or class to see these methods.

    Examples::
{{<--DELETE THIS LINE-->}}{{ADD_HERE}} {{Feel free to use the current Examples section as a template and replace as needed and delete this emssage}}
        import pandas as pd
        from ds.clean import Normalize

        ## the data set
        dat = pd.DataFrame({'race': ['american indian/alaskan native', 'asian american', 'foreign', 'hp', 'multiracial', 'west indian', 'hispanic american'
                , None, 'prefer not to say']})
        dat

        ## Initialize the normalizer
        nm = Normalize()

        ## Normalize
        dat['race_normed'] = nm.race.normalize(dat['race'])
        dat

        ## Mapping to other formats using map_to() method (returns DataFrame)
        nm.race.map_to(dat['race_normed'])  # Returns all
        nm.race.map_to(dat['race_normed'], ['asian'])
        nm.race.map_to(dat['race_normed'], ['american_native', 'white','multiracial])

        ## Mapping to other formats using to_XXX() methods (returns a Series)
        nm.race.to_multiracial(dat['race_normed'])
        nm.race.to_asian(dat['race_normed'])
    """
    def __init__(self):  

        ## This map will be dependent upon the thing we're normalizing but is a 
        ## DataFrame with the first column called 'normed' and the other columns to 
        ## be the other types you want to convert to
        this_dir, this_filename = os.path.split(__file__)        
        RACE_DATA_PATH = os.path.join(this_dir, "data", "race.csv")
        self.map = pd.read_csv(RACE_DATA_PATH, usecols=['normed','black','american_native','asian','hawaiian_pacific_islander','white','hispanic_latino','multiracial','unknown','bad_format','minority']).convert_dtypes()
        # self.map = pd.read_csv('./data/race.csv', usecols=['normed','black','american_native','asian','hawaiian_pacific_islander','white','hispanic_latino','multiracial','unknown','bad_format']).convert_dtypes()
        self.map.columns = self.map.columns.str.lower()
        self.map['normed'] = self.map['normed'].str.lower()

        ## This allows us to use the map and map_to tools to dynamically set the methods
        for i in self.map.columns[1:]:
            setattr(self, 'to_' + i, self._make_map_fn(i))

    ## This method will be dependent upon the thing we're normalizing but returns a series
    def normalize(self, x):
        """Normalize inconsistently formatted race categories into a common format

        Args:
            x: A pandas Series or list that has race categories

        Returns:
            A pandas Series.  
        """
        # race cleaning if not able to clean, return original value
        x = x.astype(str)
        x = x.str.lower()
        dict_race = MyDict({
            'as':'asian',
            'pi':'pacific islander',
            'hs':'hispanic',
            'un':'unknown',
            'am':'native american',
            'bl':'black',
            'mu':'multiracial',
            'wh':'white',
            'amind':'native american',
            'an':'native american',
            'pi':'pacific islander',
            'pacif':'pacific islander',
            'american indian':'american native',
            'africanamerican':'african american',
            'na':'unknown',
            'n a':'unknown',
            'n/a':'unknown',
            'am. ind':'native american'
        })
        
        x = x.str.replace('\(\)|-|^z|non-hispanic origin|non-hispanic|non hispanic|race\d|rac\d','',regex=True).str.strip()
        x = x.map(dict_race, na_action = 'ignore')

        black_index = x[x.str.contains('african|bl') & ~x.str.contains('north') == True].index
        american_native_index = x[x.str.contains('alaska|american.*indian|native.*american|west.*indian|american.*native') == True].index
        asian_index = x[x.str.contains('asia') & ~x.str.contains('cau') | x.str.match('indian') == True].index
        hawaiian_pacific_islander_index = x[x.str.contains('hawai|paci|islander') == True].index
        white_index = x[x.str.contains('white|cau|middle|north') == True].index
        # hispanic_index = x[x.str.contains('his|lat|hs|hp')& ~x.str.contains('non|not') == True].index
        multiracial_index_1 = x[x.str.contains('multi|more|two|^2') == True].index

        all_race = black_index.append([american_native_index,asian_index,hawaiian_pacific_islander_index,white_index])
        multiracial_index_2 = all_race[all_race.duplicated()]
        multiracial_index = multiracial_index_1.append(multiracial_index_2)

        black_index = [x for x in black_index if x not in multiracial_index]
        american_native_index = [x for x in american_native_index if x not in multiracial_index]
        asian_index = [x for x in asian_index if x not in multiracial_index]
        hawaiian_pacific_islander_index = [x for x in hawaiian_pacific_islander_index if x not in multiracial_index]
        white_index = [x for x in white_index if x not in multiracial_index]

        x.loc[black_index] = 'black'
        x.loc[american_native_index] = 'american native'
        x.loc[asian_index] = 'asian'
        x.loc[hawaiian_pacific_islander_index] = 'hawaiian or pacific islander'
        x.loc[white_index] = 'white'
        x.loc[x[x.str.contains('unknown')].index] = 'unknown'

        return x

    ## generic mapping function
    def map_to(self, x, to:list= None):
        """Convert the normalized race categories to other common formats

        Args:
            x: A pandas Series or list that has normalized race categories (generated by the normalize() method)

        Returns:
            A pandas Series.  
        """
        cols = self.map.columns[1:]

        if np.isscalar(to):
            to = list(to)

        if to is not None:
            to = [x for x in to if x != 'normed']

            if any([x not in cols for x in to]):
                raise Exception('The following are not available `to` formats: {}'.format(', '.join(["'" + x + "'" for x in to if x not in cols])))

        my_map = self.map
        # Map input field to corresponding race label
        ls_race = ['black','american_native','asian','hawaiian_pacific_islander','white']
        ls_minority = ['black','american_native','asian','hawaiian_pacific_islander','multiracial','hispanic_latino']

        df_combined = pd.merge(x.to_frame('normed'), my_map, how = 'left', on='normed')        

        df_combined.loc[df_combined[(~df_combined[ls_race].any(axis=1)) | (df_combined[ls_race].isnull().sum(axis=1) >= 5)].index,'unknown'] = True

        # additional parsing when input fields cannot be normalized
        hispanic_index = x[x.str.contains('his|lat|hs|hp')& ~x.str.contains('non|not') == True].index
        df_combined.loc[hispanic_index, 'hispanic_latino'] = True

        black_index = x[x.str.contains('african|bl') & ~x.str.contains('north') == True].index
        american_native_index = x[x.str.contains('alaska|american.*indian|native.*american|west.*indian|american.*native') == True].index
        asian_index = x[x.str.contains('asia') & ~x.str.contains('cau') | x.str.match('indian') == True].index
        hawaiian_pacific_islander_index = x[x.str.contains('hawai|paci|islander') == True].index
        white_index = x[x.str.contains('white|cau|middle|north') == True].index
        df_combined.loc[black_index, 'black'] = True
        df_combined.loc[american_native_index, 'american_native'] = True
        df_combined.loc[asian_index, 'asian'] = True
        df_combined.loc[hawaiian_pacific_islander_index, 'hawaiian_pacific_islander'] = True
        df_combined.loc[white_index, 'white'] = True

        multiracial_index_1 = x[x.str.contains('multi|more|two|^2') == True].index
        all_race = black_index.append([american_native_index,asian_index,hawaiian_pacific_islander_index,white_index])
        multiracial_index_2 = all_race[all_race.duplicated()]
        multiracial_index = multiracial_index_1.append(multiracial_index_2)
        df_combined.loc[multiracial_index, 'multiracial'] = True

        minority_index = df_combined[df_combined[ls_minority].sum(axis=1) > 0].index
        df_combined.loc[minority_index, 'minority'] = True

        # if above parsing overwrite table mapping, and situation not all race are na and more than one race is true or false
        # it will fill the remaining race columns as false
        ind = df_combined[df_combined[ls_race].isna().sum(axis=1)<5].index
        df_combined.loc[ind,ls_race] = df_combined.loc[ind,ls_race].replace(np.nan,False)

        # combine one hot encoding columns into race columns, this will only grab first true value.
        df_combined = df_combined.assign(
            race=lambda x: x[ls_race].idxmax(1)
        )
        # assign multiracial when more than one label in race columns
        df_combined.loc[df_combined[df_combined['multiracial'] == True].index,'race'] = 'multiracial'

        if to is None:
            return df_combined
        else:
            return df_combined[['normed'] + to]

    ## Function factor helper used to dynamically assign methods
    def _make_map_fn(self, cname): # factory function
        def fn(x): # result function
            return self.map_to(x = x, to = [cname]).iloc[:,1]
        return fn






######################################################################################
## Do Not Add New Normalizer Classes Below This Point
######################################################################################


################################################################################################
## Function to generate new normalizer classes
def _norm_cls_template(category:str, copy_to_clip:bool = False):

    lower_cat = category.lower()  
    upper_cat = lower_cat.title()   

    out = re.sub('\{upper_cat\}', upper_cat, norm_cls_template)
    out = re.sub('\{lower_cat\}', lower_cat, out)
    out = re.sub('\{trip_quote\}', '"""', out)

    if copy_to_clip:
        copy(out)
        print(out)
        print('\n\nPaste to normalize.py and then find the 3 places with {{ADD_HERE}} (your `map`, `normalize`\nfunction guts, and Examples in the doc string) and replace with your functionality')
    else:
        return out


norm_cls_template = """
################################################################################################\n\n
class Norm{upper_cat}:
    {trip_quote}Normalize & Convert {upper_cat}
\n    A class that provides methods to (1) normalize {lower_cat} data into a consistant form and (2) convert between formats.  Workflow is to:
        1. Use the `normalize() method to get the data consistent
        2. Use the to_XXX() and/or map_to() methods on the normalized data (the result from step one) to convert to other formats
\n    Attributes:
        map: A mapping between various {lower_cat} formats
\n    Methods:
        normalize: Returns a pandas Series.  This is a method to take inconsistently formatted {lower_cat} categories and normalize it to a common format.
        map_to: Returns a pandas DataFrame.  This is a method to convert the normalized {lower_cat} categories to other common formats. This is 
                usefull if you want several formats as new columns over the to_XXX() methods.
        to_XXX: Returns a pandas Series.  There are a number of methods that convert a normalized data source into other formats (formats indicated 
                by _XXX).  Use `dir()` on the instance or class to see these methods.
\n    Examples:\n{{<--DELETE THIS LINE-->}}{{ADD_HERE}} {{Feel free to use the current Examples section as a template and replace as needed and delete this emssage}}
        import pandas as pd
        from ds.clean import Normalize
\n        ## the data set
        dat = pd.DataFrame({'sex': ['m', 0, 1, 'female', 'F', 'Male', 'male', None, 'prefer not to say']})
        dat
\n        ## Initialize the normalizer
        nm = Normalize()
\n        ## Normalize
        dat['sex_normed'] = nm.sex.normalize(dat['sex'])
        dat
\n        ## Mapping to other formats using map_to() method (returns DataFrame)
        nm.sex.map_to(dat['sex_normed'])  # Returns all
        nm.sex.map_to(dat['sex_normed'], ['integer'])
        nm.sex.map_to(dat['sex_normed'], ['label_strict', 'sign'])
\n        ## Mapping to other formats using to_XXX() methods (returns a Series)
        nm.sex.to_integer(dat['sex_normed'])
        nm.sex.to_sign(dat['sex_normed'])
    {trip_quote}
    def __init__(self):  
\n        ## This map will be dependent upon the thing we're normalizing but is a 
        ## DataFrame with the first column called 'normed' and the other columns to 
        ## be the other types you want to convert to
        self.map = pd.DataFrame({
            'normed': [], 
            {{ADD_HERE}} 
        }).convert_dtypes()
\n        ## This allows us to use the map and map_to tools to dynamically set the methods
        for i in self.map.columns[1:]:
            setattr(self, 'to_' + i, self._make_map_fn(i))
\n    ## This method will be dependent upon the thing we're normalizing but returns a series
    def normalize(self, x):
        {trip_quote}Normalize inconsistently formatted {lower_cat} categories into a common format
\n        Args:
            x: A pandas Series or list that has {lower_cat} categories
\n        Returns:
            A pandas Series.  
        {trip_quote}
\n        {{ADD_HERE}} 
\n    ## generic mapping function
    def map_to(self, x, to:list= None):
        {trip_quote}Convert the normalized {lower_cat} categories to other common formats
\n        Args:
            x: A pandas Series or list that has normalized {lower_cat} categories (generated by the normalize() method)
\n        Returns:
            A pandas Series.  
        {trip_quote}
        cols = self.map.columns[1:]
\n        if np.isscalar(to):
            to = list(to)
\n        if to is not None:
            to = [x for x in to if x != 'normed']
\n            if any([x not in cols for x in to]):
                raise Exception('The following are not available `to` formats: {}'.format(', '.join(["'" + x + "'" for x in to if x not in cols])))
\n        if to is None:
            my_map = self.map
        else:
\n            my_map = self.map[['normed'] + to]
\n        return pd.merge(x.to_frame('normed'), my_map, how = 'left', on='normed')
\n    ## Function factor helper used to dynamically assign methods
    def _make_map_fn(self, cname): # factory function
        def fn(x): # result function
            return self.map_to(x = x, to = [cname]).iloc[:,1]
        return fn
"""






