from django.contrib import admin

from django.conf import settings
from django.conf.urls import include, url

from waldo.api.urls import api_v1_urlpatterns

from waldo import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', views.user_logout, name='logout'),

    url(r'^waldo/', include('waldo.urls')),
    url(r'^admin/', admin.site.urls),

]

if settings.DEBUG:
    if settings.COMBINE_API_AND_WEB_URLS:
        urlpatterns += [
            url(r'^api/1/', include(api_v1_urlpatterns, namespace='api')),
        ]
