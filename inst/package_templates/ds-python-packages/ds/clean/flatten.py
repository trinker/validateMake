from itertools import chain
import pandas as pd
import numpy as np


def unnest(dict, nms: list = ["key", "values"], drop: bool = False):
    """Dictionary of Lists to 2 Column Dataframe

    Convert a dictionary of different length lists to a 2 column dataframe;
    analogous to the pandas `explode` method.

    Parameters:
        dict: A dictionary of lists
        nms: A list of length 2 naming the first keys column and the second values column

    Examples::

        from ds.clean import flatten, unnest
        import pandas as pd
        import numpy as np

        dict_c = {'a': [1, 2, 3], 'b': [3, 5], 'c': 1, 'd': None}
        unnest(dict_c)

        ## Now flatten it
        new = unnest(dict_c)
        new['values'] = new['values'].map(lambda x: [x])

        (
            new.groupby('key').
                agg(new = ('values', lambda x: flatten(x, unique = True, sort = True))).
                reset_index(inplace = False)
        )

        ## Flatten Data Frame
        ## Make some nested data
        dat = pd.DataFrame({
            'a': ['0', '0', '0', '1', '1', '2', '3', '3', '4'],
            'b': [[1, 2], None, [1], None, None, [1, 2, 3], [4, 5], [3], [5]]
        })

        ## Flatten it
        flat = (
            dat.groupby('a').
                agg(b = ('b', lambda x: flatten(x, unique = True, sort = True))).
                reset_index(inplace = False)
        )

        flat
        flat.explode('b')


        ## Dictionary it
        my_dict = dict(zip(flat.a, flat.b))
        ## Stretch to 2 column dataframe
        unnest(my_dict)


        df = pd.DataFrame({'A': ['w', 'x', 'y', 'z'],'B': [[2, 3, 4], [1, 2], [], np.nan]})
        unnest(dict(zip(df.A, df.B)))
        unnest(dict(zip(df.A, df.B)), drop = True)
        df.explode('B')

        new2 = df.explode('B')
        new2.B = new2.B.map(lambda x: [x])

        (
            new2.groupby('A').
                agg(B = ('B', lambda x: flatten(x, unique = True, sort = True))).
                reset_index(inplace = False)
        )
    """
    empt = [] if drop else [None]
    dict = {
        k: v
        if (isinstance(v, list) and (len(v) != 0))
        else empt
        if (isinstance(v, list) and (len(v) == 0))
        else [v]
        for k, v in dict.items()
    }
    return pd.DataFrame.from_dict(
        {
            nms[0]: list(chain(*[[k] * len(v) for k, v in dict.items()])),
            nms[1]: list(chain(*dict.values())),
        }
    ).convert_dtypes()
    # return pd.DataFrame(my_dict.items(), columns = nms).explode(nms[1])


## Function to Flatten Lists
def flatten(dataframe, unique: bool = False, sort: bool = False):
    """Flatten a DataFrame with a List Column

    Parameters:
        dataframe: A pandas DataFrame with a list column
        unique: Should duplicate values be dropped?
        sort: Should the values within the lists be sorted?

    Examples::

        from ds.clean import flatten, unnest
        import pandas as pd
        import numpy as np

        dict_c = {'a': [1, 2, 3], 'b': [3, 5], 'c': 1, 'd': None}
        unnest(dict_c)

        ## Now flatten it
        new = unnest(dict_c)
        new['values'] = new['values'].map(lambda x: [x])

        (
            new.groupby('key').
                agg(new = ('values', lambda x: flatten(x, unique = True, sort = True))).
                reset_index(inplace = False)
        )

        ## Flatten Data Frame
        ## Make some nested data
        dat = pd.DataFrame({
            'a': ['0', '0', '0', '1', '1', '2', '3', '3', '4'],
            'b': [[1, 2], None, [1], None, None, [1, 2, 3], [4, 5], [3], [5]]
        })

        ## Flatten it
        flat = (
            dat.groupby('a').
                agg(b = ('b', lambda x: flatten(x, unique = True, sort = True))).
                reset_index(inplace = False)
        )

        flat
        flat.explode('b')


        ## Dictionary it
        my_dict = dict(zip(flat.a, flat.b))
        ## Stretch to 2 column dataframe
        unnest(my_dict)


        df = pd.DataFrame({'A': ['w', 'x', 'y', 'z'],'B': [[2, 3, 4], [1, 2], [], np.nan]})
        unnest(dict(zip(df.A, df.B)))
        unnest(dict(zip(df.A, df.B)), drop = True)
        df.explode('B')

        new2 = df.explode('B')
        new2.B = new2.B.map(lambda x: [x])

        (
            new2.groupby('A').
                agg(B = ('B', lambda x: flatten(x, unique = True, sort = True))).
                reset_index(inplace = False)
        )
    """
    m = [i for i in dataframe if i]
    m = sum(m, [])

    if len(m) == 0:
        m = None
    else:
        if unique:
            m = list(dict.fromkeys(m))

        if sort:
            m = sorted(m)

    return m
