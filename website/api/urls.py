from django.urls import path

from .views import (
    ProjectList, AllFlatsLastPriceList,
    UserAPIView, create_user,
    send_email_for_activate_user, user_email_activate,
    UserSelectedFlatsAPIView
)

app_name = 'api_v1'

urlpatterns = [
    path('projects/', ProjectList.as_view()),
    path('flats/', AllFlatsLastPriceList.as_view()),
    path('user/selected-flats/', UserSelectedFlatsAPIView.as_view()),
    path('user/create/', create_user),
    path('user/send-activation-email/', send_email_for_activate_user),
    path('user/activate-email/<str:sign>/', user_email_activate),
    path('user/', UserAPIView.as_view()),
]
