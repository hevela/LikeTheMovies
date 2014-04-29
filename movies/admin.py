from django.contrib import admin
from movies import models
# Register your models here.
admin.site.register(models.Movie)
admin.site.register(models.TvSerie)
admin.site.register(models.TvEpisode)
admin.site.register(models.Game)