from django.template.defaulttags import url
from django.urls import path
from temruk import views
from temruk import views2
from temruk import views5,views4
from temruk.views import profile_view, profileOut_view, start_perenaladka5, start_donaladka5, rabota5, TO5, \
    start_perenaladka2, start_donaladka2, rabota2, TO2, start_perenaladka4, start_donaladka4, rabota4, TO4
from temruk.views5 import select5

urlpatterns = [

    path('', views.index, name='home'),

    path('tv5', views.TV5, name='tv5'),
    path('tv2', views.TV2, name='tv2'),
    path('tv4', views.TV4, name='tv4'),


    path('temruk', views.temruk, name='temruk'),

    path(r'update', views5.update, name='update'),
    path(r'update5_2', views5.update5_2, name='update5_2'),
    path(r'update4', views4.update4, name='update4'),
    path(r'update4_2', views4.update4_2, name='update4_2'),
    path(r'update2', views2.update2, name='update2'),
    path(r'update2_2', views2.update2_2, name='update2_2'),


    path('getData', views5.getData, name='getData'),
    path('getData4', views4.getData4, name='getData4'),
    path('getData2', views2.getData2, name='getData2'),


    path('update_items5/', views5.update_items5, name='update_items5'),
    path('update_items4/', views4.update_items4, name='update_items4'),
    path('update_items2/', views2.update_items2, name='update_items2'),

    path('getBtn2', views2.getBtn2, name='getBtn2'),
    path('getBtn4', views4.getBtn4, name='getBtn4'),
    path('getBtn5', views5.getBtn5, name='getBtn5'),

    path('otchet', views.otchet, name='otchet'),
    path('otchetSmena', views.otchetSmena, name='otchetSmena'),

    path('start_perenaladka5/', start_perenaladka5, name='start_perenaladka5'),
    path('start_donaladka5/', start_donaladka5, name='start_donaladka5'),
    path('rabota5/', rabota5, name='rabota5'),
    path('TO5/', TO5, name='TO5'),


    path('start_perenaladka2/', start_perenaladka2, name='start_perenaladka2'),
    path('start_donaladka2/', start_donaladka2, name='start_donaladka2'),
    path('rabota2/', rabota2, name='rabota2'),
    path('TO2/', TO2, name='TO2'),

    path('start_perenaladka4/', start_perenaladka4, name='start_perenaladka4'),
    path('start_donaladka4/', start_donaladka4, name='start_donaladka4'),
    path('rabota4/', rabota4, name='rabota4'),
    path('TO4/', TO4, name='TO4'),


    path('profile', profile_view, name='profile'),
    path('profileOut/', profileOut_view, name='profileOut'),

    path('select5/', select5, name='select5'),

]
