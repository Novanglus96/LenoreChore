from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'areas', views.AreaView, 'area')
router.register(r'chores', views.ChoreView, 'chore')
router.register(r'historyitems', views.HistoryItemView, 'historyitem')
router.register(r'options', views.OptionView, 'option')
router.register(r'users', views.UserViewSet, 'user')
router.register(r'historyitem-create', views.HistoryItemCreateViewSet, basename='historyitem-create')
router.register(r'chore-complete', views.ChoreCompleteViewSet)

urlpatterns = [
    path("", include(router.urls)),
]