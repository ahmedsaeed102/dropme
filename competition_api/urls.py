from django.urls import path
from .views import *

urlpatterns = [
    path('competitions/', Competitions.as_view(), name='competitions'),
]