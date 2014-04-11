from django.contrib.auth.models import User
from django.db import models
from movies.models import Movie


class MovieUser(models.Model):
    user = models.OneToOneField(User)
    external_uid = models.IntegerField(db_index=True, unique=True)
    access_token = models.CharField(max_length=256)
    expires = models.IntegerField(blank=True, null=True)

    @property
    def movies_seen(self):
        return MovieSeen.objects.filter(user=self.user).count()


class FavoriteMovie(models.Model):
    movie = models.ForeignKey(Movie)
    user = models.ForeignKey(User)

    class Meta:
        unique_together = (('movie', 'user'),)

    def __unicode__(self):
        return self.user + ' - ' + self.movie.title


class BlockedMovie(models.Model):
    movie = models.ForeignKey(Movie)
    user = models.ForeignKey(User)

    class Meta:
        unique_together = (('movie', 'user'),)

    def __unicode__(self):
        return self.user + ' - ' + self.movie.title


class MovieSeen(models.Model):
    movie = models.ForeignKey(Movie)
    user = models.ForeignKey(User)

    class Meta:
        unique_together = (('movie', 'user'),)

    def __unicode__(self):
        return self.user + ' - ' + self.movie.title


class MovieToSee(models.Model):
    movie = models.ForeignKey(Movie)
    user = models.ForeignKey(User)

    def seen(self):
        MovieSeen(user=self.user, movie=self.movie).save()
        self.delete()

    class Meta:
        unique_together = (('movie', 'user'),)

    def __unicode__(self):
        return self.user + ' - ' + self.movie.title