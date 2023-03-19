import requests
from users_api.models import UserModel
from channels.db import database_sync_to_async


@database_sync_to_async
def update_user_points(user_pk, points):
    user = UserModel.objects.get(pk=user_pk)
    user.total_points += points
    user.save()
    for competion in user.comp_user.all():
        if competion.is_ongoing:
            rank = competion.competitionranking_set.get(competition=competion.pk, user=user_pk)
            rank.points += points
            rank.save()

def claculate_travel_distance_and_time(userlocation, machinelocation):
    data={}
    timebyfoot = requests.get(
            f'https://routing.openstreetmap.de/routed-foot/route/v1/driving/{userlocation[0]},{userlocation[1]};{machinelocation[0]},{machinelocation[1]}'
        ).json()
    
    timebycar = requests.get(
            f'https://routing.openstreetmap.de/routed-car/route/v1/driving/{userlocation[0]},{userlocation[1]};{machinelocation[0]},{machinelocation[1]}'
        ).json()
    
    timebybike = requests.get(
            f'https://routing.openstreetmap.de/routed-bike/route/v1/driving/{userlocation[0]},{userlocation[1]};{machinelocation[0]},{machinelocation[1]}'
        ).json()
    
    data['distance'] = timebyfoot['routes'][0]['distance']
    data['timebyfoot'] = timebyfoot['routes'][0]['duration'] / 60
    data['timebycar'] = timebycar['routes'][0]['duration'] / 60
    data['timebybike'] = timebybike['routes'][0]['duration'] / 60

    return data