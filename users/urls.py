from django.urls import path

from users.views import MeView, SignInView, SignOutView, SignUpView

urlpatterns = [
    path("auth/sign-up", SignUpView.as_view(), name="sign-up"),
    path("auth/sign-in", SignInView.as_view(), name="sign-in"),
    path("auth/sign-out", SignOutView.as_view(), name="sign-out"),
    path("user/me", MeView.as_view(), name="user-me"),
]
