stopwords = '''
i
a
an
are
as
at
be
by
for
from
how
in
is
it
of
on
or
that
the
this
to
was
what
when
where
'''.split()


def strip_stopwords(sentence):
    """Removes stopwords - also normalizes whitespace"""
    words = sentence.split()
    sentence = []
    for word in words:
        if word.lower() not in stopwords:
            sentence.append(word)
    return sentence
