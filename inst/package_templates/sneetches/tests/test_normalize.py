#!/usr/bin/env python

import numpy as np
import pandas as pd
import pytest
from sneetches.normalize import NormCip, NormGrade, NormSex, NormRace
from pandas.testing import assert_frame_equal

@pytest.fixture
def sex_norm():
    return NormSex()


def test_normsex_defaults(sex_norm):
    # Test if the object has the correct `to_` methods
    assert all(
        [
            dir(sex_norm).__contains__(m)
            for m in ["to_" + c for c in sex_norm.map.columns[1:]]
        ]
    )

def test_normsex_uncommon_labels():
    s = NormSex()
    dat = ["man", "men", "women", "woman", "boy", "girl", "♂", 3, "", "-"]
    expected = [
        "Male",
        "Unknown",
        "Unknown",
        "Female",
        "Unknown",
        "Unknown",
        "Unknown",
        "Unknown",
        "Unknown",
        "Unknown",
    ]
    actual = s.normalize(dat).to_list()
    assert expected == actual


## NormCip
def test_normcip_results():
    s = NormCip()
    dat = pd.DataFrame(
        {"cip": ["27.0101", "270101", "27", "27.01", "27.", ".27", "2021-01-01", None]}
    )
    expected = [
        "27.0101",
        "27.0101",
        "27.0000",
        "27.0100",
        "27.0000",
        "Unknown",
        "Unknown",
        np.nan,
    ]
    actual = s.normalize(dat["cip"]).to_list()
    assert expected == actual

def test_normgrade_letter_result():
    g = NormGrade()
    df = pd.DataFrame(
        {'InstitutionId':[147,5649,147,147,5649,20,20,20,147,5649,20,147,20,5649,5649,5649,20,147,20,5649,147,147,
        147,147,147,147,147,5649,147,147,147,20,5649,147,20,147,147,20,5649,147,20,5649,5649,147,5649,147,147,147,
        147,147,5649,147,5649,5649,5649,5649,147],
        'Grade':['B+','WW','AF','D+','AU','A','W','D','W','US','DC','XF','E','B','I','P','CB','A','BA','A','A+',
        'B-','B','X','I','F','AU','W','D','D-','A-','I','N','IX','X','NS','NR','C','F','UN','B','S.','X','C+',
        'X.','WF','C','C-','SA','NC','S','SH','D','FALSE','WE','C','FW']
        }
    )
    expected_groups = ['89.0','WW','59.0','69.0','AU','100.0','W','69.0','W','US','73.0','XF','59.0','89.0','I','P',
    '83.0','96.0','93.0','100.0','100.0','82.0','86.0','X','I','59.0','AU','W','66.0','62.0','92.0','I','N','IX','X',
    'NS','NR','79.0','59.0','UN','89.0','S','X','79.0','X','WF','76.0','72.0','SA','NC','S','SH','69.0','FALSE','WE','79.0','FW']
    actual_groups = g.normalize(df['Grade'],df['InstitutionId']).to_list()
    assert expected_groups == actual_groups

    expected_one_institution = ['89.0','WW','59.0','69.0','AU','96.0','W','66.0','W','US','73.0','XF','59.0','86.0','I','P',
    '83.0','96.0','93.0','96.0','100.0','82.0','86.0','X','I','59.0','AU','W','66.0','62.0','92.0','I','N','IX','X',
    'NS','NR','76.0','59.0','UN','86.0','S','X','79.0','X','WF','76.0','72.0','SA','NC','S','SH','66.0','FALSE','WE','76.0','FW']
    actual_one_institution = g.normalize(df['Grade']).to_list()
    assert expected_one_institution == actual_one_institution

def test_normgrade_bad_format_result():
    g = NormGrade()
    df = pd.DataFrame({'Grade':[2.65,'C','I/N','B+','F','WF','A','CCC','F.',56.98,'9.2','C*','F','',np.nan,'Pass','Unsatisfactory',
    '9.8','39','39.2',1.53,'1.54','5.6',4.5,103,'104','2020-03-21','<p>23</p>',271,'Online','837','inclass','sdfjioihjawiwhjer','<p>Online</p>']})
    expected = [np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,
    np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,'time','html','>105','mode','>105','mode','long string','html']
    actual = g.map_to((g.normalize(df['Grade'])))['Bad_Format'].to_list()
    assert expected == actual

def test_normrace_result():
    r = NormRace()
    df = pd.DataFrame(
        {'Name':['not hispanic/latinx','native hawaiian pacific island','egyptian','oneidawi','np.nan','american indian/alaska native',
        'black (non-hispanic origin)','latino','notspecified','hmong','apple','238',184]
        }
    )
    expected_groups = ['not hispanic/latinx','hawaiian or pacific islander','egyptian','oneidawi','np.nan','american native','black',
        'latino','notspecified','hmong','apple','238','184']
    actual_groups = r.normalize(df['Name']).to_list()
    assert expected_groups == actual_groups

    expected_dataframe = pd.DataFrame(
        {'normed':['not hispanic/latinx','hawaiian or pacific islander','egyptian','oneidawi','np.nan','american native','black',
                    'latino','notspecified','hmong','apple','238','184'],
        'black':[False,False,False,False,False,False,True,False,False,False,False,False,False],
        'american_native':[False,False,False,False,False,True,False,False,False,False,False,False,False],
        'asian':[False,False,False,False,False,False,False,False,False,False,False,False,False],
        'hawaiian_pacific_islander':[False,True,False,False,False,False,False,False,False,False,False,False,False],
        'white':[False,False,False,False,False,False,False,False,False,False,False,False,False],
        'hispanic_latino':[False,False,False,False,False,False,False,True,False,False,False,False,False],
        'multiracial':[False,False,False,False,False,False,False,False,False,False,False,False,False],
        'unknown':[True,False,True,True,True,False,False,True,True,True,True,True,True],
        'nationality':[False,False,True,False,False,False,False,False,False,False,False,False,False],
        'minority':[False,True,False,False,False,True,True,True,False,False,False,False,False]
        }
    )
    actual_dataframe = r.map_to(r.normalize(df['Name']))
    assert_frame_equal(expected_dataframe, actual_dataframe, check_dtype=False)

