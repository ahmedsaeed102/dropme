from rest_framework.permissions import IsAuthenticated, IsAdminUser


class GetPermissionsMixin:
    def get_permissions(self):
        self.action = self.request.method

        if (
            self.action.lower() == "put"
            or self.action.lower() == "patch"
            or self.action.lower() == "post"
        ):
            return [IsAdminUser()]

        return [IsAuthenticated()]
