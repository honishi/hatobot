#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import hato
import pytest

RESPONSE_FILE_IMG = os.path.dirname(os.path.realpath(__file__)) + "/responses/img.cgi.utf-8"


def test_parse_img():
    h = hato.HatoCore(None, None, None, None, None, None, None)
    text = open(RESPONSE_FILE_IMG, 'r').read()
    parsed = h.parse_img(text)

    assert(len(parsed))
