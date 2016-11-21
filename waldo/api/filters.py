from __future__ import division, print_function, unicode_literals

from django.core.exceptions import ValidationError
from django.forms import Form, CharField
from rest_framework.filters import BaseFilterBackend


class CharForm(Form):
    text = CharField()


class ExifTypeFilter(BaseFilterBackend):
    """
    Adds Child EXIF Field Filtering on Photos
    """

    def filter_queryset(self, request, queryset, view):

        for query_param in request.query_params.keys():
            field = self.parse_query_param(query_param)

            if field:
                value = request.query_params[query_param]

                form = CharForm(data={'text': value})

                if not form.is_valid():
                    raise ValidationError(form.errors)

                value = form.cleaned_data['text']

                queryset = queryset.filter(exif_items__exif_name=field, exif_items__exif_value=value)

        return queryset

    def parse_query_param(self, query_param):
        """
        Parse query param - remove 'exif-'
        """
        if query_param.startswith("exif-"):
            query_param = query_param[5:]

        return query_param
