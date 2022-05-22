import math

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect

from moviemon.views_utils import pressed_button
from django.template.defaulttags import register

from .game import GameData, MapState, BattleState


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


game = GameData.load_default_settings()


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
        # 'buttons_active': {'A', 'B'},
        'buttons_active': {'A'},
    }
    return render(request, 'moviemon/title.html', context)


def options(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        match pressed_button(request.POST):
            case 'Start':
                return redirect('worldmap')
            case 'A':
                return redirect('save')
            case 'B':
                return redirect('title')
        return redirect(request.resolver_match.view_name)

    context = {
        'title': 'Options',
        'buttons_active': {'Start', 'A', 'B'},
    }
    return render(request, 'moviemon/options.html', context)


def save(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        match pressed_button(request.POST):
            case 'Up':
                game.slot_index = max(0, game.slot_index - 1)
            case 'Down':
                game.slot_index = min(2, game.slot_index + 1)
            case 'A':
                game.save_game(game.slot_index)
                return redirect('worldmap')
            case 'B':
                return redirect('options')
        return redirect(request.resolver_match.view_name)

    slots = game.get_slots()
    context = {
        'title': 'Options',
        'buttons_active': {'Up', 'Down', 'A', 'B'},
        'slot1': slots[0] if 0 in slots else 'Empty',
        'slot2': slots[1] if 1 in slots else 'Empty',
        'slot3': slots[2] if 2 in slots else 'Empty',
        'active_index': game.slot_index,
    }
    return render(request, 'moviemon/slots.html', context)


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


def battle(request: HttpRequest, moviemon_id: str) -> HttpResponse:
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
        'player_strength': game.get_strength(),
        'win_rate': game.player.calc_win_rate(movie['rating'])
    }

    if moviemon_id in game.player.moviedex:
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
    movies_caught = len(game.player.moviedex)
    grid_size = int(math.ceil(movies_caught**0.5))

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
                return redirect(f'detail/{game.player.moviedex[index]}')
            case 'Select':
                return redirect('worldmap')
        return redirect(request.resolver_match.view_name)

    if movies_caught == 0:
        return render(request, 'moviemon/moviedex.html', {
            'title': 'Moviedex',
            'buttons_active': {'Select'},
            'message': 'No Moviemons caught :('
        })

    movies = [game.moviemons[index] for index in game.player.moviedex]
    moviemons_grid = [
        range(x, min(x+grid_size, movies_caught))
        for x in range(0, movies_caught, grid_size)
    ]

    print(moviemons_grid, movies_caught)
    context = {
        'title': 'Moviedex',
        'buttons_active': {'Up', 'Down', 'Left', 'Right', 'Select'},
        # 'buttons_active': {'Up', 'Down', 'Left', 'Right', 'Select', 'A'},
        'moviemons': movies,
        'grid': moviemons_grid,
        'active_index': index,
        'cell_size': 100 / grid_size,
    }

    return render(request, 'moviemon/moviedex.html', context)
