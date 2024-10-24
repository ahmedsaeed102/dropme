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
    # google auth
    path("google_auth/", views.GoogleAuth.as_view(), name="google_auth"),
    # reset password
    path("reset_password_emaillink/", views.RequestPasswordResetEmail.as_view(), name="send_email_password",),
    path("password-reset/",  views.SetNewPasswordAPIView.as_view(), name="password-reset-complete",),
    path("password-reset/verify-otp/", views.VerifyPasswordResetOTP.as_view(), name="password-reset-verify-otp",),
    # edit profile
    path("<int:pk>/edit_profile/", views.ManageUserProfileView.as_view(), name="edit_profile",),
    # preferred language
    path("preferred_language/", views.PreferredLanguageView.as_view(), name="preferred_language",),
    # referral code
    path("referral_code/", views.ReferralCodeView.as_view(), name="referral_code",),
    # user points
    path("current_user_details/", views.CurrentUserDetailsView.as_view(), name="current_user_details",),
    #  home page data
    path("home_page_data/", views.HomePageView.as_view(), name="home_page_data",),
    path("users_points", views.UsersPointsView.as_view(), name="users_points"),
    # address list
    path("list_address/", views.LocationList.as_view(), name="create_address"),
    # user feedback
    path("feedbacks/list/", views.FeedbacksList.as_view(), name="list_feedback"),
    path("feedbacks/create/", views.FeedbackCreate.as_view(), name="create_feedback"),
]
