
from django.conf.urls import url


from waldo import views

urlpatterns = [

    url(r'^$', views.PhotoListView.as_view(), name='photo-list'),

]
