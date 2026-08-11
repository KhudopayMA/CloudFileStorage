from django.urls import path

from users.views import SignUpView, SignInView, MeView, SignOutView

urlpatterns = [
    path("auth/sign-up", SignUpView.as_view()),
    path("auth/sign-in", SignInView.as_view()),
    path("auth/sign-out", SignOutView.as_view()),
    path("user/me", MeView.as_view()),
]