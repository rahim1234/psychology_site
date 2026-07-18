from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class PhoneNumberBackend(ModelBackend):
    """Authenticate using phone number + password instead of username + password."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        phone_number = kwargs.get('phone_number', username)
        if not phone_number or not password:
            return None
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(phone_number=phone_number)
        except UserModel.DoesNotExist:
            # Run the hasher anyway to keep response timing similar whether
            # or not the account exists.
            UserModel().set_password(password)
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
