from django.contrib.auth.models import User
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from movies.models import Movie, TvSerie, Game


class MovieUser(models.Model):
    # TODO: add manager to get lists of movies
    user = models.OneToOneField(User)
    external_uid = models.IntegerField(db_index=True, unique=True)
    access_token = models.CharField(max_length=256)
    expires = models.IntegerField(blank=True, null=True)


@python_2_unicode_compatible
class MovieListName(models.Model):
    movie_list_name = models.CharField(max_length=128)

    def __str__(self):
        return self.movie_list_name


@python_2_unicode_compatible
class SavedMovie(models.Model):
    movie = models.ForeignKey(Movie)
    user = models.ForeignKey(User)
    list = models.ForeignKey(MovieListName)

    def __str__(self):
        s = [self.movie.title,
             self.user.get_full_name(),
             self.list.movie_list_name]
        return " - ".join(s)


@python_2_unicode_compatible
class SavedTVSerie(models.Model):
    tv_serie = models.ForeignKey(TvSerie)
    user = models.ForeignKey(User)
    list = models.ForeignKey(MovieListName)

    def __str__(self):
        s = [self.tv_serie.title,
             self.user.get_full_name(),
             self.list.movie_list_name]
        return " - ".join(s)


@python_2_unicode_compatible
class SavedGame(models.Model):
    game = models.ForeignKey(Game)
    user = models.ForeignKey(User)
    list = models.ForeignKey(MovieListName)

    def __str__(self):
        s = [self.game.title,
             self.user.get_full_name(),
             self.list.movie_list_name]
        return " - ".join(s)