from rest_framework import routers,serializers,viewsets
from .models import Area, Chore, HistoryItem, Option, CustomUser
from django.contrib.auth.models import User

class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = '__all__'

class ChoreSerializer(serializers.ModelSerializer):
    duedays = serializers.IntegerField(required=False)
    dirtiness = serializers.IntegerField(required=False)
    class Meta:
        model = Chore
        fields = '__all__'
        
class HistoryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoryItem
        fields = ('completed_date', 'completed_by', 'chore')

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = '__all__'

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

class UserLogoutSerializer(serializers.Serializer):
    pass
