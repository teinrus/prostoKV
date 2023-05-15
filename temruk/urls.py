from django.urls import path
from temruk import views
from temruk import views2
from temruk import views5,views4
from temruk.views import profile_view, profileOut_view

urlpatterns = [
    path('', views.index, name='home'),

    path('temruk', views.temruk, name='temruk'),

    path(r'update', views5.update, name='update'),
    path(r'update4', views4.update4, name='update4'),
    path(r'update2', views2.update2, name='update2'),


    path('getData', views5.getData, name='getData'),
    path('getData4', views4.getData4, name='getData4'),
    path('getData2', views2.getData2, name='getData2'),


    path('update_items5/', views5.update_items5, name='update_items5'),
    path('update_items4/', views4.update_items4, name='update_items4'),
    path('update_items2/', views2.update_items2, name='update_items2'),

    path('otchet', views.otchet, name='otchet'),


    path('profile', profile_view, name='profile'),
    path('profileOut', profileOut_view, name='profileOut'),

]
