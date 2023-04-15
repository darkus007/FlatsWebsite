from django.urls import path

from members.views import UserRegistrationView, UserChangeView, UserPasswordChangeView, RegisterDoneView
from members.views import password_changed, user_email_activate, send_email_activate_letter


urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('register/activate/<str:sign>/', user_email_activate, name='email-activate'),
    path('register/done/', RegisterDoneView.as_view(), name='register-done'),
    path('repeat-send-email/<int:flat_id>/', send_email_activate_letter, name='repeat-send-email'),
    path('edit-user/', UserChangeView.as_view(), name='edit-user'),
    path('password/', UserPasswordChangeView.as_view(template_name='registration/change_password.html'),
         name='password-change'),
    path('password-success/', password_changed, name='password-changed'),
]
