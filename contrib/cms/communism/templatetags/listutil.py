"""
Template filters to partition lists into columns or columns.

A common use-case is for splitting a list into a table with columns::

    {% load listutil %}
    <table>
    {% for column in mylist|columns:3 %}
        <tr>
        {% for item in column %}
            <td>{{ item }}</td>
        {% endfor %}
        </tr>
    {% endfor %}
    </table>
"""

from django.template import Library

register = Library()

def columns(thelist, n):
    """
    Break a list into ``n`` columns, filling up each column to the maximum equal
    length possible. For example::

        >>> l = range(10)

        >>> columns(l, 2)
        [[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]

        >>> columns(l, 3)
        [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9]]

        >>> columns(l, 4)
        [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]

        >>> columns(l, 5)
        [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]

        >>> columns(l, 9)
        [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9], [], [], [], []]

        # This filter will always return `n` columns, even if some are empty:
        >>> columns(range(2), 3)
        [[0], [1], []]
    """
    try:
        n = int(n)
        thelist = list(thelist)
    except (ValueError, TypeError):
        return [thelist]
    list_len = len(thelist)
    split = list_len // n

    if list_len % n != 0:
        split += 1
    return [thelist[split*i:split*(i+1)] for i in range(n)]

def columns_distributed(thelist, n):
    """
    Break a list into ``n`` columns, distributing columns as evenly as possible
    across the columns. For example::

        >>> l = range(10)

        >>> columns_distributed(l, 2)
        [[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]

        >>> columns_distributed(l, 3)
        [[0, 1, 2, 3], [4, 5, 6], [7, 8, 9]]

        >>> columns_distributed(l, 4)
        [[0, 1, 2], [3, 4, 5], [6, 7], [8, 9]]

        >>> columns_distributed(l, 5)
        [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]

        >>> columns_distributed(l, 9)
        [[0, 1], [2], [3], [4], [5], [6], [7], [8], [9]]

        # This filter will always return `n` columns, even if some are empty:
        >>> columns(range(2), 3)
        [[0], [1], []]
    """
    try:
        n = int(n)
        thelist = list(thelist)
    except (ValueError, TypeError):
        return [thelist]
    list_len = len(thelist)
    split = list_len // n

    remainder = list_len % n
    offset = 0
    columns = []
    for i in range(n):
        if remainder:
            start, end = (split+1)*i, (split+1)*(i+1)
        else:
            start, end = split*i+offset, split*(i+1)+offset
        columns.append(thelist[start:end])
        if remainder:
            remainder -= 1
            offset += 1
    return columns

register.filter(columns)
register.filter(columns_distributed)

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()