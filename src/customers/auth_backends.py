# from django.contrib.auth import get_user_model
# from django.contrib.auth.backends import ModelBackend
# from django.db.models import Q
#
#
# class PalladiumBackend(ModelBackend):
#     def authenticate(self, request, username=None, password=None, **kwargs):
#         User = get_user_model()
#         try:
#             user = User.objects.get(Q(username=username) | Q(email=username) | Q(phone=username))
#             if user.check_password(password):
#                 return user
#         except User.DoesNotExist:
#             return None

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class PalladiumBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = User.objects.filter(phone=email).first()

        if user and user.check_password(password):
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
