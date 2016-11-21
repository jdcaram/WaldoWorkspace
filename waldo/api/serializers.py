from __future__ import division, print_function, unicode_literals

from rest_framework import serializers

from waldo.models import User, Photo, PhotoExifItem


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')


class PhotoExifItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = PhotoExifItem
        fields = [
            'id',
            'photo',
            'exif_name',
            'exif_value',
        ]


class PhotoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Photo
        fields = [
            'id',
            'name',
            's3_key',
        ]


class PhotoExpandedSerializer(serializers.ModelSerializer):

    exif_items = PhotoExifItemSerializer(
        many=True,
        required=False)

    class Meta:
        model = Photo
        fields = [
            'id',
            'name',
            's3_key',
            'exif_items',
        ]
