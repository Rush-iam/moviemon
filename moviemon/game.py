import pickle
import random
from enum import Enum
from pathlib import Path

import requests
import os

from django.conf import settings
from django.shortcuts import Http404


class MapState(Enum):
    NONE = 0
    MON = 1
    BALL = 2


class BattleState(Enum):
    NONE = 0
    MISSED = 1


class Player:
    def __init__(self, x, y, balls, strength):
        self.pos_x = x
        self.pos_y = y
        self.movieballs = balls
        self.moviedex = []
        self.strength = strength


class GameData:
    moviemons: dict
    player: Player
    map_size_x: int
    map_size_y: int

    map_state: MapState
    map_state_moviemon: int
    battle_state: BattleState
    moviedex_index: int
    slot_state: str

    def __init__(self, player, moviemons, map_size_x, map_size_y):
        random.seed()
        self.player = player
        self.moviemons = moviemons
        self.map_size_x = map_size_x
        self.map_size_y = map_size_y

        self.map_state = MapState.NONE
        self.map_state_moviemon = 0
        self.battle_state = BattleState.NONE
        self.moviedex_index = 0
        self.slot_state = 'a'

    @classmethod
    def load_default_settings(cls):
        player = Player(
                x=settings.PLAYER_POS_X,
                y=settings.PLAYER_POS_Y,
                balls=settings.NBR_MOVIEBALL,
                strength=settings.PLAYER_STRENGTH,
            )
        moviemons = {m['imdbID']: {
            "name": m['Title'],
            "poster": m['Poster'],
            "real": m["Director"],
            "year": m["Year"],
            "rating": m['imdbRating'],
            "synopsis": m["Plot"],
            "actors": m["Actors"],
        } for m in MoviesInfo.get_list()}
        player.moviedex = []

        map_size_x = settings.MAP_WIDTH
        map_size_y = settings.MAP_HEIGHT
        return GameData(player, moviemons, map_size_x, map_size_y)

    @staticmethod
    def get_slots():
        slots = {}
        save_dir = Path(settings.SAVE_DIR)
        if not save_dir.exists():
            save_dir.mkdir()
        for file in os.listdir(settings.SAVE_DIR):
            if file.startswith('slot') and len(file) > 4:
                slots[file[4]] = file
        return slots

    @staticmethod
    def slot_filename_decode(file_name):
        words = file_name.split('_')
        moviedex_len = words[1]
        moviemons_len = words[2].split('.')[0]
        return f'Progress: {moviedex_len}/{moviemons_len}'

    @staticmethod
    def slot_filename_encode(slot, moviedex_len, moviemons_len):
        return f'slot{slot}_{moviedex_len}_{moviemons_len}.mmg'

    def load_game(self, slot):
        slots = self.get_slots()
        if slot in slots:
            with open(os.path.join(settings.SAVE_DIR, slots[slot]), 'rb') as gd_file:
                game = pickle.load(gd_file)
            return game
        return None

    def save_game(self, slot):
        slots = self.get_slots()
        if slot in slots:
            os.remove(os.path.join(settings.SAVE_DIR, slots[slot]))

        file_name = self.slot_filename_encode(
            slot, len(self.player.moviedex), len(self.moviemons)
        )
        pathfile = os.path.join(settings.SAVE_DIR, file_name)
        with open(pathfile, 'wb') as gd_file:
            pickle.dump(self, gd_file)

    def get_random_movie(self):
        list_moviemon_nc = self.get_not_caught()
        if len(list_moviemon_nc):
            return random.choice(list_moviemon_nc)
        else:
            return 0

    def get_not_caught(self):
        not_caught = []
        for movie_id in self.moviemons:
            if movie_id not in self.player.moviedex:
                not_caught.append(movie_id)
        return not_caught

    def get_strength(self):
        return self.player.strength + len(self.player.moviedex)

    def calc_win_rate(self, moviemon_id):
        moviemon_rating = self.moviemons[moviemon_id]['rating']
        moviemon_strength = int(float(moviemon_rating) * 10)
        win_rate = 50 - moviemon_strength + self.get_strength() * 5
        win_rate = min(90, win_rate)
        win_rate = max(1, win_rate)
        return win_rate

    def get_movie(self, moviemon_id):
        return self.moviemons.get(moviemon_id)

    def set_random_map_state(self):
        self.map_state = random.choice((MapState.NONE, MapState.MON, MapState.BALL))
        not_caught = self.get_not_caught()
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

    def try_to_catch(self, movie_id: str):
        win_rate = self.calc_win_rate(movie_id)
        if random.randrange(100) < win_rate:
            self.player.moviedex.append(movie_id)
        else:
            self.battle_state = BattleState.MISSED


class MoviesInfo:
    film_list = []

    @classmethod
    def get_info_list(cls):
        titles_movies = settings.MOVIES
        for title in titles_movies:
            try:
                response_json = requests.get(
                    f'http://www.omdbapi.com/?apikey='
                    f'{settings.OMDB_KEY}&t="{title}"'
                )
            except Exception as e:
                raise Http404()
            if response_json.status_code != 200:
                raise Http404()
            res = response_json.json()
            if res['Title'] == 'N/A':
                raise Http404()
            if res['Poster'] == 'N/A':
                raise Http404()
            if res['imdbRating'] == 'N/A':
                raise Http404()

            cls.film_list.append(res)
        print(f'{len(cls.film_list)} films got from OMDB')

    @classmethod
    def get_list(cls):
        if len(cls.film_list) == 0:
            cls.get_info_list()
        return cls.film_list
