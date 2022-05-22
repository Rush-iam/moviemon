from django.urls import path

from . import views

urlpatterns = [
    path('', views.title, name='title'),
    path('worldmap', views.worldmap, name='worldmap'),
    path('battle/<int:moviemon_id>', views.battle, name='battle'),
    # path('moviedex', views.title_screen, name='moviedex'),
    # path('moviedex/<int:moviemon_id>', views.title_screen, name='detail'),
    # path('options', views.title_screen, name='options'),
    # path('options/save_game', views.title_screen, name='save'),
    # path('options/load_game', views.title_screen, name='load'),
]
