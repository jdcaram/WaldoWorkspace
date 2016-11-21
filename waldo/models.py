from __future__ import division, print_function, unicode_literals

import uuid

from django.db import models
from django.db.models.query import QuerySet as DjangoQuerySet
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices

from django.core.urlresolvers import reverse
from django.db.models import (
    BooleanField,
    DateField,
    ForeignKey,
    IntegerField,
    Max,
    Q,
    URLField)


class Photo(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=100, blank=True)
    s3_key = models.CharField(max_length=100, blank=True)
    # exif_json = JSONField(null=True, blank=True)

    def __unicode__(self):
        return self.name


class PhotoExifQuerySet(DjangoQuerySet):
    """Chainable, custom, query methods for PhotoExif Items."""

    pass


class PhotoExifItem(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    exif_name = models.CharField(max_length=100, blank=True)
    exif_value = models.CharField(max_length=1000, blank=True)

    photo = ForeignKey(Photo, related_name='exif_items')

    objects = PhotoExifQuerySet.as_manager()

    def __unicode__(self):
        return "<Photo %s Exif %s>" % (self.photo.id, self.id)



