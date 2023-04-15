from django.urls import path

from members.views import UserRegistrationView, UserChangeView, UserPasswordChangeView, password_changed

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('edit-user/', UserChangeView.as_view(), name='edit-user'),
    path('password/', UserPasswordChangeView.as_view(template_name='registration/change_password.html'),
         name='password-change'),
    path('password-success/', password_changed, name='password-changed'),
]
