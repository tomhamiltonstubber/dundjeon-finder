import datetime

from django import forms
from django.utils import timezone


class DFFormMixin:
    def __init__(self, request, *args, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)
        for f in self.fields:
            self.fields[f].widget.attrs.update({'class': 'dk-field'})


class DFForm(DFFormMixin, forms.Form):
    pass


class DFModelForm(DFFormMixin, forms.ModelForm):
    pass


def date2datetime(date, day_end=False):
    """
    convert date to datetime in current timezone.

    :param date: datetime.date object
    :param day_end: if true 23.59.59 is used for the time
    :return: datetime.datetime object
    """
    if day_end:
        hours, mins, seconds = 23, 59, 59
    else:
        hours, mins, seconds = 0, 0, 0
    tzinfo = timezone.get_current_timezone()
    return tzinfo.localize(datetime.datetime(date.year, date.month, date.day, hours, mins, seconds))
