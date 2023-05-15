from django.urls import path
from titorovka import views


urlpatterns = [
    path('', views.index, name='titorovka'),
    path('otchet', views.Sotchet, name='Sotchet'),
]
