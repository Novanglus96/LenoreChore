from rest_framework import routers,serializers,viewsets
from .models import Area, Chore, HistoryItem, Option, CustomUser
from django.contrib.auth.models import User

class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ('area_name', 'area_bgcolor', 'area_textcolor')

class ChoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chore
        fields = ('chore_name', 'area', 'chore_type', 'active', 'dueDate', 'lastCompleted', 'intervalNumber', 'unit', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun', 'm_jan', 'm_feb', 'm_mar', 'm_apr', 'm_may', 'm_jun', 'm_jul', 'm_aug', 'm_sep', 'm_oct', 'm_nov', 'm_dec', 'effort', 'seasonal', 'assignee', 'vacationMode', 'vacationPause', 'vSeasonal')

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
        field = '__all__'
        extra_kwargs = {'password': {'write_only': True}}
