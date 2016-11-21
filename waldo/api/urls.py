from __future__ import division, print_function, unicode_literals

from django.conf.urls import include, url
from rest_framework import routers

from .views import UserViewSet, PhotoViewSet, PhotoExifItemViewSet, action_post

# For this test - just use the Default ViewSet for now
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'photos', PhotoViewSet)
router.register(r'exif_items', PhotoExifItemViewSet)

# Break this out so waldo.urls can use it and root it apart from us.
api_v1_urlpatterns = [
    url(r'^', include(router.urls)),

    url(r'^action/$', action_post, name='action'),
]

urlpatterns = [
    url(r'^api/1/', include(api_v1_urlpatterns, namespace='api')),
]


