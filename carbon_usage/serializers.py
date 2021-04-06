from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UsageType, Usage


class UserSerializer(serializers.ModelSerializer):

    usage = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Usage.objects.all())

    class Meta:
        model = User
        fields = ['id', 'username', 'usage']


class UsageTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsageType
        fields = ['name', 'unit', 'id']


class UsageSerializer(serializers.ModelSerializer):
    user = serializers.CharField(read_only=True, source='user.username')

    class Meta:
        model = Usage
        fields = ['user', 'usage_type', 'usage_at', 'id']
