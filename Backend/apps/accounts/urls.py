# apps/accounts/urls.py
from django.urls import path
from .api.views.account_views import (
    RegisterView, LoginView, MeView, ThrottledTokenRefreshView
)

urlpatterns = [
    path("register/",      RegisterView.as_view(),    name="register"),
    path("login/",         LoginView.as_view(),        name="login"),
    path("token/refresh/", ThrottledTokenRefreshView.as_view(), name="token-refresh"),
    path("me/",            MeView.as_view(),           name="me"),
]