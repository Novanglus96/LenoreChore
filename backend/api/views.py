from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.parsers import JSONParser
from django.views.decorators.csrf import csrf_exempt
from .serializers import AreaSerializer, ChoreSerializer, HistoryItemSerializer, OptionSerializer
from .models import Area, Chore, HistoryItem, Option

# Create your views here.

def index(request):
    return HttpResponse("Hello, world. You're at the API.")

@csrf_exempt
def areas(request):
    '''
    List all areas
    '''
    if(request.method == 'GET'):
        # get all the areas
        areas = Area.objects.all()
        # serialize the area data
        serializer = AreaSerializer(areas, many=True)
        # return a JSON response
        return JsonResponse(serializer.data,safe=False)
    elif(request.method == 'POST'):
        # parse the incoming information
        data = JSONParser().parse(request)
        # instantiate with the serializer
        serializer = AreaSerializer(data=data)
        # check if the sent information is okay
        if(serializer.is_valid()):
            # if okay save to database
            serializer.save()
            # provide a JSON Response with the data that was saved
            return JsonResponse(serializer.data, status=201)
        # provide a JSON Response with the necessary error information
        return JsonResponse(serializer.errors, status=400)

@csrf_exempt
def area_detail(request, pk):
    try:
        # obtain the area with the passed id
        area = Area.objects.get(pk=pk)
    except:
        # respond with a 404 error message
        return HttpResponse(status=404)
    if(request.method == 'PUT'):
        # parse the incoming information
        data = JSONParser().parse(request)
        # instantiate with the serializer
        serializer = AreaSerializer(area, data=data)
        # check whether the sent information is okay
        if(serializer.is_valid()):
            # if okay, save it on the database
            serializer.save()
            # return a JSON response with the data that was submitted
            return JsonResponse(serializer.data, status=201)
        # provide a JSON response with the necessary error information
        return JsonResponse(serializer.errors, status=400)
    elif(request.method == 'DELETE'):
        # delete the area
        area.delete()
        # return a no content response
        return HttpResponse(status=204)
    elif(request.method == 'GET'):
        # serialize the area data
        serializer = AreaSerializer(area, many=False)
        # return a JSON response
        return JsonResponse(serializer.data,safe=False)