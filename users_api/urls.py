from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenBlacklistView,
    TokenRefreshView,
    TokenVerifyView,
    TokenObtainPairView,
)
from rest_framework.routers import DefaultRouter
from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet
from .views import (
    LocationList,
    UserViewSet,
    RequestPasswordResetEmail,
    SetNewPasswordAPIView,
    ManageUserProfileView,
    VerifyPasswordResetOTP,
    CurrentUserTotalPointsView,
)

router = DefaultRouter()
router.register("user_register", UserViewSet, basename="user_register")
router.register("devices", FCMDeviceAuthorizedViewSet)


urlpatterns = [
    # user crud
    path("user_register/", include(router.urls)),
    path(
        "current_user/points/",
        CurrentUserTotalPointsView.as_view(),
        name="current_user_points",
    ),
    # authentication
    path("user_login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("user_login/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("user_login/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("logout/", TokenBlacklistView.as_view(), name="token_blacklist"),
    # reset password
    path(
        "reset_password_emaillink/",
        RequestPasswordResetEmail.as_view(),
        name="send_email_password",
    ),
    path(
        "password-reset/",
        SetNewPasswordAPIView.as_view(),
        name="password-reset-complete",
    ),
    path(
        "password-reset/verify-otp/",
        VerifyPasswordResetOTP.as_view(),
        name="password-reset-verify-otp",
    ),
    # edit profile
    path(
        "<int:pk>/edit_profile/", ManageUserProfileView.as_view(), name="edit_profile"
    ),
    # address list
    path("list_address/", LocationList.as_view(), name="create_address"),
]
