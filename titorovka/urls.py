from django.urls import path
from titorovka import views, views31, views33
from titorovka.views import start_perenaladka31, start_donaladka31, rabota31, TO31, start_perenaladka33, rabota33, TO33, \
    start_donaladka33

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

    path('update_items33/', views33.update_items33, name='update_items33'),
    path('getData33', views33.getData33, name='getData33'),
    path(r'update33', views33.update33, name='update33'),
    path('getBtn33', views33.getBtn33, name='getBtn33'),
    path('start_perenaladka33/', start_perenaladka33, name='start_perenaladka33'),
    path('start_donaladka33/', start_donaladka33, name='start_donaladka33'),
    path('rabota33/', rabota33, name='rabota33'),
    path('TO33/', TO33, name='TO33'),

]
