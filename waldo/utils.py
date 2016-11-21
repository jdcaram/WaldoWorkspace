from __future__ import division, print_function, unicode_literals

from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404

TRUTHY_VALUES = ['true', '1', 'yes', 't', 'y']


def is_truthy(value):
    """Return `bool` of whether the given value is "truthy"."""
    if isinstance(value, bool):
        return value
    else:
        return str(value).lower() in TRUTHY_VALUES


def get_object_or_none(klass, *args, **kwargs):
    """
    Like django.shortcuts.get_object_or_404, but returns None if it cannot
    be found.
    """
    try:
        obj = get_object_or_404(klass, *args, **kwargs)
        return obj
    except Http404:
        return None

