def func(x):
    return x + 1


def test_answer():
    assert func(3) == 5

import pytest
import pandas as pd

from ds.clean.normalize import NormSex   

def test_normsex_defaults():
    s = NormSex()
    cols = ['normed', 'label_strict', 'is_female', 'sign']
    assert set(s.map.columns) == set(cols)
    # Test if the object has the correct `to_` methods
    assert all([dir(s).__contains__(t) for t in ['to_' + c for c in cols[1:]]])
    
