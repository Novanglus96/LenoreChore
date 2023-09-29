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
    last_three_history_items = serializers.SerializerMethodField()
    
    class Meta:
        model = Chore
        fields = ('id', 'chore_name', 'area', 'active', 'nextDue', 'lastCompleted', 'intervalNumber', 'unit', 'm_jan', 'm_feb', 'm_mar', 'm_apr', 'm_may', 'm_jun', 'm_jul', 'm_aug', 'm_sep', 'm_oct', 'm_nov', 'm_dec', 'assignee', 'effort', 'vacationPause', 'expand', 'dirtiness', 'duedays', 'last_three_history_items')
    
    def get_last_three_history_items(self, instance):
        # Get the last three HistoryItem objects related to the Chore
        history_items = HistoryItem.objects.filter(chore=instance).order_by('-completed_date')[:3]
        
        # Serialize the 'completed_date' and 'completed_by.fullname' fields
        history_items_data = [{'completed_date': item.completed_date, 'completed_by': item.completed_by.fullname} for item in history_items]
        
        return history_items_data
    
class HistoryItemSerializer(serializers.ModelSerializer):
    chore = ChoreSerializer(required=False, allow_null=True)
    completed_by = CustomUserSerializer(required=False, allow_null=True)
    class Meta:
        model = HistoryItem
        fields = '__all__'
        
class HistoryItemCreateSerializer(serializers.Serializer):
    chore_id = serializers.PrimaryKeyRelatedField(
        queryset=Chore.objects.all(),
        required=True,
        allow_null=False
    )
    completed_by_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        required=True,
        allow_null=False
    )

    def create(self, validated_data):
        chore_id = validated_data['chore_id']
        completed_by_id = validated_data['completed_by_id']

        # Create a new HistoryItem using the provided chore and user IDs
        history_item = HistoryItem.objects.create(
            chore=chore_id,
            completed_by=completed_by_id,
            # Set other fields as needed
        )
        return history_item
    
class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = '__all__'

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

class UserLogoutSerializer(serializers.Serializer):
    pass

class ChoreCompleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chore
        fields = ['lastCompleted']
        
class ChoreSnoozeSerializer(serializers.Serializer):
    next_due_date = serializers.DateField(required=False)
    snooze_days = serializers.IntegerField(required=False)
        