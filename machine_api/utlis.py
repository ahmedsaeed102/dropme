import requests
import os
from datetime import timedelta, datetime
from django.db.models import Sum
from django.utils import timezone
from django.utils.timezone import make_aware
from rest_framework.exceptions import APIException
from users_api.services import user_get
from marketplace.services import special_offer_apply
from .models import RecycleLog


def update_user_points(user_pk, points):
    user = user_get(id=user_pk)
    special_points = special_offer_apply(user=user, points=points)

    user.total_points += points + special_points
    user.save()

    for competion in user.comp_user.all():  # refactor
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

    return data


bottle_point = int
can_point = int
total_point = int

def calculate_points(bottles: int, cans: int) -> tuple[bottle_point, can_point, total_point]:
    bottles_points = bottles * 2
    cans_points = cans * 4
    total_points = bottles_points + cans_points
    return bottles_points, cans_points, total_points


def calculate_co2_energy(bottles: int, cans: int) -> dict:
    bottles_co2 = round(bottles * 0.8, 2)
    cans_co2 = round(cans * 0.15, 2)
    bottles_energy = round(bottles * 0.06, 2)
    cans_energy = round(cans * 0.09, 2)
    return {
        "bottles_co2": bottles_co2,
        "cans_co2": cans_co2,
        "bottles_energy": bottles_energy,
        "cans_energy": cans_energy,
    }

def get_total_recycled_items(userid: int) -> int:
    user_recycle_logs = RecycleLog.objects.filter(user=userid)
    total_bottles = user_recycle_logs.aggregate(Sum("bottles"))["bottles__sum"]
    total_cans = user_recycle_logs.aggregate(Sum("cans"))["cans__sum"]
    return total_bottles + total_cans if total_bottles and total_cans else 0

def get_user_weekly_logs(userid: int) -> dict:
    friday_last_week = timezone.now().date() - timedelta(days=7)
    friday_last_week = datetime.combine(friday_last_week, datetime.min.time())
    logs = RecycleLog.objects.filter(user=userid, created_at__gte=make_aware(friday_last_week))
    if not logs:
        return {"recycled": False}

    total_bottles = logs.aggregate(Sum("bottles"))["bottles__sum"]
    total_cans = logs.aggregate(Sum("cans"))["cans__sum"]
    bottles_points, cans_points, total_points = calculate_points(total_bottles, total_cans)
    co2_energy = calculate_co2_energy(total_bottles, total_cans)

    data = {
        "recycled": True,
        "bottles_number": total_bottles,
        "bottles_points": bottles_points,
        "cans_number": total_cans,
        "cans_points": cans_points,
        "total_points": total_points,
    }
    data.update(co2_energy)
    return data