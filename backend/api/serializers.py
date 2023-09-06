from rest_framework import routers,serializers,viewsets
from .models import Area, Chore, HistoryItem, Option

class AreaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Area
        fields = ('area_name', 'area_bgcolor', 'area_textcolor')

class ChoreSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Chore
        fields = ('chore_name', 'area', 'chore_type', 'active', 'dueDate', 'lastCompleted', 'intervalNumber', 'unit', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun', 'm_jan', 'm_feb', 'm_mar', 'm_apr', 'm_may', 'm_jun', 'm_jul', 'm_aug', 'm_sep', 'm_oct', 'm_nov', 'm_dec', 'assignee', 'effort', 'seasonal', 'vacationMode', 'vacationPause', 'vSeasonal')

class HistoryItemSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = HistoryItem
        fields = ('completed_date', 'completed_by', 'chore')

class OptionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Option
        fields = ('vacation_mode')