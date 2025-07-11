import requests
import os
from datetime import timedelta, datetime
from django.db.models import Sum
from django.utils import timezone
from django.utils.timezone import make_aware
from rest_framework.exceptions import APIException
from users_api.services import user_get
# from marketplace.services import special_offer_apply
from .models import RecycleLog
from competition_api.models import CompetitionRanking

# def update_user_points(user_pk, points):
#     user = user_get(id=user_pk)
#     special_points = special_offer_apply(user=user, points=points)
#     if CompetitionRanking.objects.filter(user=user):
#         competition_ranking = CompetitionRanking.objects.filter(user=user).first()
#         if competition_ranking.competition.is_ongoing:
#             competition_ranking.points += points + special_points
#             competition_ranking.save()
#         else:
#             user.total_points += points + special_points
#             user.save()
#     else:
#         user.total_points += points + special_points
#         user.save()

def claculate_travel_distance(userlocation, machinelocation):
    timebyfoot = requests.get(f"https://routing.openstreetmap.de/routed-foot/route/v1/driving/{userlocation[0]},{userlocation[1]};{machinelocation[0]},{machinelocation[1]}").json()
    return timebyfoot["routes"][0]["distance"] if timebyfoot.get("routes") else 0

def claculate_travel_distance_and_time(userlocation, machinelocation):
    data = {}
    timebyfoot = requests.get(f"https://routing.openstreetmap.de/routed-foot/route/v1/driving/{userlocation[0]},{userlocation[1]};{machinelocation[0]},{machinelocation[1]}").json()
    timebycar = requests.get(f"https://routing.openstreetmap.de/routed-car/route/v1/driving/{userlocation[0]},{userlocation[1]};{machinelocation[0]},{machinelocation[1]}").json()
    timebybike = requests.get(f"https://routing.openstreetmap.de/routed-bike/route/v1/driving/{userlocation[0]},{userlocation[1]};{machinelocation[0]},{machinelocation[1]}").json()
    timebymotorcycle = requests.get(f"https://routing.openstreetmap.de/routed-car/route/v1/driving/{userlocation[0]},{userlocation[1]};{machinelocation[0]},{machinelocation[1]}").json()

    data["distance"] = timebyfoot["routes"][0]["distance"] if timebyfoot.get("routes") else 0
    data["timebyfoot"] = timebyfoot["routes"][0]["duration"] / 60 if timebyfoot.get("routes") else 0
    data["timebycar"] = timebycar["routes"][0]["duration"] / 60 if timebycar.get("routes") else 0
    data["timebybike"] = timebybike["routes"][0]["duration"] / 60 if timebybike.get("routes") else 0
    data["timebymotorcycle"] = timebymotorcycle["routes"][0]["duration"] / 60 if timebymotorcycle.get("routes") else 0

    return data

def get_directions(userlocation, machinelocation):
    key = os.environ.get("apikey")
    data = requests.get(f"https://api.openrouteservice.org/v2/directions/driving-car?api_key={key}&start={userlocation[0]},{userlocation[1]}&end={machinelocation[0]},{machinelocation[1]}").json()
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
    if not user_recycle_logs:
        return 0
    total_bottles = user_recycle_logs.aggregate(Sum("bottles"))["bottles__sum"]
    total_cans = user_recycle_logs.aggregate(Sum("cans"))["cans__sum"]
    print("recycled items:", total_bottles, total_cans)
    user = user_get(id=userid)
    if user.phone_number:
        phone_recycle_logs = RecycleLog.objects.filter(phone__phone_number=user.phone_number)
        if phone_recycle_logs:
            print(phone_recycle_logs)
            print("phone recycled items:", phone_recycle_logs.aggregate(Sum("bottles"))["bottles__sum"], phone_recycle_logs.aggregate(Sum("cans"))["cans__sum"])
            total_bottles += phone_recycle_logs.aggregate(Sum("bottles"))["bottles__sum"]
            total_cans += phone_recycle_logs.aggregate(Sum("cans"))["cans__sum"]
    return total_bottles + total_cans

def get_user_logs(userid: int) -> dict:
    logs = RecycleLog.objects.filter(user=userid)
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
    }
    data.update(co2_energy)
    return data

def get_remaining_points(user):
    competition_ranking = CompetitionRanking.objects.filter(user=user).first()
    if competition_ranking:
        remaining_points = competition_ranking.competition.target - competition_ranking.points
        if remaining_points > 0:
            return remaining_points
    return 0