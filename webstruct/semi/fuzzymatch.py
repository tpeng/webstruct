"""
This class help to generate the training data from partially labelled data with fuzzy match.

it need fuzzywuzzy_ installed.

.. _fuzzywuzzy: https://github.com/seatgeek/fuzzywuzzy

"""
import re
import warnings
from webstruct.sequence_encoding import IobEncoder

# adapted from http://en.wikipedia.org/wiki/Space_(punctuation)#Spaces_in_Unicode
SPACES_SRE = ur'[\s\u0020\u00a0\u1680\u18e0\u2000-\u200d\u202f\u205f\u2060\u3000\ufeff]+'

def identity(x):
    return x

def assign_bio_tags(html_tokens, pattern, entity, choices, threshold=0.9, postprocess=identity, verbose=False):
    """Assign the BIO tags with fuzzy string match.

    It first finds the candidates using the given regex
    pattern and then compare similarity to the string in ``choices``,

    if the similarity to any ``choices`` exceed the ``threshold``, assign the
    ``BIO`` entities to corresponding tags.

    Parameters
    ----------
    html_tokens : HtmlToken list
        a list of ``HtmlToken``

    pattern: string
        a regex pattern used to find the match string from the text joinned from ``html_tokens``

    entity : string
        the entitiy type (e.g. ADDR or ORG) want to assign to.

    choices : string list
        a list of string to get the similarity to the string found by ``pattern``.

    threshold: float
        a float value to decide if found text should assign to given entity.

    postprocess: function
        a function to post process the matched text before compare to ``choices``

    Returns
    -------
    a list of BIO tags

    Notes
    -----
    the ``pattern`` should include the whitespaces see ``SPACES_SRE``.

    """
    tokens = [html_token.token for html_token in html_tokens]
    iob_encoder = IobEncoder()

    from fuzzywuzzy import process

    def repl(m):
        extracted = postprocess(m.group(0))
        if verbose:
            print extracted, choices

        if process.extractBests(extracted, choices, score_cutoff=threshold * 100):
            return u' __START_{0}__ {1} __END_{0}__ '.format(entity, m.group(0))
        return m.group(0)

    text = re.sub(pattern, repl, u" ".join(tokens), flags=re.I | re.U | re.DOTALL)
    tags = [tag for _, tag in iob_encoder.encode(text.split())]
    assert len(html_tokens) == len(tags), 'len(html_tokens): %s and len(tags): %s are not matched' % \
                (len(html_tokens), len(tags))
    return tags

def merge_bio_tags(*tag_list):
    """Merge BIO tags"""
    def select_tag(x, y):

        if x != 'O' and y != 'O' and x.split('-')[-1] == y.split('-')[-1]:
            warnings.warn('conflict BIO tag %s %s' % (x, y))

        # later one wins
        if y != 'O':
            return y
        if x != 'O':
            return x
        return 'O'
    return [reduce(select_tag, i) for i in zip(*tag_list)]
