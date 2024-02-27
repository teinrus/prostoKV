from django.urls import path
from titorovka import views, views31, views33, views24, views26, views25
from titorovka.views import start_perenaladka31, start_adaptacia31, rabota31, TO31, start_perenaladka33, rabota33, TO33, \
    start_perenaladka24, start_donaladka24, rabota24, TO24, start_perenaladka26, start_donaladka26, \
    rabota26, TO26, start_perenaladka25, start_donaladka25, rabota25, TO25, vid25, vid26, Oformlenie31, \
    start_adaptation33, start_oformlenie33
from titorovka.views31 import handle_select_position31, list_nomenklature31

urlpatterns = [
    path('', views.index, name='titorovka'),
    path('otchet', views.Sotchet, name='Sotchet'),
    path('otchetIgr', views.SotchetIgr, name='SotchetIgr'),

    path('update_items31/', views31.update_items31, name='update_items31'),
    path('getData31', views31.getData31, name='getData31'),
    path(r'update31', views31.update31, name='update31'),
    path('getBtn31', views31.getBtn31, name='getBtn31'),
    path('start_perenaladka31/', start_perenaladka31, name='start_perenaladka31'),
    path('start_adaptacia31/', start_adaptacia31, name='start_adaptacia31'),
    path('rabota31/', rabota31, name='rabota31'),
    path('TO31/', TO31, name='TO31'),
    path('Oformlenie31/', Oformlenie31, name='Oformlenie31'),
    path('list_nomenklature31', list_nomenklature31, name='list_nomenklature31'),
    path('handle_select_position31', handle_select_position31, name='handle_select_position31'),

    path('update_items33/', views33.update_items33, name='update_items33'),
    path('getData33', views33.getData33, name='getData33'),
    path(r'update33', views33.update33, name='update33'),
    path('getBtn33', views33.getBtn33, name='getBtn33'),
    path('start_perenaladka33/', start_perenaladka33, name='start_perenaladka33'),
    path('start_adaptation33/', start_adaptation33, name='start_adaptation33'),
    path('start_oformlenie33/', start_oformlenie33, name='Oformlenie33'),
    path('rabota33/', rabota33, name='rabota33'),
    path('TO33/', TO33, name='TO33'),

    path('update_items24/', views24.update_items24, name='update_items24'),
    path('getData24', views24.getData24, name='getData24'),
    path(r'update24', views24.update24, name='update24'),
    path('getBtn24', views24.getBtn24, name='getBtn24'),
    path('start_perenaladka24/', start_perenaladka24, name='start_perenaladka24'),
    path('start_donaladka24/', start_donaladka24, name='start_donaladka24'),
    path('rabota24/', rabota24, name='rabota24'),
    path('TO24/', TO24, name='TO24'),

    path('update_items26/', views26.update_items26, name='update_items26'),
    path('getData26', views26.getData26, name='getData26'),
    path(r'update26', views26.update26, name='update26'),
    path('getBtn26', views26.getBtn26, name='getBtn26'),
    path('start_perenaladka26/', start_perenaladka26, name='start_perenaladka26'),
    path('start_donaladka26/', start_donaladka26, name='start_donaladka26'),
    path('rabota26/', rabota26, name='rabota26'),
    path('TO26/', TO26, name='TO26'),
    path('vid26/', vid26, name='vid26'),

    path('update_items25/', views25.update_items25, name='update_items25'),
    path('getData25', views25.getData25, name='getData25'),
    path(r'update25', views25.update25, name='update25'),
    path('getBtn25', views25.getBtn25, name='getBtn25'),
    path('start_perenaladka25/', start_perenaladka25, name='start_perenaladka25'),
    path('start_donaladka25/', start_donaladka25, name='start_donaladka25'),
    path('rabota25/', rabota25, name='rabota25'),
    path('TO25/', TO25, name='TO25'),
    path('vid25/', vid25, name='vid25'),

]
