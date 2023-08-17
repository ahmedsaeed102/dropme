from django.urls import path
from .views import *

urlpatterns = [
    path("competitions/", Competitions.as_view(), name="competitions"),
    path(
        "competitions/<int:pk>/", CompetitionDetail.as_view(), name="competition_detail"
    ),
    path(
        "competitions/delete/<int:pk>/",
        CompetitionDelete.as_view(),
        name="competition_delete",
    ),
    path(
        "competitions/join/<int:pk>/",
        JoinCompetition.as_view(),
        name="competition_join",
    ),
    path(
        "competitions/ranking/<int:pk>/",
        CompetitionRanking.as_view(),
        name="competition_ranking",
    ),
    path("leaderboard/", Leaderboard.as_view(), name="leaderboard"),
    # Home page ads
    path("advertisements/", AdsList.as_view(), name="ads"),
]
