from django.shortcuts import get_object_or_404
from .serializers import CompetitionRankingSerializer
from .models import Competition

def competition_get(*, pk: int) -> Competition:
    return get_object_or_404(Competition, pk=pk)

def current_user_ranking(*, request) -> dict:
    return {
        "username": request.user.username,
        "photo": request.build_absolute_uri(request.user.profile_photo.url),
        "total_points": request.user.total_points,
        "rank": request.user.ranking,
    }

def competition_ranking(*, request, competition: Competition) -> dict:
    ranking = competition.competitionranking_set.all()[:10]
    serializer = CompetitionRankingSerializer(ranking, many=True, context={"request": request})
    has_currentuser_joined = competition.users.filter(pk=request.user.pk).exists()
    if has_currentuser_joined:
        current_user = competition.competitionranking_set.get(user=request.user.pk)
        current_user_ranking = {
            "username": request.user.username,
            "photo": request.build_absolute_uri(request.user.profile_photo.url),
            "points": current_user.points,
            "rank": current_user.ranking,
        }
    else:
        current_user_ranking = {
            "username": request.user.username,
            "photo": request.build_absolute_uri(request.user.profile_photo.url),
            "joined": False,
        }
    return {
        "status": "success",
        "message": "got competition ranking successfully",
        "data": {
            "current_user": current_user_ranking,
            "ranking": serializer.data,
        },
    }
