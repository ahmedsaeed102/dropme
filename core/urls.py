from django.contrib import admin
from django.urls import path ,include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from users_api.views import UserViewSet,ManageUserProfileView
from rest_framework.routers import DefaultRouter

router=DefaultRouter()
router.register('user_register',UserViewSet,basename='user_register')



urlpatterns = [
    path('admin/', admin.site.urls),
    # path(' ', include('users_api.urls',namespace='users_api')),
    path('edit_profile/', ManageUserProfileView.as_view(), name='edit_profile'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('machine/', include('machine_api.urls'), name='machine_api'),
    path('community/', include('community_api.urls'), name='community_api'),
]
urlpatterns +=router.urls