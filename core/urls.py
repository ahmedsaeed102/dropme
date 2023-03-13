from django.contrib import admin
from django.urls import path ,include
# from rest_framework_simplejwt.views import (
#     TokenObtainPairView,
    
# )
from users_api.views import UserViewSet,RequestPasswordResetEmail,PasswordTokenCheckAPI,SetNewPasswordAPIView,ManageUserProfileView,MyTokenObtainPairView
from rest_framework_simplejwt.views import TokenBlacklistView
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static

from drf_spectacular.views import SpectacularAPIView,SpectacularSwaggerView

router=DefaultRouter()
router.register('user_register',UserViewSet,basename='user_register')



urlpatterns = [
    path('admin/', admin.site.urls),
    # path(' ', include('users_api.urls',namespace='users_api')),
    path('user_register/', include(router.urls)),
    path('edit_profile/', ManageUserProfileView.as_view(), name='edit_profile'),
    path('reset_password_emaillink/',RequestPasswordResetEmail.as_view(), name='send_email_password'),
    path('password-reset/<uidb64>/<token>/',PasswordTokenCheckAPI.as_view(), name='password-reset-confirm'),
    path('password-reset/', SetNewPasswordAPIView.as_view(),name='password-reset-complete'),
    path('logout/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('user_login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('', SpectacularSwaggerView.as_view(url_name='schema')),
    path('', include('machine_api.urls'), name='machine_api'),
    path('', include('competition_api.urls'), name='competition_api'),
]
# urlpatterns +=router.urls
urlpatterns +=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)