from rest_framework import routers,serializers,viewsets
from .models import Area, Chore, HistoryItem, Option, CustomUser
from django.contrib.auth.models import User
from drf_writable_nested.serializers import WritableNestedModelSerializer

class CustomUserSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField(required=False)
    class Meta:
        model = CustomUser
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}
        
class AreaSerializer(serializers.ModelSerializer):
    dirtiness = serializers.IntegerField(required=False, read_only=True)
    dueCount = serializers.IntegerField(required=False, read_only=True)
    class Meta:
        model = Area
        fields = '__all__'

class ChoreSerializer(WritableNestedModelSerializer, serializers.ModelSerializer):
    duedays = serializers.IntegerField(required=False)
    dirtiness = serializers.IntegerField(required=False)
    area = AreaSerializer(required=False, allow_null=True)
    assignee = CustomUserSerializer(required=False, allow_null=True)
    
    class Meta:
        model = Chore
        fields = ('id', 'chore_name', 'area', 'active', 'nextDue', 'lastCompleted', 'intervalNumber', 'unit', 'm_jan', 'm_feb', 'm_mar', 'm_apr', 'm_may', 'm_jun', 'm_jul', 'm_aug', 'm_sep', 'm_oct', 'm_nov', 'm_dec', 'assignee', 'effort', 'vacationPause', 'expand', 'dirtiness', 'duedays')
        
class HistoryItemSerializer(serializers.ModelSerializer):
    chore = ChoreSerializer()
    completed_by = CustomUserSerializer()
    class Meta:
        model = HistoryItem
        fields = ('completed_date', 'completed_by', 'chore')

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = '__all__'

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

class UserLogoutSerializer(serializers.Serializer):
    pass
