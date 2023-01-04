from django.urls import path

from flats.views import IndexList

urlpatterns = [
    path('', IndexList.as_view(), name='index'),
]