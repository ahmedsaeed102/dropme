from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


urlpatterns = [
    path("admin/", admin.site.urls),
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
    path("", include("notification.urls")),
    path("", include("marketplace.urls")),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# urlpatterns +=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
