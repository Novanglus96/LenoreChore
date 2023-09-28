from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
from .serializers import AreaSerializer, ChoreSerializer, HistoryItemSerializer, OptionSerializer, CustomUserSerializer, UserLoginSerializer, HistoryItemCreateSerializer, ChoreCompleteSerializer, ChoreSnoozeSerializer
from .models import Area, Chore, HistoryItem, Option, CustomUser
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta

# Create your views here.

def index(request):
    return HttpResponse("Hello, world. You're at the API.")

class AreaView(viewsets.ModelViewSet):
    serializer_class = AreaSerializer
    queryset = Area.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering_fields = '__all__'
    ordering = ['area_name']

class ChoreView(viewsets.ModelViewSet):
    serializer_class = ChoreSerializer
    queryset = Chore.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering_fields = '__all__'
    ordering = ['nextDue']

class HistoryItemView(viewsets.ModelViewSet):
    serializer_class = HistoryItemSerializer
    queryset = HistoryItem.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering_fields = '__all__'
    ordering = ['-completed_date','-id']
    
    @action(detail=False, methods=['GET'])
    def weekly_totals(self, request):
        # Define the days of the week
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        # Get a list of all CustomUser objects
        users = CustomUser.objects.all()

        # Initialize the result list
        result = []

        # Loop through each user
        for user in users:
            user_data = {
                "label": user.first_name,
                "data": [0] * 7  # Initialize data with zeros for each day of the week
            }

            # Get history items for the user
            history_items = HistoryItem.objects.filter(completed_by=user)

            # Calculate totals for each day of the week
            for day_index, day in enumerate(days_of_week):
                # Calculate the date for the current day of the week
                today = datetime.now()
                day_offset = today.weekday() - day_index
                target_date = today - timedelta(days=day_offset)

                # Filter history items for the current day
                day_total = history_items.filter(completed_date=target_date).count()

                # Update the user's data with the total for the current day
                user_data["data"][day_index] = day_total

            # Append the user's data to the result list
            result.append(user_data)

        return Response(result)
    
    @action(detail=False, methods=['GET'])
    def last_3_completed_for_chore(self, request):
        chore_id = request.query_params.get('chore_id')

        # Check if chore_id is provided in the query parameters
        if not chore_id:
            return Response({'detail': 'chore_id is required as a query parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        # Get the last 3 completed history items for the specified chore
        history_items = HistoryItem.objects.filter(chore_id=chore_id).order_by('-completed_date')[:3]

        # Serialize the history items
        serializer = HistoryItemSerializer(history_items, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

class OptionView(viewsets.ModelViewSet):
    serializer_class = OptionSerializer
    queryset = Option.objects.all()

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()
    
    @action(detail=False, methods=['POST'])
    def login(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)

                # Retrieve or create a token for the authenticated user
                token, _ = Token.objects.get_or_create(user=user)

                return Response({'token': token.key, 'firstname':  user.first_name, 'lastname': user.last_name, 'email': user.email, 'isAdmin': user.is_superuser, 'male': user.male, 'id': user.id, 'detail': 'Login successful'}, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def logout(self, request):
        # Log the user out
        logout(request)
        return Response({'detail': 'Logout successful'}, status=status.HTTP_200_OK)

class HistoryItemCreateViewSet(viewsets.ViewSet):
    def create(self, request):
        serializer = HistoryItemCreateSerializer(data=request.data)

        if serializer.is_valid():
            history_item = serializer.save()
            # Customize the response as needed
            return Response(
                {'message': 'HistoryItem created successfully', 'id': history_item.id},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChoreCompleteViewSet(viewsets.ModelViewSet):
    queryset = Chore.objects.all()
    serializer_class = ChoreCompleteSerializer
    
    def perform_update(self, serializer):
        if 'lastCompleted' not in self.request.data:
            serializer.validated_data['lastCompleted'] = date.today()
            
        # Use the object's intervalNumber and unit to calculate nextDue
        interval_number = serializer.instance.intervalNumber
        unit = serializer.instance.unit

        if interval_number and unit:
            if unit == 'day(s)':
                serializer.validated_data['nextDue'] = date.today() + timedelta(days=interval_number)
            elif unit == 'week(s)':
                serializer.validated_data['nextDue'] = date.today() + timedelta(weeks=interval_number)
            elif unit == 'month(s)':
                serializer.validated_data['nextDue'] = date.today() + relativedelta(months=interval_number)
            elif unit == 'year(s)':
                serializer.validated_data['nextDue'] = date.today() + relativedelta(years=interval_number)
        
        serializer.validated_data['assignee'] = None
        
        serializer.save()

class ChoreSnoozeViewSet(viewsets.ViewSet):
    def partial_update(self, request, pk=None):
        chore = Chore.objects.get(pk=pk)

        serializer = ChoreSnoozeSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            next_due_date = serializer.validated_data.get('next_due_date')
            snooze_days = serializer.validated_data.get('snooze_days')

            if next_due_date:
                chore.nextDue = next_due_date
            elif snooze_days:
                chore.nextDue += timedelta(days=snooze_days)
            
            chore.save()
            return Response({'message': 'Chore snoozed successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
