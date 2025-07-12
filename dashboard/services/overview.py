#  active users , Average points per user , Total revenue (derived from recycled bottles and cans using static or dynamic pricing)
from users_api.models import UserModel
from django.core.cache import cache
from django.db.models import Sum


def get_total_users():
	count = cache.get('total_users_count')
	if count is None :
		count = UserModel.objects.count()
		cache.set('total_users_count', count, timeout=60*60) # Cache for 1 hour
	return count


def get_active_users():
	count = cache.get('total_users_count')
	if count is None:
		count = UserModel.objects.filter(is_active=True).count()
		cache.set('total_users_count', count, timeout=60 * 60)
	return count

def get_total_points():
	total_points= cache.get('total_points_sum')
	if total_points is None:
		total_points= UserModel.objects.aggregate(total_points_sum=Sum('total_points'))['total_points_sum'] or 0
		cache.set('total_points_sum', total_points, timeout=60*60)
	return total_points

def get_average_points_per_user():
	total_points = get_total_points()
	total_users = get_total_users()
	if total_users == 0:
		return 0
	average_points = total_points / total_users
	return average_points

def get_total_revenue():
	pass # This function would need to be implemented based on how revenue is calculated from recycled bottles and cans.

def get_overview_data():
	overview_data = {
		'total_users': get_total_users(),
		'active_users': get_active_users(),
		'total_points': get_total_points(),
		'average_points_per_user': get_average_points_per_user(),
		# 'total_revenue': get_total_revenue(), # un implemented
	}
	return overview_data