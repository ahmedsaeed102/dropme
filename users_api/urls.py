from django.urls import path, include
from rest_framework_simplejwt.views import TokenBlacklistView, TokenRefreshView, TokenVerifyView, TokenObtainPairView
from rest_framework.routers import DefaultRouter
from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet
from . import views

router = DefaultRouter()
router.register("user_register", views.UserViewSet, basename="user_register")
router.register("devices", FCMDeviceAuthorizedViewSet)

urlpatterns = [
    # register user
    path("user_register/", include(router.urls)),
    # authentication (login, logout)
    path("user_login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("user_login/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("user_login/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("logout/", TokenBlacklistView.as_view(), name="token_blacklist"),
    # reset password
    path("reset_password_emaillink/", views.RequestPasswordResetEmail.as_view(), name="send_email_password",),
    path("password-reset/",  views.SetNewPasswordAPIView.as_view(), name="password-reset-complete",),
    path("password-reset/verify-otp/", views.VerifyPasswordResetOTP.as_view(), name="password-reset-verify-otp",),
    # edit profile
    path("<int:pk>/edit_profile/", views.ManageUserProfileView.as_view(), name="edit_profile",),
    # prefered language
    path("prefered_language/", views.PreferedLanguageView.as_view(), name="prefered_language",),
    # user points
    path("current_user/points/", views.CurrentUserTotalPointsView.as_view(), name="current_user_points",),
    # address list
    path("list_address/", views.LocationList.as_view(), name="create_address"),
    # user feedback
    path("feedbacks/list/", views.FeedbacksList.as_view(), name="list_feedback"),
    path("feedbacks/create/", views.FeedbackCreate.as_view(), name="create_feedback"),
    # anoynmous user
    path("anonymous/", views.AnonymousUser.as_view(), name="anonymous_user"),
]
