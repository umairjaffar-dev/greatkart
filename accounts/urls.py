from django.urls import path
from . import views

urlpatterns = [
    ##  - URLs for authentication.
    path("login/", views.login, name="login"),
    path("register/", views.register, name="register"),
    path("logout/", views.logout, name="logout"),
    ##  - URLs to activate user through email link.
    path("activate/<uidb64>/<token>/", views.activate, name="activate"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("", views.dashboard, name="dashboard"),
    ##  - URLs to reset password.
    path("forgotPassword/", views.forgotPassword, name="forgotPassword"),
    path(
        "reset_password_validate/<uidb64>/<token>/",
        views.reset_password_validate,
        name="reset_password_validate",
    ),
    path("resetPassword/", views.resetPassword, name="resetPassword"),
]
