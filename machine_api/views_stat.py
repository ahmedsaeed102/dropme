from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_api_key.permissions import HasAPIKey
from django.utils.timezone import now
from datetime import timedelta
from django.db.models import Count, Sum
from django.db.models.functions import TruncDay

from rest_framework.response import Response
from machine_api.models import Machine, RecycleLog

class MachineOverview(APIView):
    # permission_classes = [HasAPIKey | IsAuthenticated]

    def get(self, request, name):
        try:
            machine = Machine.objects.get(identification_name=name)
            thirty_days_ago = now() - timedelta(days=30)
            recycle_logs_last_30_days = RecycleLog.objects.filter(machine=machine,created_at__gte=thirty_days_ago)

            daily_data = recycle_logs_last_30_days.annotate(day=TruncDay('created_at')).values('day').annotate(
                unique_users=Count('user', distinct=True),
                total_cans=Sum('cans'),
                total_bottles=Sum('bottles'),
                total_recycled_items=Sum('cans') + Sum('bottles')
            ).order_by('day')

            all_days = {
                (thirty_days_ago + timedelta(days=i)).date(): {
                    "unique_users": 0,
                    "total_cans": 0,
                    "total_bottles": 0,
                    "total_recycled_items": 0,
                }
                for i in range(30)
            }

            for entry in daily_data:
                day = entry["day"].date()
                if day in all_days:
                    all_days[day]["unique_users"] = entry["unique_users"] or 0
                    all_days[day]["total_cans"] = entry["total_cans"] or 0
                    all_days[day]["total_bottles"] = entry["total_bottles"] or 0
                    all_days[day]["total_recycled_items"] = entry["total_recycled_items"] or 0

            response_data = [
                {
                    "title": "Users",
                    "value": sum(d["unique_users"] for d in all_days.values()),
                    "interval": "Last 30 days",
                    "trend": "up",
                    "data": [d["unique_users"] for d in all_days.values()],
                },
                {
                    "title": "Bottles",
                    "value": sum(d["total_bottles"] for d in all_days.values()),
                    "interval": "Last 30 days",
                    "trend": "up",
                    "data": [d["total_bottles"] for d in all_days.values()],
                },
                {
                    "title": "Cans",
                    "value": sum(d["total_cans"] for d in all_days.values()),
                    "interval": "Last 30 days",
                    "trend": "up",
                    "data": [d["total_cans"] for d in all_days.values()],
                },
                {
                    "title": "Total Items",
                    "value": sum(d["total_recycled_items"] for d in all_days.values()),
                    "interval": "Last 30 days",
                    "trend": "up",
                    "data": [d["total_recycled_items"] for d in all_days.values()],
                }
            ]
            return Response(response_data, status=200)
        except Machine.DoesNotExist:
            return Response({"error": "Machine not found"}, status=404)