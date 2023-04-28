from django.urls import path
from titorovka import views


urlpatterns = [
    path('', views.homePageView, name='titorovka'),
]
