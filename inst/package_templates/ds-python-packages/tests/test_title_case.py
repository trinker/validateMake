#!/usr/bin/env python

import pytest
import pandas as pd

from ds.clean.title_case import title_case



def test_title_case_results():
    x = ["I see to see him go After him", 'the farmer and the dell']
    expected = ['I See to See Him Go After Him', 'The Farmer and the Dell'] 
    actual = title_case(x).to_list()
    assert expected == actual
