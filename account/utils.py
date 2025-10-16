from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import text_type
from django.core.serializers.python import Serializer
from django.conf import settings

url = settings.BASE_URL


class AppTokenGenerator(PasswordResetTokenGenerator):

    def _make_hash_value(self, user, timestamp):
        return (text_type(user.is_active)+text_type(user.pk)+text_type(timestamp))


account_activation_token = AppTokenGenerator()


class LazyAccountEncoder(Serializer):
    def get_dump_object(self, obj):
        dump_object = {}
        dump_object.update({'id': str(obj.id)})
        dump_object.update({'email': str(obj.email)})
        dump_object.update({'username': str(obj.username)})
        dump_object.update(
            {'profile_image': f'{url}{str(obj.profile_image.url)}'})
        return dump_object
