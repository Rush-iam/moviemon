import pickle
from django.shortcuts import Http404
import requests
from django.conf import settings
import random
import os
import re

class GameData():
    data = {}
    list_movie_nc = []
    catchable = ''

    def load_game(self, save_file):
        gd_file = open(settings.SAVE_DIR + '/' + save_file, 'rb')
        data = pickle.load(gd_file)
        gd_file.close()
        self.load(data)

    def save_game(self, slot):
        pathfile = "{}/slot{}_{}_{}.sav".format(settings.SAVE_DIR,list(['a','b','c'])[slot],len(self.data['moviedex']),len(self.data['list_moviemon']))
        gd_file = open(pathfile, 'wb')
        pickle.dump(self.data,gd_file)
        gd_file.close()

    def save_state(self):
        gd_file = open('gamestate', 'wb')
        pickle.dump(self.data,gd_file)
        gd_file.close()

    def load_state(self):
        gd_file = open('gamestate', 'rb')
        self.data = pickle.load(gd_file)
        gd_file.close()

    def load(self, data: object) -> object:
        self.data = data
        self.list_movie_nc = self.get_list_movi_nc()
        self.save_state()
        return self

    def dump(self):
        return(self.data)

    def load_default_settings(self):
        self.data = {
            "position": [settings.PLAYER_POS_X, settings.PLAYER_POS_Y],
            "nbr_movieball":settings.NBR_MOVIEBALL,
            "moviedex":[],
            "list_moviemon" : movies.MoviesInfo().get_list(),
        }
        list_movie_nc = settings.MOVIES
        return self

    def get_list_movi_nc(self):
        movie_nc = []
        for movie in self.data['list_moviemon']:
            if not movie['imdbID'] in self.data['moviedex']:
                movie_nc.append(movie['imdbID'])
        return(movie_nc)

    def get_random_movie(self):
        list_moviemon_nc = self.get_list_movi_nc()
        return list_moviemon_nc[random.randint(0,len(list_moviemon_nc) - 1)]

    def get_strength(self):
        return(len(self.data['moviedex']))

    def get_movie(self, moviemon_id):
        for movie in self.data["list_moviemon"]:
            if movie['imdbID'] ==  moviemon_id:
                detail_movie = {
                    "name" : movie['Title'],
                    "poster" : movie['Poster'],
                    "real" : movie["Director"],
                    "year" : movie["Year"],
                    "rating" : movie['imdbRating'],
                    "synopsis" : movie["Plot"],
                    "actors" : movie["Actors"],
                }
                return detail_movie
        return None

    # def checkpos(self):
    #     if self.data['position'][0] < 0 or self.data['position'][0] >= settings.MAP_WIDTH:
    #         self.load_state()
    #     elif self.data['position'][1] < 0 or self.data['position'][1] >= settings.MAP_HEIGHT:
    #         self.load_state()
    #     else:
    #         return 1
    #     return 0

    @classmethod
    def define_catchable(cls, movie_id):
        cls.catchable = movie_id

  # def transform_events(self, movieball_event, moviemon_id):
  #    events = ['','', '#']
  #      if movieball_event == "True":
  #          events[0] = 'You found a movieball!'
  #          self.data['nbr_movieball'] += 1
  #      if moviemon_id != "":
  #          movie_name = self.get_movie(moviemon_id)['name']
  #          events[1] = "You tumbled over " + movie_name + ", Press A to catch it!"
  #          events[2] = 'http://127.0.0.1:8000/battle/' + moviemon_id + '/'
  #          self.define_catchable(moviemon_id)
  #      return events

    # def try_random_events(self):
    #     events = ['', '#']
    #     if len(self.data['moviedex']) != len(self.data['list_moviemon']):
    #         if random.randint(1, 100) <= settings.FIND_MOVIEBALL_PERCENT:
    #             events[0] = True
    #         if random.randint(1, 100) <= settings.FIND_MOVIEMON_PERCENT:
    #             movie_id = self.get_random_movie()
    #             events[1] = movie_id
    #     return events

class MoviesInfo:
    film_list = []

    @classmethod
    def get_info_list(cls):
        titles_movies = settings.MOVIES
        for title in titles_movies:
            try:
                response_json = requests.get(
                    'http://www.omdbapi.com/?apikey=' + settings.OMDB_KEY + '&t="' + title + '"'
                )
            except Exception as e:
                raise Http404()
            if response_json.status_code != 200:
                raise Http404()
            res = response_json.json()
            if (res['Title'] == 'N/A'):
                raise Http404()
            if (res['Poster'] == 'N/A'):
                raise Http404()
            if (res['imdbRating'] == 'N/A'):
                raise Http404()

            cls.film_list.append(res)

    def get_list(self):
        if len(self.film_list) == 0:
            self.get_info_list()
        return self.film_list

if __name__ == "__main__":
    g = GameData()
    