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


def test_adjust_subject():
    h = hato.HatoCore(None, None, None, None, None, None, None)

    # no need to adjust
    subject = "タイトル"
    comment = "雪と氷の世界・北海道には、この時季ここでしかできないオンリーワンのイベントが盛りだくさん。"
    adjusted = h.adjust_subject(subject, comment)
    assert(adjusted == "タイトル")

    # embedded text
    subject = "無題"
    adjusted = h.adjust_subject(subject, comment)
    assert(adjusted == "無題 (雪と氷の世界・北海道には、この時季ここでしかできないオンリー...)")

    # masking twitter mention
    subject = "@abc"
    adjusted = h.adjust_subject(subject, comment)
    assert(adjusted == "%abc")

    subject = "＠abc"
    adjusted = h.adjust_subject(subject, comment)
    assert(adjusted == "%abc")

    # <br />
    subject = "無題"
    comment = "頑張ってはいるけど需要ないんだよなこの子<br /><br />推すならたわしの方が伸びるよ"
    adjusted = h.adjust_subject(subject, comment)
    assert(adjusted == "無題 (頑張ってはいるけど需要ないんだよなこの子推すならたわしの方が...)")
