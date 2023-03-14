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