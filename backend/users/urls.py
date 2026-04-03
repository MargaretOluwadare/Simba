from django.urls import include
from django.urls import re_path as url, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "users"

router = DefaultRouter()


router.register("register", views.UserRegisterViewSet, basename="register")
router.register("verify-email", views.VerifyEmailViewset, basename="verify-email")
router.register("login", views.LoginViewset, basename="login")
router.register("logout", views.LogoutViewSet, basename="logout")
router.register("forgot-password", views.ForgotPasswordViewset, basename="forgot-password")
router.register("reset-password", views.ResetPasswordViewset, basename="reset-password")
router.register("resend-email", views.ResendEmailViewSet, basename="resend-email")


urlpatterns = [
    url(r"", include(router.urls)),
    path("profile/", views.ProfileView.as_view(), name="profile"),
]
