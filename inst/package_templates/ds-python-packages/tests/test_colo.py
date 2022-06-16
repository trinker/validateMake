#!/usr/bin/env python

import pytest


from ds.text.colo import colo


def test_colo_results():
    actual = [
        colo('cat', 'dog', 'fish'),
        colo('cat', 'dog', 'fish', fail = 'I Wish'),
        colo('cat', 'fish'),
        colo('cat', 'fish', fail = None),
        colo('cat', 'fish', fail = 'I Wish'),
        colo('cat'),
        colo('cat', fail = 'I Wish'),
        colo('cat\\b', 'fish(\\b|es)')
    ]
    expected = [
        '^(?=.*cat)(?=.*dog)(?=.*fish)', 
        '^(?!.*(I Wish))(?=.*(cat))(?=.*(dog))(?=.*(fish))', 
        '((cat.*fish)|(fish.*cat))', 
        '((cat.*fish)|(fish.*cat))', 
        '^(?!.*(I Wish))(?=.*(cat))(?=.*(fish))', 
        'cat', 
        '^(?!.*(I Wish))(?=.*(cat))', 
        '((cat\\b.*fish(\\b|es))|(fish(\\b|es).*cat\\b))'
    ]
    assert expected == actual
