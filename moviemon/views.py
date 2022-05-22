import random
from enum import Enum

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect

from moviemon.views_utils import pressed_button


class MapState(Enum):
    NONE = 0
    MON = 1
    BALL = 2


class GameDummy:
    class Player:
        pos_x = 3
        pos_y = 5
        movieballs = 2

    player = Player()
    map_size_x = 10
    map_size_y = 10
    moviemons = {
        123: 'Godzilla'
    }

    map_state: MapState = MapState.NONE
    map_state_moviemon = 123

    def __init__(self):
        random.seed()

    def load_default_settings(self):
        self.map_state = MapState.NONE

    def set_random_map_state(self):
        self.map_state = random.choice((MapState.MON, MapState.BALL))
        if self.map_state == MapState.MON:
            self.map_state_moviemon = random.choice(tuple(self.moviemons.keys()))
        elif self.map_state == MapState.BALL:
            self.player.movieballs += 1

    def move_up(self):
        if self.player.pos_y != 0:
            self.player.pos_y -= 1
            self.set_random_map_state()

    def move_down(self):
        if self.player.pos_y != self.map_size_y - 1:
            self.player.pos_y += 1
            self.set_random_map_state()

    def move_left(self):
        if self.player.pos_x != 0:
            self.player.pos_x -= 1
            self.set_random_map_state()

    def move_right(self):
        if self.player.pos_x != self.map_size_x - 1:
            self.player.pos_x += 1
            self.set_random_map_state()


game = GameDummy()


def title(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        match pressed_button(request.POST):
            case 'A':
                game.load_default_settings()
                return redirect('worldmap')
            case 'B':
                return redirect('load')
        return redirect(request.resolver_match.view_name)

    context = {
        'title': 'Title Screen',
        'buttons_active': {'A', 'B'},
    }

    return render(request, 'moviemon/title.html', context)


def worldmap(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        match pressed_button(request.POST):
            case 'Up':
                game.move_up()
            case 'Down':
                game.move_down()
            case 'Left':
                game.move_left()
            case 'Right':
                game.move_right()
            case 'A':
                if game.map_state == MapState.MON:
                    moviemon_id = game.map_state_moviemon
                    return redirect(f'battle/{moviemon_id}')
            case 'Select':
                return redirect('moviedex')
            case 'Start':
                return redirect('options')
        return redirect(request.resolver_match.view_name)

    context = {
        'title': 'Worldmap',
        'buttons_active': {
            'Up', 'Down', 'Left', 'Right', 'Select', 'Start', 'A'
        },
        'map_cell_size': 100 / max(game.map_size_y, game.map_size_x),
        'map_size_x': range(game.map_size_x),
        'map_size_y': range(game.map_size_y),
        'player_pos_x': game.player.pos_x,
        'player_pos_y': game.player.pos_y,
        'movieballs': game.player.movieballs,
    }
    if game.map_state == MapState.BALL:
        context['map_message'] = 'You have found MovieBall!<br> +1'
    elif game.map_state == MapState.MON:
        context['map_message'] = 'You met MovieMon!<br> Press A to catch!'

    if game.player.pos_x == 0:
        context['buttons_active'].remove('Left')
    elif game.player.pos_x == game.map_size_x - 1:
        context['buttons_active'].remove('Right')
    if game.player.pos_y == 0:
        context['buttons_active'].remove('Up')
    elif game.player.pos_y == game.map_size_y - 1:
        context['buttons_active'].remove('Down')

    if game.map_state != MapState.MON:
        context['buttons_active'].remove('A')

    return render(request, 'moviemon/worldmap.html', context)
