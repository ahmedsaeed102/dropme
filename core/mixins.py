from rest_framework.permissions import IsAuthenticated, IsAdminUser


class AdminOrReadOnlyPermissionMixin:
    def get_permissions(self):
        self.action = self.request.method

        if (
            self.action.lower() == "put"
            or self.action.lower() == "patch"
            or self.action.lower() == "post"
            or self.action.lower() == "delete"
        ):
            return [IsAdminUser()]

        return [IsAuthenticated()]
