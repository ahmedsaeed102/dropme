import requests
import os
from datetime import timedelta, datetime
from django.db.models import Sum, F
from django.utils.timezone import make_aware
from django.utils import timezone
from channels.db import database_sync_to_async
from rest_framework.exceptions import APIException
from users_api.models import UserModel
from .models import RecycleLog


@database_sync_to_async
def update_user_points(user_pk, points):
    user = UserModel.objects.get(pk=user_pk)
    user.total_points += points
    user.save()
    for competion in user.comp_user.all():
        if competion.is_ongoing:
            rank = competion.competitionranking_set.get(
                competition=competion.pk, user=user_pk
            )
            rank.points += points
            rank.save()


def claculate_travel_distance_and_time(userlocation, machinelocation):
    data = {}

    timebyfoot = requests.get(
        f"https://routing.openstreetmap.de/routed-foot/route/v1/driving/{userlocation[0]},{userlocation[1]};{machinelocation[0]},{machinelocation[1]}"
    ).json()

    timebycar = requests.get(
        f"https://routing.openstreetmap.de/routed-car/route/v1/driving/{userlocation[0]},{userlocation[1]};{machinelocation[0]},{machinelocation[1]}"
    ).json()

    timebybike = requests.get(
        f"https://routing.openstreetmap.de/routed-bike/route/v1/driving/{userlocation[0]},{userlocation[1]};{machinelocation[0]},{machinelocation[1]}"
    ).json()

    try:
        data["distance"] = timebyfoot["routes"][0]["distance"]
        data["timebyfoot"] = timebyfoot["routes"][0]["duration"] / 60
        data["timebycar"] = timebycar["routes"][0]["duration"] / 60
        data["timebybike"] = timebybike["routes"][0]["duration"] / 60
    except:
        raise APIException("No route found")

    return data


def get_directions(userlocation, machinelocation):
    key = os.environ.get("apikey")
    data = requests.get(
        f"https://api.openrouteservice.org/v2/directions/driving-car?api_key={key}&start={userlocation[0]},{userlocation[1]}&end={machinelocation[0]},{machinelocation[1]}"
    ).json()
    del data["metadata"]
    del data["type"]
    return data


def get_user_weekly_logs(userid):
    friday_last_week = timezone.now().date() - timedelta(days=7)
    friday_last_week = datetime.combine(friday_last_week, datetime.min.time())
    logs = RecycleLog.objects.filter(
        user=userid, created_at__gte=make_aware(friday_last_week)
    )

    total_points = logs.aggregate(Sum("points"))
    items = logs.aggregate(items=Sum(F("bottles") + F("cans")))["items"]

    return logs, total_points, items
