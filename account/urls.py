from django.urls import path
from .views import sign_up, sign_in, sign_out
from django.conf import settings

urlpatterns = [
    path("register/", sign_up, name="register"),
    path("login/", sign_in, name="login"),
    path(
        "logout/",
        sign_out,
        name="logout",
    ),
]
