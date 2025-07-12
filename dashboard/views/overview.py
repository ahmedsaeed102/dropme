from dashboard.services.overview import get_overview_data
from rest_framework.views import APIView
from rest_framework.response import Response

class Overview(APIView):
	"""
	API view to get the overview data for the dashboard.
	"""

	def get(self, request):
		"""
		Handle GET requests to retrieve overview data.
		"""
		overview = get_overview_data()
		return Response(overview, status=200)





