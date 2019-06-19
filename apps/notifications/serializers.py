from django.utils.timezone import now
from rest_framework import serializers
from .models import Notification



class UpdateNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification

    def update(self, instance, validated_data):
        instance.seen_at = now()
        instance.save()
