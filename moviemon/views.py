import math
import random
from enum import Enum

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect

from moviemon.views_utils import pressed_button
from django.template.defaulttags import register


@register.filter
def return_poster(l, i):
    try:
        return l[i]['poster']
    except:
        return None

@register.filter
def return_rating(l, i):
    try:
        return l[i]['rating']
    except:
        return None


class MapState(Enum):
    NONE = 0
    MON = 1
    BALL = 2


class BattleState(Enum):
    NONE = 0
    MISSED = 1


class GameDummy:
    class Player:
        pos_x = 3
        pos_y = 5
        movieballs = 2
        caught = [123]
        strength = 3.2

        def calc_win_rate(self, movimon_rating):
            return 33

    player = Player()
    map_size_x = 10
    map_size_y = 10
    moviemons = {
        123: {
            'title': 'Godzilla',
            'rating': 3.3,
            'poster': 'posters/godzilla.jpg'
        }
    }

    map_state: MapState = MapState.NONE
    map_state_moviemon = 123

    battle_state: BattleState = BattleState.NONE

    moviedex_index = 0

    def __init__(self):
        random.seed()

    def get_movie(self, movie_id: int):
        return self.moviemons[movie_id]

    def try_to_catch(self, movie_id: int):
        if random.randrange(2) == 1:  # DO CALC BY SUBJECT
            self.player.caught.append(movie_id)
        else:
            self.battle_state = BattleState.MISSED

    def load_default_settings(self):
        self.map_state = MapState.NONE

    def set_random_map_state(self):
        self.map_state = random.choice((MapState.NONE, MapState.MON, MapState.BALL))
        not_caught = [m for m in self.moviemons if m not in self.player.caught]
        if self.map_state == MapState.MON and not_caught:
            self.map_state_moviemon = random.choice(not_caught)
        elif self.map_state == MapState.BALL:
            self.player.movieballs += 1
        else:
            self.map_state = MapState.NONE

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
                    game.map_state = MapState.NONE
                    game.battle_state = BattleState.NONE
                    return redirect(f'battle/{moviemon_id}')
            case 'Select':
                game.moviedex_index = 0
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


def battle(request: HttpRequest, moviemon_id: int) -> HttpResponse:
    if request.method == 'POST':
        match pressed_button(request.POST):
            case 'A':
                if game.player.movieballs > 0:
                    game.player.movieballs -= 1
                    game.try_to_catch(moviemon_id)
            case 'B':
                return redirect('worldmap')
        return redirect(request.resolver_match.view_name, moviemon_id)

    movie = game.get_movie(moviemon_id)

    context = {
        'title': 'Battle!',
        'buttons_active': {'A', 'B'},
        'movieballs': game.player.movieballs,
        'moviemon_strength': movie['rating'],
        'moviemon_img': movie['poster'],
        'player_strength': game.player.strength,
        'win_rate': game.player.calc_win_rate(movie['rating'])
    }

    if moviemon_id in game.player.caught:
        context['buttons_active'].remove('A')
        context['message'] = 'You caught it!'
    else:
        if game.player.movieballs == 0:
            context['buttons_active'].remove('A')
            context['message'] = 'No movieballs left :-('
        else:
            context['message'] = '<b>A</b> - Launch movieball!'
        if game.battle_state == BattleState.MISSED:
            context['message'] += '<br>You missed!'

    return render(request, 'moviemon/battle.html', context)


def moviedex(request: HttpRequest) -> HttpResponse:
    index = game.moviedex_index
    movies_caught = len(game.player.caught)
    grid_size = int(math.floor(movies_caught**0.5))

    if request.method == 'POST':
        match pressed_button(request.POST):
            case 'Up':
                if index - grid_size >= 0:
                    game.moviedex_index -= grid_size
            case 'Down':
                if index + grid_size < movies_caught:
                    game.moviedex_index += grid_size
            case 'Left':
                if index > 0:
                    game.moviedex_index -= 1
            case 'Right':
                if index < movies_caught - 1:
                    game.moviedex_index += 1
            case 'A':
                return redirect(f'detail/{game.player.caught[index]}')
            case 'Select':
                return redirect('worldmap')
        return redirect(request.resolver_match.view_name)

    if movies_caught == 0:
        return render(request, 'moviemon/moviedex.html', {
            'title': 'Moviedex',
            'buttons_active': {'Select'},
            'message': 'No Moviemons caught :('
        })

    movies = [game.moviemons[index] for index in game.player.caught]
    moviemons_grid = (range(x, x+grid_size) for x in range(0, movies_caught, grid_size))

    context = {
        'title': 'Moviedex',
        'buttons_active': {'Up', 'Down', 'Left', 'Right', 'Select', 'A'},
        'moviemons': movies,
        'grid': moviemons_grid,
        'active_index_x': index % grid_size,
        'active_index_y': index // grid_size,
    }

    return render(request, 'moviemon/moviedex.html', context)
