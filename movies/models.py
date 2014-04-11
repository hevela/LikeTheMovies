# -*- coding: utf-8 -*-
from django.db import models


class NotFound(models.Model):
    imdb_id = models.CharField(max_length=10, unique=True)

    def __unicode__(self):
        return str(self.imdb_id)


class Movie(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField(null=True, blank=True)
    image = models.CharField(max_length=144, null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    director = models.CharField(max_length=128)
    imdb_id = models.CharField(max_length=16)

    def __unicode__(self):
        return self.title + '(' + str(self.year) + ')'


class TvSerie(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField(null=True, blank=True)
    image = models.CharField(max_length=144, null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    director = models.CharField(max_length=128)
    imdb_id = models.CharField(max_length=16)

    def __unicode__(self):
        return self.title + '(' + str(self.year) + ')'


class TvEpisode(models.Model):
    serie = models.ForeignKey(TvSerie)
    title = models.CharField(max_length=128)
    description = models.TextField(null=True, blank=True)
    image = models.CharField(max_length=144, null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    director = models.CharField(max_length=128)
    imdb_id = models.CharField(max_length=16)
    episode_info = models.CharField(max_length=144, null=True, blank=True)

    def __unicode__(self):
        return self.serie.title + '-' + self.title + '(' + str(self.year) + ')'