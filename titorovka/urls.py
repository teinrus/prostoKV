from django.urls import path
from titorovka import views, views31
from titorovka.views import start_perenaladka31, start_donaladka31, rabota31, TO31

urlpatterns = [
    path('', views.index, name='titorovka'),
    path('otchet', views.Sotchet, name='Sotchet'),

    path('update_items31/', views31.update_items31, name='update_items31'),

    path('getData31', views31.getData31, name='getData31'),

    path(r'update31', views31.update31, name='update31'),

    path('getBtn31', views31.getBtn31, name='getBtn31'),

    path('start_perenaladka31/', start_perenaladka31, name='start_perenaladka31'),
    path('start_donaladka31/', start_donaladka31, name='start_donaladka31'),
    path('rabota31/', rabota31, name='rabota31'),
    path('TO31/', TO31, name='TO31'),
]
