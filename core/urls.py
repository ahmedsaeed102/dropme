from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet

router = DefaultRouter()
# router.register("user_register", UserViewSet, basename="user_register")
router.register("devices", FCMDeviceAuthorizedViewSet)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("user_register/", include(router.urls)),
    # docs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("", SpectacularSwaggerView.as_view(url_name="schema")),
    # my apps
    path("", include("users_api.urls"), name="users_api"),
    path("", include("machine_api.urls"), name="machine_api"),
    path("", include("competition_api.urls"), name="competition_api"),
    path("", include("machine_api.routing")),
    path("", include("community_api.urls"), name="community_api"),
    path("", include("community_api.routing")),
]

# urlpatterns +=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
