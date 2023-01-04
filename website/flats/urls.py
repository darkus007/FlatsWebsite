from django.conf.urls.static import static
from django.urls import path, include

from flats.views import IndexList
from website import settings

urlpatterns = [
    path('', IndexList.as_view(), name='index'),
]

if settings.DEBUG:
    urlpatterns.append(path('__debug__/', include('debug_toolbar.urls')))
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
