from django.urls import path

from . import views

urlpatterns = [
    path('areas/', views.areas),
    path('areas/<int:pk>/', views.area_detail),
    path("", views.index, name="index"),
]