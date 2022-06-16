#!/usr/bin/env python

import pytest
import pandas as pd
import numpy as np

from ds.clean.flatten import unnest, flatten


def test_flatten_results():
    dat = pd.DataFrame({
        'a': ['0', '0', '0', '1', '1', '2', '3', '3', '4'],
        'b': [[1, 2], None, [1], None, None, [1, 2, 3], [4, 5], [3], [5]]  
    })

    ## Flatten it
    flat_explode_unique_sorted = ( 
        dat.groupby('a').
            agg(b = ('b', lambda x: flatten(x, unique = True, sort = True))).
            explode('b').
            reset_index(inplace = False)
    )

    flat_explode_duped_sorted = ( 
        dat.groupby('a').
            agg(b = ('b', lambda x: flatten(x, unique = False, sort = True))).
            explode('b').
            reset_index(inplace = False)
    )

    flat_explode_duped_unsorted = ( 
        dat.groupby('a').
            agg(b = ('b', lambda x: flatten(x, unique = False, sort = False))).
            explode('b').
            reset_index(inplace = False)
    )

    assert pd.Series([1, 2, None, 1, 2, 3, 3, 4, 5, 5], name = 'b').equals( 
        flat_explode_unique_sorted.b.astype(float)
    )

    assert pd.Series([1, 1, 2, None, 1, 2, 3, 3, 4, 5, 5], name = 'b').equals( 
        flat_explode_duped_sorted.b.astype(float)
    )

    assert pd.Series([1, 2, 1, None, 1, 2, 3, 4, 5, 3, 5], name = 'b').equals( 
        flat_explode_duped_unsorted.b.astype(float)
    )    

def test_unnest_results():
    dict_c = {'a': [1, 2, 3], 'b': [3, 5], 'c': 1, 'd': None}
    expected = {'k': ['a', 'a', 'a', 'b', 'b', 'c', 'd'], 'v': [1, 2, 3, 3, 5, 1, np.nan]}
    actual = unnest(dict_c)

    assert pd.Series(expected['v'], name = 'values').convert_dtypes().equals(actual['values'])
    assert pd.Series(expected['k'], name = 'key').convert_dtypes().equals(actual['key'])