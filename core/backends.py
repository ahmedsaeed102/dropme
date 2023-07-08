from django.contrib.auth.backends import ModelBackend


class AuthBackend(ModelBackend):
    def user_can_authenticate(self, user):
        return True


def simple_jwt_authentication_rule(user):
    return user is not None
