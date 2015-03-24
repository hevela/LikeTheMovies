# -*- coding: utf-8 -*-
__author__ = 'hector'


class MovieParser(object):
    # seconds
    timeout = 5
    NO_IMG = ['http://ia.media-imdb.com/images/G/01/imdb/images/logos/'
              'imdb_fb_logo-1730868325._V379391653_.png',
              'http://ia.media-imdb.com/images/G/01/imdb/images/logos/'
              'imdb_fb_logo-1730868325._CB379391653_.png']
    BASE_URL = 'http://www.imdb.com/title/tt{0}'
