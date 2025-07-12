from django.urls import path, include
from .views.overview import Overview

urlpatterns = [
	path('metrics/overview/', Overview.as_view(), name='overview'),
	# Add other dashboard-related URLs here
]
