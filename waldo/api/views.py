from __future__ import division, print_function, unicode_literals

import logging
import os

# from boto.exception import S3ResponseError
from boto.s3.connection import S3Connection
from PIL import Image, ExifTags
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.filters import (
    DjangoFilterBackend,
    OrderingFilter,
    SearchFilter)
from rest_framework.generics import GenericAPIView as RestGenericAPIView
from rest_framework.response import Response

from .filters import ExifTypeFilter
from .serializers import UserSerializer, PhotoSerializer, PhotoExifItemSerializer, PhotoExpandedSerializer

from waldo.models import User, Photo, PhotoExifItem
from waldo import utils


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class PhotoViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    expanded_serializer_class = PhotoExpandedSerializer

    _is_expanded = False

    @property
    def is_expanded(self):
        return self._is_expanded

    @is_expanded.setter
    def is_expanded(self, value):
        self._is_expanded = value


    filter_backends = RestGenericAPIView.filter_backends + [
        DjangoFilterBackend,
        ExifTypeFilter,
        SearchFilter,
        OrderingFilter]

    def get_serializer_class(self):
        if self.is_expanded:
            return self.expanded_serializer_class

        return super(PhotoViewSet, self).get_serializer_class()

    # For filtering - Prefetch the Exif Items
    def get_queryset(self):
        qs = super(PhotoViewSet, self).get_queryset()

        # If we are going to be getting expanded - prefetch the EXIF Items
        if self.is_expanded:
            return qs.prefetch_related('exif_items')
        return qs

    def retrieve(self, request, *args, **kwargs):
        # check if expanded
        # if utils.is_truthy(self.request.query_params.get('expanded', '')):
        #     self.is_expanded = True
        self.is_expanded = True

        return super(PhotoViewSet, self).retrieve(self, request, *args, **kwargs)


class PhotoExifItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = PhotoExifItem.objects.all()
    serializer_class = PhotoExifItemSerializer

    filter_fields = ['exif_name', 'exif_value', 'photo']

    filter_backends = RestGenericAPIView.filter_backends + [
        DjangoFilterBackend,
        SearchFilter]


@api_view(['POST'])
def action_post(request):
    """
    API Method to perform certain actions.  Pass 'retrieve' or 'delete' as value for 'action' key
    :param request:
    :return: response
    """

    action = request.data.get('action', None)
    return_status = status.HTTP_400_BAD_REQUEST

    result_dictionary = {"response_message": "Acknowledged"}

    directory_name = "files/"

    try:

        if action == "retrieve":

            # I could also move this method into the Photo Model (Fat Model & Thin View/Controller)
            conn = S3Connection(anon=True)
            bucket = conn.get_bucket("waldo-recruiting")

            count = 0
            errors = []

            # go through the list of photos
            bucket_list = bucket.list()
            for key_object in bucket_list:
                key_string = str(key_object.key)

                try:
                    photo = utils.get_object_or_none(Photo, s3_key=key_string)

                    # If the photo is already in Database - already processed - Just skip
                    if photo:
                        continue

                    # construct the file name to save at
                    file_name = directory_name + key_string

                    # save to the filesystem if it doesn't already exist
                    if not os.path.exists(file_name):
                        key_object.get_contents_to_filename(file_name)

                    # save a photo object to the DB
                    photo = Photo.objects.create(
                        name=file_name,
                        s3_key=key_string,
                    )

                    count += 1

                    # Open with Pillow to get the EXIF data
                    im = Image.open(file_name)
                    if hasattr(im, '_getexif'):
                        exif = im._getexif()

                        for exif_key, exif_value in exif.iteritems():
                            exif_name = ExifTags.TAGS.get(exif_key)

                            # MakerNote has a lot of weird characters - I'd need to look into this more
                            if exif_name == "MakerNote":
                                continue

                            # convert value to string (can be int/float/etc)
                            exif_string_value = str(exif_value).strip()

                            # Only add to Database if we know what the Text Name of the value is
                            # and there is a value

                            # If I was doing this fully, I'd probably have the Value for the ExifTags
                            # broken up by Value type - have Date Times and Integers - so the filtering would be
                            # better
                            if exif_name and exif_string_value:
                                exif_item = PhotoExifItem.objects.create(
                                    photo=photo,
                                    exif_name=exif_name,
                                    exif_value=exif_string_value,
                                )
                except Exception as exc:
                    # I've seen S3ResponseError as well as String Parsing error on Exif Item

                    error_message = "Error processing Photo - S3 Key: {0}; Error Msg: {1}.".format(
                        key_string,
                        exc.message
                    )

                    errors.append(error_message)

                    # notify server team about processing errors  - Usually I'd use Sentry
                    manual_logger = logging.getLogger("manual_waldo")
                    if manual_logger:
                        manual_logger.error(error_message)

            result_dictionary["photo_count"] = count
            if errors:
                result_dictionary["errors"] = errors
            return_status = status.HTTP_200_OK

        elif action == "delete":

            Photo.objects.all().delete()

            return_status = status.HTTP_204_NO_CONTENT

        else:
            result_dictionary["reason"] = "A valid 'action' is required"

    except Exception as exc1:
        result_dictionary["error"] = exc1.message

    return Response(result_dictionary, status=return_status)
