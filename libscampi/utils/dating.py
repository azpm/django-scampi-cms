import datetime
from django.db import models


def date_from_string(year, year_format, month, month_format, day='', day_format='', delim='__'):
    """
    Helper: get a datetime.date object given a format string and a year,
    month, and possibly day; raise a 404 for an invalid date.
    """
    date_format = delim.join((year_format, month_format, day_format))
    date_strine = delim.join((year, month, day))
    try:
        return datetime.datetime.strptime(date_strine, date_format).date()
    except ValueError:
        raise ValueError("Invalid date string '{datestr:>s}' given format '{format:>s}'".format(datestr=date_strine, format=date_format))


def date_lookup_for_field(field, date):
    """
    Get the lookup kwargs for looking up a date against a given Field. If the
    date field is a DateTimeField, we can't just do filter(df=date) because
    that doesn't take the time into account. So we need to make a range lookup
    in those cases.
    """
    if isinstance(field, models.DateTimeField):
        date_range = (
            datetime.datetime.combine(date, datetime.time.min),
            datetime.datetime.combine(date, datetime.time.max)
            )
        return {'%s__range' % field.name: date_range}
    else:
        return {field.name: date}
