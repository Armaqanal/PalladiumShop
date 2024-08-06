from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q


class PalladiumBackend(ModelBackend):
    # def authenticate(self, request, username=None, password=None, **kwargs):
    #     User = get_user_model()
    #     try:
    #         user = User.objects.get(Q(username=username) | Q(email=username) | Q(phone=username))
    #         if user.check_password(password):
    #             return user
    #     except User.DoesNotExist:
    #         return None

    def authenticate(self, request, email=None, password=None, **kwargs):
        User = get_user_model()
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                return user
            else:
                print("Password check failed")
        except User.DoesNotExist:
            print("User does not exist")
        return None
