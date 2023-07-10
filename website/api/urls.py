from django.urls import path

from .views import (
    ProjectList, AllFlatsLastPriceList,
    UserAPIView, create_user,
    send_email_for_activate_user, user_email_activate,
    UserSelectedFlatsAPIView
)

app_name = 'api_v1'

urlpatterns = [
    path('projects/', ProjectList.as_view(), name='projects'),
    path('flats/', AllFlatsLastPriceList.as_view(), name='flats'),
    path('user/selected-flats/', UserSelectedFlatsAPIView.as_view(), name='selected-flats'),
    path('user/create/', create_user, name='user-create'),
    path('user/send-activation-email/', send_email_for_activate_user, name='send-activation-email'),
    path('user/activate-email/<str:sign>/', user_email_activate, name='activate-email'),
    path('user/', UserAPIView.as_view(), name='user'),
]
