from django.urls import path
from .views import *

urlpatterns = [
    path('competitions/', Competitions.as_view(), name='competitions'),
    path('competitions/<int:pk>/', CompetitionDetail.as_view(), name='competition_detail'),
    path('competitions/delete/<int:pk>/', CompetitionDelete.as_view(), name='competition_delete'),
]