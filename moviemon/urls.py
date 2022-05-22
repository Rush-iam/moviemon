from django.urls import path

from . import views

urlpatterns = [
    path('', views.title, name='title'),
    path('worldmap', views.worldmap, name='worldmap'),
    path('battle/<str:moviemon_id>', views.battle, name='battle'),
    path('moviedex', views.moviedex, name='moviedex'),
    # path('moviedex/<str:moviemon_id>', views.title_screen, name='detail'),
    path('options', views.options, name='options'),
    path('options/save_game', views.save_load, name='save'),
    path('options/load_game', views.save_load, name='load'),
]
