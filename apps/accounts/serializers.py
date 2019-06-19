# coding=utf-8
from django.contrib.auth import authenticate
from push_notifications.models import GCMDevice
from requests import HTTPError
from rest_framework import serializers
from rest_framework_jwt.serializers import JSONWebTokenSerializer, jwt_payload_handler, jwt_encode_handler
from django.utils.translation import ugettext_lazy as _
from apps.universities.models import University, KnowledgeArea
from apps.universities.serializers import KnowledgeAreaSerializer, UniversitySerializer
from miprepa.utils.fields import UidRelatedField
from .models import User, UserUniversity
from ..badges.models import Level
from ..badges.serializers import SerializerLevelInProfile, BadgeSerializer


class OwnJSONWebTokenSerializer(JSONWebTokenSerializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    @property
    def username_field(self):
        return 'email'

    def validate(self, attrs):
        credentials = {
            self.username_field: attrs.get(self.username_field),
            'password': attrs.get('password')
        }

        if all(credentials.values()):
            user = authenticate(**credentials)

            if user:
                if not user.is_active:
                    msg = _('User account is disabled.')
                    raise serializers.ValidationError(msg)

                payload = jwt_payload_handler(user)

                return {
                    'token': jwt_encode_handler(payload),
                    'user': user
                }
            else:
                msg = _('Unable to login with provided credentials.')
                raise serializers.ValidationError(msg)
        else:
            msg = _('Must include "{username_field}" and "password".')
            msg = msg.format(username_field=self.username_field)
            raise serializers.ValidationError(msg)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('uid', 'first_name', 'last_name', 'nickname', 'email', 'gender', 'birthday', 'photo', 'is_new')
        read_only_fields = ('email', 'is_new', 'nickname')


class RegisterUserSerializer(serializers.ModelSerializer):
    access_token = serializers.CharField(required=False, max_length=500)
    password = serializers.CharField(required=False)
    gender = serializers.ChoiceField(choices=[(item.name, item.value) for item in User.Gender])

    class Meta:
        model = User
        fields = ('uid', 'first_name', 'last_name', 'password', 'nickname', 'email', 'gender',
                  'birthday', 'access_token')
        write_only_fields = ('password', 'access_token')

    def clean_password(self):
        if len(self.cleaned_data.get('password')) < 6:
            raise serializers.ValidationError(u"Mínimo 6 caracteres")
        else:
            return self.cleaned_data.get('password')

    def create(self, validated_data):
        user = User(first_name=validated_data.get('first_name'), last_name=validated_data.get('last_name'),
                    email=validated_data.get('email'), nickname=validated_data.get('nickname'),
                    gender=validated_data.get('gender'), birthday=validated_data.get('birthday'), )
        user.set_password(validated_data.get('password'))
        user.save()
        return user


class FacebookLoginSerializer(serializers.Serializer):
    access_token = serializers.CharField(error_messages={"blank": "Este campo es obligatorio"})

    def validate(self, attrs):
        request = self.context.get("request")
        try:
            user = request.backend.do_auth(attrs.get("access_token"))
            payload = jwt_payload_handler(user)
            return {
                "token": jwt_encode_handler(payload),
                "user": user
            }
        except HTTPError as ex:
            raise serializers.ValidationError("Invalid facebook token")


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(error_messages={"blank": "Este campo es obligatorio"})
    password = serializers.CharField(error_messages={"blank": "Este campo es obligatorio"})

    def validate(self, attrs):
        self.user_cache = authenticate(username=attrs["username"], password=attrs["password"])
        if not self.user_cache:
            raise serializers.ValidationError("Invalid login")
        return attrs

    def get_user(self):
        return self.user_cache


class UserFollowSerializer(serializers.Serializer):
    uid_user = UidRelatedField(queryset=User.objects.all())


class UserInListFollowSerializer(serializers.ModelSerializer):
    image_level = serializers.SerializerMethodField(read_only=True)
    experience = serializers.SerializerMethodField(read_only=True)

    def get_experience(self, obj):
        return obj.user_universities.filter(desired_university=self.context.get('uu')).first().experience

    def get_image_level(self, obj):
        user_university = obj.user_universities.filter(desired_university=self.context.get('uu')).first()
        level = Level.objects.filter(is_enabled=True, min_experience__lte=user_university.experience,
                                     max_experience__gte=user_university.experience).first()
        if level:
            return SerializerLevelInProfile(level, context=self.context).data
        else:
            return None

    class Meta:
        model = User
        fields = ('uid', 'first_name', 'last_name', 'nickname', 'image_level', 'experience')


class UserSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('uid', 'first_name', 'last_name', 'nickname', 'photo')


class UserUniversitySearchSerializer(serializers.ModelSerializer):
    user = UserSearchSerializer(read_only=True)
    image_level = serializers.SerializerMethodField(read_only=True)

    def get_image_level(self, obj):
        level = Level.objects.filter(is_enabled=True, min_experience__lte=obj.experience,
                                     max_experience__gte=obj.experience).first()
        if level:
            return SerializerLevelInProfile(level, context=self.context).data
        else:
            return None

    class Meta:
        model = UserUniversity
        fields = ('uid', 'user', 'image_level', 'experience')


# class UpdateUserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ('first_name', 'last_name', 'password', 'photo', 'gender', 'birthday')
#         write_only_fields = ('password',)
#
#     def update(self, instance, validated_data):
#         instance.first_name = validated_data.get('first_name', instance.first_name)
#         instance.last_name = validated_data.get('last_name', instance.last_name)
#         instance.gender = validated_data.get('gender', instance.gender)
#         instance.birthday = validated_data.get('birthday', instance.birthday)
#         # instance.professional_career = validated_data.get('professional_career', instance.professional_career)
#         if validated_data.get('password'):
#             instance.set_password(validated_data.get('password'))
#         instance.photo = validated_data.get('photo', instance.photo)
#         instance.save()
#         return instance


class GCMDeviceSerializer(serializers.ModelSerializer):
    registration_id = serializers.CharField()
    device_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate_registration_id(self, attr):
        user = getattr(self.context.get("request"), "user")
        if self.Meta.model.objects.filter(registration_id=attr, user=user):
            raise serializers.ValidationError("El usuario ya registró este dispositivo")
        return attr

    class Meta:
        model = GCMDevice
        fields = ("id", "name", "date_created", "device_id", "registration_id")


class ValidateUserDataSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    nickname = serializers.CharField(required=False)

    def validate_email(self, email):
        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Este email ya fue registrado")
        return email

    def validate_nickname(self, nickname):
        if nickname and User.objects.filter(nickname=nickname).exists():
            raise serializers.ValidationError("Este nickname ya fue registrado")
        return nickname

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError("Se debe especificar al menos un campo para validar")
        return attrs


class RetrievePasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    def validate_email(self, email):
        if email and User.objects.filter(email=email).exists():
            return email
        raise serializers.ValidationError("Este no es un email registrado :(")


class UserUniversitySerializer(serializers.ModelSerializer):
    desired_university = UniversitySerializer(read_only=True, required=False)
    # user = UserSerializer(read_only=True, required=False)
    level = serializers.SerializerMethodField(read_only=True)
    knowledge_area = KnowledgeAreaSerializer(read_only=True)
    has_knowledge_area = serializers.SerializerMethodField(read_only=True)
    count_follows = serializers.SerializerMethodField(read_only=True)
    count_badges = serializers.SerializerMethodField(read_only=True)

    def get_count_badges(self, obj):
        return len(obj.badges.all())

    def get_count_follows(self, obj):
        return len(obj.follows) if obj.follows else 0

    def get_has_knowledge_area(self, obj):
        return True if obj.knowledge_area else False

    def get_level(self, obj):
        level = Level.objects.filter(is_enabled=True, min_experience__lte=obj.experience,
                                     max_experience__gte=obj.experience).first()
        if level:
            return SerializerLevelInProfile(level, context=self.context).data
        else:
            return None

    class Meta:
        model = UserUniversity
        fields = ('uid', 'desired_university', 'first_option', 'level', 'experience', 'count_follows',
                  'knowledge_area', 'has_knowledge_area', 'count_badges',)
        read_only_fields = ('desired_university', 'knowledge_area', 'experience', 'count_follows', 'level',
                            'first_option')


class RetrieveUserUniversitySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True, required=False)
    level = serializers.SerializerMethodField(read_only=True)
    has_knowledge_area = serializers.SerializerMethodField(read_only=True)
    count_follows = serializers.SerializerMethodField(read_only=True)
    count_badges = serializers.SerializerMethodField(read_only=True)
    # badges = BadgeSerializer(read_only=True, many=True)

    def get_count_badges(self, obj):
        return len(obj.badges.all())

    def get_count_follows(self, obj):
        return len(obj.follows) if obj.follows else 0

    def get_has_knowledge_area(self, obj):
        return True if obj.knowledge_area else False

    def get_level(self, obj):
        level = Level.objects.filter(is_enabled=True, min_experience__lte=obj.experience,
                                     max_experience__gte=obj.experience).first()
        if level:
            return SerializerLevelInProfile(level, context=self.context).data
        else:
            return None

    class Meta:
        model = UserUniversity
        fields = ('uid', 'user', 'first_option', 'level', 'experience', 'count_follows', 'has_knowledge_area',
                  'count_badges')


class CreateUserUniversitySerializer(serializers.ModelSerializer):
    desired_university = UidRelatedField(queryset=University.objects.filter(is_enabled=True))

    class Meta:
        model = UserUniversity
        fields = ('desired_university',)


class UpdateUserUniversitySerializer(serializers.ModelSerializer):
    knowledge_area = UidRelatedField(queryset=KnowledgeArea.objects.filter(is_enabled=True))

    class Meta:
        model = UserUniversity
        fields = ('knowledge_area', 'first_option')
