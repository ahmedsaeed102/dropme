from django.urls import path
from .views import *

urlpatterns = [
    # Leaderboard
    path("leaderboard/", Leaderboard.as_view(), name="leaderboard"),
    # Competitions
    path("competitions/", Competitions.as_view(), name="competitions"),
    path("competitions/<int:pk>/", CompetitionDetail.as_view(), name="competition_detail"),
    path("competitions/delete/<int:pk>/",CompetitionDelete.as_view(), name="competition_delete"),
    # Join
    path("competitions/join/<int:pk>/", JoinCompetition.as_view(), name="competition_join"),
    # Ranking
    path("competitions/ranking/<int:pk>/", CompetitionRanking.as_view(), name="competition_ranking",),
    # contact_us
    path("contactus/", LinksAPI.as_view(), name="contact_us"),
]
