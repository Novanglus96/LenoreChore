from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
from .serializers import AreaSerializer, ChoreSerializer, HistoryItemSerializer, OptionSerializer, CustomUserSerializer, UserLoginSerializer
from .models import Area, Chore, HistoryItem, Option, CustomUser
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

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
    ordering = ['completed_date']

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
