from django.contrib import admin
from django.urls import path ,include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from users_api.views import UserViewSet,UserLogViewSet
from rest_framework.routers import DefaultRouter

router=DefaultRouter()
router.register('user_register',UserViewSet,basename='user_register')
router.register('user_login',UserLogViewSet,basename='user_login')

urlpatterns = [
    path('admin/', admin.site.urls),
    path(' ', include('users_api.urls',namespace='users_api')),
    path('api-auth', include('rest_framework.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]


urlpatterns +=router.urls