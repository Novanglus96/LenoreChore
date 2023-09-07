from django.http import HttpResponse
from rest_framework import viewsets
from .serializers import AreaSerializer, ChoreSerializer, HistoryItemSerializer, OptionSerializer
from .models import Area, Chore, HistoryItem, Option

# Create your views here.

def index(request):
    return HttpResponse("Hello, world. You're at the API.")

class AreaView(viewsets.ModelViewSet):
    serializer_class = AreaSerializer
    queryset = Area.objects.all()

class ChoreView(viewsets.ModelViewSet):
    serializer_class = ChoreSerializer
    queryset = Chore.objects.all()

class HistoryItemView(viewsets.ModelViewSet):
    serializer_class = HistoryItemSerializer
    queryset = HistoryItem.objects.all()

class OptionView(viewsets.ModelViewSet):
    serializer_class = OptionSerializer
    queryset = Option.objects.all()
