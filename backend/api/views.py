from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.parsers import JSONParser
from django.views.decorators.csrf import csrf_exempt
#from .serializers import TaskSerializer
#from .models import Task

# Create your views here.

def index(request):
    return HttpResponse("Hello, world. You're at the API.")