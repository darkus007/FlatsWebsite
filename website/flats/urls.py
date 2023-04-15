from django.conf.urls.static import static
from django.urls import path, include

from flats.views import IndexList, FlatDetailView, ProjectListView, add_flat_to_selected, SelectedFlatList
from website import settings

urlpatterns = [
    path('', IndexList.as_view(), name='index'),
    path('flat/<int:flatid>/', FlatDetailView.as_view(), name='flat-detail'),
    path('project/<int:project_id>/', ProjectListView.as_view(), name='project-list'),
    path('user-choice/<int:user_id>/', SelectedFlatList.as_view(), name='user-choice'),
    path('select_flat/<int:flat_id>/', add_flat_to_selected, name='select-flat'),
]

if settings.DEBUG:
    urlpatterns.append(path('__debug__/', include('debug_toolbar.urls')))
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
