from django.contrib import admin
from django.urls import path, include
from users_api.views import LocationList, RequestPasswordOtp,UserViewSet,RequestPasswordResetEmail,SetNewPasswordAPIView,ManageUserProfileView,MyTokenObtainPairView

from rest_framework_simplejwt.views import TokenBlacklistView
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet

router=DefaultRouter()
router.register('user_register',UserViewSet,basename='user_register')
router.register('devices', FCMDeviceAuthorizedViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('list_address/', LocationList.as_view(), name='create_address'),

    path('user_register/', include(router.urls)),
    path('<int:pk>/edit_profile/', ManageUserProfileView.as_view(), name='edit_profile'),
    path('reset_password_emaillink/',RequestPasswordResetEmail.as_view(), name='send_email_password'),
    path('password-reset/', SetNewPasswordAPIView.as_view(),name='password-reset-complete'),
    path('logout/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('user_login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('', SpectacularSwaggerView.as_view(url_name='schema')),
    path('', include('machine_api.urls'), name='machine_api'),
    path('', include('competition_api.urls'), name='competition_api'),
    path('', include('machine_api.routing')),
    path('', include('community_api.urls'), name='community_api'),
    path('', include('community_api.routing')),

]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# urlpatterns +=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)