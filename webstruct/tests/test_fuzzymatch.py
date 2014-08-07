from webstruct.semi.fuzzymatch import assign_bio_tags, merge_bio_tags, SPACES_SRE
from webstruct import HtmlTokenizer
from webstruct.utils import html_document_fromstring

def test_fuzzy_assign_bio_tags():
    html = """<div id="intro_contact">
         013-Witgoedreparaties.nl<br/>Postbus 27<br/>
         4500 AA Oostburg<br/><a href="mailto:info@013-witgoedreparaties.nl">info@013-witgoedreparaties.nl</a><br/>  tel: 013-5444999<br/></div></div>
        </div>
    """
    html_tokenizer = HtmlTokenizer()
    html_tokens, tags = html_tokenizer.tokenize_single(html_document_fromstring(html))
    pattern = ur'(^|{0})Postbus.*?Oostburg({0}|$)'.format(SPACES_SRE)
    choices = ['Postbus 22 4500AA Oostburg']
    tags = assign_bio_tags(html_tokens, pattern, 'ADDR', choices)
    assert tags == ['O', 'B-ADDR', 'I-ADDR', 'I-ADDR', 'I-ADDR', 'I-ADDR', 'O', 'O', 'O']

    html = """<div id="intro_contact">
         013-Witgoedreparaties.nl<br/>Postbus 27<br/>
         4500 AA Oostburg<br/>The Netherlands</br><a href="mailto:info@013-witgoedreparaties.nl">info@013-witgoedreparaties.nl</a><br/>  tel: 013-5444999<br/></div></div>
        </div>
    """
    html_tokens, tags = html_tokenizer.tokenize_single(html_document_fromstring(html))
    pattern = ur'(^|{0})Postbus.*?Oostburg{0}((the\s+)?ne(d|th)erlands?)?'.format(SPACES_SRE)
    choices = ['Postbus 22 4500AA Oostburg', 'Postbus 22 4500AA Oostburg the netherlands']
    tags = assign_bio_tags(html_tokens, pattern, 'ADDR', choices)
    # tokens == [u'013-Witgoedreparaties.nl', u'Postbus', u'27', u'4500', u'AA', u'Oostburg',
    # u'The', u'Netherlands', u'info@013-witgoedreparaties.nl', u'tel:', u'013-5444999']
    assert tags == ['O', 'B-ADDR', 'I-ADDR', 'I-ADDR', 'I-ADDR', 'I-ADDR', 'I-ADDR', 'I-ADDR', 'O', 'O', 'O']

    html = """<title>013-witgoedreparaties.nl | 013-witgoedreparaties.nl | title </title>"""
    html_tokens, tags = html_tokenizer.tokenize_single(html_document_fromstring(html))
    pattern = ur'(^|{0})013-Witgoedreparaties.nl({0}|$)'.format(SPACES_SRE)
    choices = ['013-witgoedreparaties.nl']
    tags = assign_bio_tags(html_tokens, pattern, 'ORG', choices)
    # tokens = [u'013-witgoedreparaties.nl', u'|', u'013-witgoedreparaties.nl', u'|', u'title']
    assert tags == ['B-ORG', 'O', 'B-ORG', 'O', 'O']


def test_fuzzy_assign_bio_tags_with_non_break_spaces():
    html_tokenizer = HtmlTokenizer()
    html = """<title>013-witgoedreparaties.nl | &#8203;013-witgoedreparaties.nl | title </title>"""
    html_tokens, tags = html_tokenizer.tokenize_single(html_document_fromstring(html))
    pattern = ur'(^|{0})013-Witgoedreparaties.nl({0}|$)'.format(SPACES_SRE)
    choices = ['013-witgoedreparaties.nl']

    tags = assign_bio_tags(html_tokens, pattern, 'ORG', choices)
    # tokens = [u'013-witgoedreparaties.nl', u'|', u'013-witgoedreparaties.nl', u'|', u'title']
    assert tags == ['B-ORG', 'O', 'B-ORG', 'O', 'O']

    html = """<title>013-witgoedreparaties.nl | &nbsp;013-witgoedreparaties.nl | title </title>"""
    html_tokens, tags = html_tokenizer.tokenize_single(html_document_fromstring(html))
    choices = ['013-witgoedreparaties.nl']

    tags = assign_bio_tags(html_tokens, pattern, 'ORG', choices)
    # tokens = [u'013-witgoedreparaties.nl', u'|', u'013-witgoedreparaties.nl', u'|', u'title']
    assert tags == ['B-ORG', 'O', 'B-ORG', 'O', 'O']


def test_merge_bio_tags():
    tags = merge_bio_tags(['B-ORG', 'O', 'B-ORG', 'O', 'O'], ['B-ORG', 'B-ADDR', 'B-ORG', 'O', 'O'])
    assert tags == ['B-ORG', 'B-ADDR', 'B-ORG', 'O', 'O']
