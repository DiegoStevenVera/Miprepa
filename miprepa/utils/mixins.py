from django.conf import settings


class UidMixin:
    @property
    def uid(self):
        return settings.HASHIDS.encode(self.id)
