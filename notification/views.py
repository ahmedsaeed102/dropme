from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import NotificationSerializer, NotificationUpdateSerializer
from .models import Notification

class Notifications(GenericAPIView, ListModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin):
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = 'pk'

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

    def get(self, request, *args, **kwargs):
        if 'pk' in kwargs:
            return self.retrieve(request, *args, **kwargs)
        return self.list(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        if 'pk' in kwargs:
            notification = self.get_object()
            notification.is_read = True
            notification.save()
            return Response({'status': 'notification read'}, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        if 'pk' in kwargs:
            return self.destroy(request, *args, **kwargs)

class ReadNotifications(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = NotificationUpdateSerializer

    def post(self, request, *args, **kwargs):
        all_notifications = request.data.get('all_notifications', False)
        list_notifications = request.data.get('list_notifications', [])
        if all_notifications:
            Notification.objects.filter(user=request.user).update(is_read=True)
            return Response({'status': 'all notifications read'}, status=status.HTTP_200_OK)
        else:
            for notification_id in list_notifications:
                notification = Notification.objects.get(pk=notification_id)
                notification.is_read = True
                notification.save()
            return Response({'status': 'notifications read'}, status=status.HTTP_200_OK)

class DeleteNotifications(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = NotificationUpdateSerializer

    def post(self, request, *args, **kwargs):
        all_notifications = request.data.get('all_notifications', False)
        list_notifications = request.data.get('list_notifications', [])
        if all_notifications:
            Notification.objects.filter(user=request.user).delete()
            return Response({'status': 'all notifications deleted'}, status=status.HTTP_200_OK)
        else:
            Notification.objects.filter(pk__in=list_notifications).delete()
            return Response({'status': 'notifications deleted'}, status=status.HTTP_200_OK)