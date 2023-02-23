from django.contrib import admin
from django.urls import path ,include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from users_api.views import UserViewSet
# from rest_framework.routers import DefaultRouter
urlpatterns = [
    path('admin/', admin.site.urls),
    path(' ', include('users_api.urls',namespace='users_api')),
    path('api-auth/', include('rest_framework.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# router=DefaultRouter()
# router.register('user',UserViewSet,basename='user')
# urlpatterns +=router.urls