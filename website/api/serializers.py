from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

from rest_framework import serializers

from flats.models import Project, AllFlatsLastPrice
from members.models import SelectedFlat


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('name', 'url')


class AllFlatsLastPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AllFlatsLastPrice
        fields = '__all__'


class SelectedFlatSerializer(serializers.ModelSerializer):
    class Meta:
        model = SelectedFlat
        fields = '__all__'


class UserReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'first_name', 'last_name', 'email')


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('username', 'first_name', 'last_name')


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('username', 'first_name', 'last_name', 'email', 'password')

    def validate_password(self, value):
        """
        Хэшируем пароль.
        """
        if 'password' not in value.lower():
            raise serializers.ValidationError()
        return make_password(value)
