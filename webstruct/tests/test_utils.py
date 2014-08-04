#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from webstruct.utils import human_sorted, fuzzy_assign_bio_tags, merge_bio_tags
from webstruct import HtmlTokenizer
from webstruct.utils import html_document_fromstring

def test_human_sorted():
    assert human_sorted(['5', '10', '7', '100']) == ['5', '7', '10', '100']
    assert human_sorted(['foo1', 'foo10', 'foo2']) == ['foo1', 'foo2', 'foo10']

def test_fuzzy_assign_bio_tags():
    html = """<div id="intro_contact">
         013-Witgoedreparaties.nl<br/>Postbus 27<br/>
         4500 AA Oostburg<br/><a href="mailto:info@013-witgoedreparaties.nl">info@013-witgoedreparaties.nl</a><br/>  tel: 013-5444999<br/></div></div>
        </div>
    """
    html_tokenizer = HtmlTokenizer()
    html_tokens, tags = html_tokenizer.tokenize_single(html_document_fromstring(html))
    pattern = ur'(Postbus.*?Oostburg)'
    choices = ['Postbus 22 4500AA Oostburg']
    tags = fuzzy_assign_bio_tags(html_tokens, pattern, 'ADDR', choices)
    assert tags == ['O', 'B-ADDR', 'I-ADDR', 'I-ADDR', 'I-ADDR', 'I-ADDR', 'O', 'O', 'O']

    html = """<div id="intro_contact">
         013-Witgoedreparaties.nl<br/>Postbus 27<br/>
         4500 AA Oostburg<br/>The Netherlands</br><a href="mailto:info@013-witgoedreparaties.nl">info@013-witgoedreparaties.nl</a><br/>  tel: 013-5444999<br/></div></div>
        </div>
    """
    html_tokens, tags = html_tokenizer.tokenize_single(html_document_fromstring(html))
    pattern = ur'(Postbus.*?Oostburg\s+(the\s+)?ne(d|th)erlands?)'
    choices = ['Postbus 22 4500AA Oostburg', 'Postbus 22 4500AA Oostburg the netherlands']
    tags = fuzzy_assign_bio_tags(html_tokens, pattern, 'ADDR', choices)
    # tokens == [u'013-Witgoedreparaties.nl', u'Postbus', u'27', u'4500', u'AA', u'Oostburg',
    # u'The', u'Netherlands', u'info@013-witgoedreparaties.nl', u'tel:', u'013-5444999']
    assert tags == ['O', 'B-ADDR', 'I-ADDR', 'I-ADDR', 'I-ADDR', 'I-ADDR', 'I-ADDR', 'I-ADDR', 'O', 'O', 'O']

    html = """<title>013-witgoedreparaties.nl | 013-witgoedreparaties.nl | title </title>"""
    html_tokens, tags = html_tokenizer.tokenize_single(html_document_fromstring(html))
    pattern = ur'013-Witgoedreparaties.nl'
    choices = ['013-witgoedreparaties.nl']
    tags = fuzzy_assign_bio_tags(html_tokens, pattern, 'ORG', choices)
    # tokens = [u'013-witgoedreparaties.nl', u'|', u'013-witgoedreparaties.nl', u'|', u'title']
    assert tags == ['B-ORG', 'O', 'B-ORG', 'O', 'O']

def test_fuzzy_assign_bio_tags_with_zero_width_space():
    html_tokenizer = HtmlTokenizer()
    html = """<title>013-witgoedreparaties.nl | &#8203;013-witgoedreparaties.nl | title </title>"""
    html_tokens, tags = html_tokenizer.tokenize_single(html_document_fromstring(html))
    tokens = [t.token for t in html_tokens]
    pattern = ur'(^|\s+|\u200b+)013-Witgoedreparaties.nl\s+'
    choices = ['013-witgoedreparaties.nl']

    tags = fuzzy_assign_bio_tags(html_tokens, pattern, 'ORG', choices)
    # tokens = [u'013-witgoedreparaties.nl', u'|', u'013-witgoedreparaties.nl', u'|', u'title']
    assert tags == ['B-ORG', 'O', 'B-ORG', 'O', 'O']

def test_merge_bio_tags():
    tags = merge_bio_tags(['B-ORG', 'O', 'B-ORG', 'O', 'O'], ['B-ORG', 'B-ADDR', 'B-ORG', 'O', 'O'])
    assert tags == ['B-ORG', 'B-ADDR', 'B-ORG', 'O', 'O']

    tags = merge_bio_tags(['B-ORG', 'I-ORG', 'B-ORG', 'O', 'O'], ['B-ORG', 'B-ADDR', 'B-ORG', 'O', 'O'])
    assert tags == ['B-ORG', 'B-ADDR', 'B-ORG', 'O', 'O']

    tags = merge_bio_tags(['B-ORG', 'I-ORG', 'B-ORG', 'O', 'O'], ['B-ORG', 'B-ADDR', 'B-ORG', 'O', 'O'], ['B-ORG', 'B-ADDR', 'B-ORG', 'O', 'B-ADDR'])
    assert tags == ['B-ORG', 'B-ADDR', 'B-ORG', 'O', 'B-ADDR']
