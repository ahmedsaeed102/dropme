#  active users , Average points per user , Total revenue (derived from recycled bottles and cans using static or dynamic pricing)
from users_api.models import UserModel
from django.core.cache import cache


def get_total_users():
	count = cache.get('total_users_count')
	if count is None :
		count = UserModel.objects.count()
		cache.set('total_users_count', count, timeout=60*60)
	return count