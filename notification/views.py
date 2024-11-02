from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import NotificationSerializer
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
