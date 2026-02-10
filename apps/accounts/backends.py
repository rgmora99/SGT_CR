from django.contrib.auth.models import User
from django.contrib.auth.backends import BaseBackend
from .services.ldap_service import authenticate_ldap

class LDAPBackend(BaseBackend):

    def authenticate(self, request, username=None, password=None):
        if not username or not password:
            return None

        ldap_user = authenticate_ldap(username, password)
        if not ldap_user:
            return None

        user, created = User.objects.get_or_create(
            username=username
        )

        user.first_name = ldap_user.get("first_name", "")
        user.last_name = ldap_user.get("last_name", "")
        user.email = ldap_user.get("email", "")
        user.is_active = True
        user.save()

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
