import pandas as pd
from collections import defaultdict
import numpy as np
import re
from pyperclip import copy
from sneetches.utils import camel_to_snake
import os
import warnings


class Normalize:
    """
    General Class of Normalizers

    Used to normalize unstandardized categories of data and convert between other common formats

    Normalizers:
        - cip
        - sex

    Examples:

    .. code-block:: python

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


################################################################################################


class NormSex:
    """
    Normalize & Convert Sex

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

    Examples:

    .. code-block:: python

        import pandas as pd
        from ds.clean import Normalize

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
        self.map = pd.DataFrame(
            {
                "normed": ["Male", "Female", "Unknown"],
                "label_strict": ["Male", "Female", None],
                "is_female": [0, 1, None],
                "sign": ["♂", "♀", "Unknown"],
            }
        ).convert_dtypes()

        ## This allows us to use the map and map_to tools to dynamically set the methods
        for i in self.map.columns[1:]:
            setattr(self, "to_" + i, self._make_map_fn(i))

    ## This method will be dependent upon the thing we're normalizing but returns a series
    def normalize(self, x):
        """
        Normalize inconsistently formatted sex categories into a common format

        Args:
            x: A pandas Series or list that has sex categories

        Returns:
            A pandas Series.
        """
        input = (
            pd.Series(x).fillna(value=np.nan).map(str, na_action="ignore").str.lower()
        )

        dict_sex = defaultdict(
            lambda: "Unknown",
            {
                "man": "Male",
                "woman": "Female",
                "m": "Male",
                "f": "Female",
                "male": "Male",
                "female": "Female",
                np.nan: np.nan,
            },
        )

        return input.map(dict_sex, na_action="ignore")

    ## generic mapping function
    def map_to(self, x, to: list = None):
        """
        Convert the normalized sex categories to other common formats

        Args:
            x: A pandas Series or list that has normalized sex categories (generated by the normalize() method)

        Returns:
            A pandas Series.
        """
        cols = self.map.columns[1:]

        if np.isscalar(to):
            to = list(to)

        if to is not None:
            to = [x for x in to if x != "normed"]

            if any([x not in cols for x in to]):
                raise Exception(
                    "The following are not available `to` formats: {}".format(
                        ", ".join(["'" + x + "'" for x in to if x not in cols])
                    )
                )

        if to is None:
            my_map = self.map
        else:

            my_map = self.map[["normed"] + to]

        return pd.merge(x.to_frame("normed"), my_map, how="left", on="normed")

    ## Function factor helper used to dynamically assign methods
    def _make_map_fn(self, cname):  # factory function
        def fn(x):  # result function
            return self.map_to(x=x, to=[cname]).iloc[:, 1]

        return fn
