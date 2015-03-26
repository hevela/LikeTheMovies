# -*- coding: utf-8 -*-
import socket
import urllib2
import time

from bs4 import BeautifulSoup
import re

from helpers import messages


__author__ = 'hector'

from LikeTheMovies import settings
from movies.models import NotFound, TvSerie, Movie, TvEpisode, Game


class MovieSaver(object):
    @classmethod
    def add_tv_series(cls, media_metadata):
        tvserie, created = TvSerie.objects.get_or_create(
            title=media_metadata['title'],
            imdb_id=media_metadata['imdb_id'],
            defaults={
                "description": media_metadata['description'],
                "image": media_metadata['media_image'],
                "year": media_metadata['year'],
            }
        )
        return tvserie

    @classmethod
    def add_game(cls, media_metadata):
        game, created = Game.objects.get_or_create(
            title=media_metadata['title'],
            description=media_metadata['description'],
            image=media_metadata['media_image'],
            year=media_metadata['year'],
            imdb_id=media_metadata['imdb_id']
        )
        return game

    @classmethod
    def add_tv_episode(cls, media_metadata):
        try:
            parent = TvSerie.objects.get(
                imdb_id=media_metadata['parent']['imdb_id'])
        except TvSerie.DoesNotExist:
            parent = cls.add_tv_series(media_metadata['parent'])
        except TvSerie.MultipleObjectsReturned:
            parent = TvSerie.objects.filter(
                imdb_id=media_metadata['parent']['imdb_id'])[0]
            TvSerie.objects.filter(
                imdb_id=media_metadata['parent']['imdb_id']
            ).exclude(pk=parent.pk).delete()

        episode, created = TvEpisode.objects.get_or_create(
            serie=parent,
            title=media_metadata['title'],
            description=media_metadata['description'],
            image=media_metadata['media_image'],
            year=media_metadata['year'],
            director=media_metadata['director'],
            imdb_id=media_metadata['imdb_id'],
            episode_info=media_metadata['episode_info']
        )
        return episode

    @classmethod
    def add_movie(cls, media_metadata):
        movie, created = Movie.objects.get_or_create(
            title=media_metadata['title'],
            description=media_metadata['description'],
            image=media_metadata['media_image'],
            year=media_metadata['year'],
            director=media_metadata['director'],
            imdb_id=media_metadata['imdb_id'],
        )
        return movie


class MovieParser(object):
    # seconds
    timeout = 5
    NO_IMG = ['http://ia.media-imdb.com/images/G/01/imdb/images/logos/'
              'imdb_fb_logo-1730868325._V379391653_.png',
              'http://ia.media-imdb.com/images/G/01/imdb/images/logos/'
              'imdb_fb_logo-1730868325._CB379391653_.png']
    BASE_URL = 'http://www.imdb.com/title/tt{0}'

    save_media = {
        'video.movie': MovieSaver.add_movie,
        'video.episode': MovieSaver.add_tv_episode,
        'video.tv_show': MovieSaver.add_tv_series,
        'game': MovieSaver.add_game,
    }

    NOTFOUND = 404
    TIMEOUT = 410
    SUCCESSCODE = 200
    ERRORSBEGINAT = 400
    SUCCESSBEGINAT = 200
    IMAGEPREFIX = "http://ia.media-imdb.com/images/M/"

    start = 1

    def __init__(self, autostart=False, start=1):
        self.start = start
        if autostart:
            self.automatic()

    @staticmethod
    def __get_meta_content(meta, soup):
        """
        Search a soup object for a specific meta tag
        @param meta: the meta to search for
        @param soup: a Beautiful Soup object
        @type soup: BeautifulSoup
        @return:
        """
        meta_tag = soup.find_all('meta', attrs=meta)
        if meta_tag:
            try:
                meta_content = meta_tag[0]['content']
            except IndexError:
                return False
            else:
                if not meta_content:
                    return False
                else:
                    return meta_content

    def start_crawling(self):
        for i in range(self.start, 9999999):
            url = self.BASE_URL.format(str(i).zfill(7))
            print url
            response, code = self.__parse_page(url)

            if code < self.ERRORSBEGINAT:
                self.save_media[response['media_type']](response)
            elif code == self.NOTFOUND:
                NotFound.objects.get_or_create(
                    imdb_id=response['imdb_id'])
            else:
                print messages.messages['non_controlled']

    def automatic(self):
        last_movie = Movie.objects.last().imdb_id
        last_imdb_id = last_movie.replace("tt0", "")
        try:
            self.start = int(last_imdb_id)
            self.start_crawling()
        except:
            print messages.messages['exception_restart']
            time.sleep(10)
            self.automatic()

    def get_image(self, image_url, folder=''):
        image_url = image_url.strip()
        if image_url and image_url not in self.NO_IMG:
            try:
                opener1 = urllib2.build_opener()
                page1 = opener1.open(image_url)
            except urllib2.HTTPError:
                return ''
            my_picture = page1.read()
            filename = image_url.partition(self.IMAGEPREFIX)
            path = settings.STATIC_ROOT
            img_filename = filename[2]
            if folder:
                path += folder + '/'
            filename = path + img_filename
            fout = open(filename, "wb")
            fout.write(my_picture)
            fout.close()
            return img_filename
        return ''

    def __parse_page(self, url):

        id_imdb = re.search('tt\d{7}', url, re.IGNORECASE)
        if id_imdb:
            imdb_id = id_imdb.group(0)
        else:
            print messages.errors['id_error']
            imdb_id = url

        media_metadata = dict(imdb_id=imdb_id)

        req = urllib2.Request(url, headers={'User-Agent': "Magic Browser"})
        try:
            response = urllib2.urlopen(req, timeout=self.timeout)
        except urllib2.HTTPError:
            print messages.errors['remote_404']
            return media_metadata, self.NOTFOUND
        except socket.timeout:
            print messages.errors['remote_timeout']
            time.sleep(10)
            self.__parse_page(url)
        else:
            text = response.read()
            code = response.getcode()
            if self.SUCCESSBEGINAT >= code < self.ERRORSBEGINAT:
                soup = BeautifulSoup(text)

                media_metadata['media_type'] = self.__get_meta_content(
                    {'property': 'og:type'}, soup)
                media_metadata['title'] = self.__get_meta_content(
                    {'property': 'og:title'}, soup)
                media_metadata['description'] = self.__get_meta_content(
                    {'property': 'og:description'}, soup)

                image_url = self.__get_meta_content({'property': 'og:image'}, soup)
                media_metadata['media_image'] = self.get_image(
                    image_url,
                    folder=media_metadata['media_type'].partition('.')[2])

                if media_metadata['media_type'] == 'video.episode':
                    self.__tv_serie_metadata(media_metadata, soup)
                else:
                    # year
                    try:
                        h1 = soup.findAll('h1', attrs={'class': 'header'})[0]
                        date_airing = h1.findAll(
                            'span',
                            attrs={'class': 'nobr'})[0].contents[0]
                    except IndexError:
                        media_metadata['year'] = None
                    else:
                        year_re = re.search('\d{4}', date_airing, re.IGNORECASE)
                        if year_re:
                            # year without link, like in tv series
                            media_metadata['year'] = year_re.group(0)
                        else:
                            media_metadata['year'] = h1.findAll('a')[0].contents[0]

                    if media_metadata['media_type'] == 'video.movie':
                        try:
                            director = soup.findAll(
                                'div',
                                attrs={'itemprop': 'director'})[0]
                        except IndexError:
                            # No director
                            media_metadata['director'] = ''
                        else:
                            media_metadata['director'] = \
                                director.findAll('span')[0].contents[0]

                return media_metadata, self.SUCCESSCODE

            else:
                return messages.errors['remote_404'], self.NOTFOUND
        return

    def __tv_serie_metadata(self, media_metadata, soup):
        h2 = soup.findAll('h2', attrs={'class': 'tv_header'})[0]

        # get episode info
        try:
            info = h2.findAll('span',
                              attrs={'class': 'nobr'})[0].contents[0].strip()
        except IndexError:
            info = ''

        media_metadata['episode_info'] = info

        try:
            director = soup.findAll('div', attrs={'itemprop': 'director'})[0]
        except IndexError:
            try:
                director = soup.findAll('div', attrs={'itemprop': 'name'})[0]
            except IndexError:
                media_metadata['director'] = ''
            else:
                media_metadata['director'] = \
                    director.findAll('span')[0].contents[0]
        else:
            media_metadata['director'] = director.findAll('span')[0].contents[0]

        # get parent info
        parent_url = h2.contents[1]['href']
        parent_identifier = parent_url.partition('/title/tt')[2]
        parent_url = self.BASE_URL.format(parent_identifier)
        media_metadata['parent'] = self.__parse_page(parent_url)[0]

        # year
        try:
            h1 = soup.findAll('h1', attrs={'class': 'header'})[0]
            date_airing = h1.findAll('span',
                                     attrs={'class': 'nobr'})[0].contents[0]
        except IndexError:
            media_metadata['year'] = None
        else:
            year_re = re.search('\d{4}', date_airing, re.IGNORECASE)
            if year_re:
                media_metadata['year'] = year_re.group(0)
        return