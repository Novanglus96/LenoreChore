from django.urls import path, include
from rest_framework import routers
from . import views
from .views import UserRegistrationView, UserLoginView, UserLogoutView

router = routers.DefaultRouter()
router.register(r'areas', views.AreaView, 'area')
router.register(r'chores', views.ChoreView, 'chore')
router.register(r'historyitems', views.HistoryItemView, 'historyitem')
router.register(r'options', views.OptionView, 'option')

urlpatterns = [
    path("", include(router.urls)),
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('logout/', UserLogoutView.as_view(), name='user-logout'),
]