from django.urls import path
from django.contrib.auth import views as auth_views
from .views import register, profile, view_profile, contact, follow_user, unfollow_user
from .forms import PasswordResetEmailCheck

urlpatterns = [
    path("register/", register, name="register"),
    path("profile/", profile, name="profile"),
    path("author/<str:username>/", view_profile, name="author-profile"),
    path("contact/", contact, name="contact"),
    path("follow/<int:user_id>/", follow_user, name="follow"),
    path("unfollow/<int:user_id>/", unfollow_user, name="unfollow"),
    path("login/", auth_views.LoginView.as_view(template_name="users/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(template_name="users/logout.html"), name="logout"),
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='users/password_reset_email.html', form_class=PasswordResetEmailCheck), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='users/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(
        template_name='users/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='users/password_reset_complete.html'), name='password_reset_complete'),
]
