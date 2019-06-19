from django.conf import settings
from rest_framework.generics import UpdateAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from apps.notifications.models import Notification
from apps.notifications.serializers import UpdateNotificationSerializer


class UpdateNotificationAPI(UpdateAPIView):
    """{Gender: m | f | b}"""
    permission_classes = (IsAuthenticated,)
    serializer_class = UpdateNotificationSerializer

    def get_object(self):
        uid = self.kwargs.get("uid")
        decoded = settings.HASHIDS.decode(uid)
        id = decoded[0] if decoded else None
        return get_object_or_404(Notification.objects.all(), id=id)
