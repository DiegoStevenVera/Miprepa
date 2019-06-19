from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.relations import RelatedField
from django.db import models
from django.utils.translation import ugettext_lazy as _


class UidRelatedField(RelatedField):
    default_error_messages = {
        'required': _('This field is required.'),
        'does_not_exist': _('Invalid uid "{uid_value}" - object does not exist.'),
        'incorrect_type': _('Incorrect type. Expected char value, received {data_type}.'),
    }

    def __init__(self, **kwargs):
        self.representation_serializer = kwargs.pop("representation_serializer", None)
        super(UidRelatedField, self).__init__(**kwargs)

    def to_internal_value(self, data):
        pk = settings.HASHIDS.decode(data)
        pk = pk[0] if pk else None
        try:
            return self.get_queryset().get(pk=pk)
        except ObjectDoesNotExist:
            self.fail('does_not_exist', uid_value=data)
        except (TypeError, ValueError):
            self.fail('incorrect_type', data_type=type(data).__name__)

    def to_representation(self, value):
        if isinstance(value, models.Model):
            return self.representation_serializer(value, context=self.context).data \
                if self.representation_serializer else value.uid
        else:
            return value
