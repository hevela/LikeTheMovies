import re
import urllib2
from bs4 import BeautifulSoup
from django.shortcuts import render

from helpers import messages

from LikeTheMovies import settings
from movies.models import NotFound, TvSerie, Movie, TvEpisode

NO_IMG = 'http://ia.media-imdb.com/images/G/01/imdb/images/logos/' \
           'imdb_fb_logo-1730868325._V379391653_.png'

BASE_URL = 'http://www.imdb.com/title/tt{0}'


def add_tv_series(media_metadata):
    tvserie, created = TvSerie.objects.get_or_create(
        title=media_metadata['title'],
        description=media_metadata['description'],
        image=media_metadata['media_image'],
        year=media_metadata['year'],
        imdb_id=media_metadata['imdb_id']
    )
    return tvserie


def add_tv_episode(media_metadata):
    try:
        parent = TvSerie.objects.get(
            imdb_id=media_metadata['parent']['imdb_id'])
    except TvSerie.DoesNotExist:
        parent = add_tv_series(media_metadata['parent'])

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


def add_movie(media_metadata):
    movie, created = Movie.objects.get_or_create(
        title=media_metadata['title'],
        description=media_metadata['description'],
        image=media_metadata['media_image'],
        year=media_metadata['year'],
        director=media_metadata['director'],
        imdb_id=media_metadata['imdb_id'],
    )
    return movie


save_media = {
    'video.movie': add_movie,
    'video.episode': add_tv_episode,
    'video.tv_show': add_tv_series,
}


def crawl(start=1):

    for i in range(start, 9999999):
        url = BASE_URL.format(str(i).zfill(7))
        print url
        response, code = parse_page(url)

        if code != 400:
            save_media[response['media_type']](response)
        else:
            NotFound(imdb_id=response['imdb_id']).save()


def parse_page(url):

    id_imdb = re.search('tt\d{7}', url, re.IGNORECASE)
    if id_imdb:
        imdb_id = id_imdb.group(0)
    else:
        print "unknown imdb format"
        imdb_id = url

    media_metadata = dict(imdb_id=imdb_id)

    req = urllib2.Request(url, headers={'User-Agent': "Magic Browser"})
    try:
        response = urllib2.urlopen(req)
    except urllib2.HTTPError:
        print messages.errors['remote_404']
        return media_metadata, 400

    text = response.read()
    code = response.getcode()
    if 200 >= code < 400:
        soup = BeautifulSoup(text)

        media_metadata['media_type'] = get_meta_content(
            {'property': 'og:type'}, soup)
        media_metadata['title'] = get_meta_content(
            {'property': 'og:title'}, soup)
        media_metadata['description'] = get_meta_content(
            {'property': 'og:description'}, soup)

        image_url = get_meta_content({'property': 'og:image'}, soup)
        media_metadata['media_image'] = get_image(
            image_url, folder=media_metadata['media_type'].partition('.')[2])

        if media_metadata['media_type'] == 'video.episode':
            tv_serie_metadata(media_metadata, soup)
        else:
            #year
            try:
                h1 = soup.findAll('h1', attrs={'class': 'header'})[0]
                date_airing = h1.findAll('span',
                                         attrs={'class': 'nobr'})[0].contents[0]
            except IndexError:
                media_metadata['year'] = None
            else:
                year_re = re.search('\d{4}', date_airing, re.IGNORECASE)
                if year_re:
                    #year without link, like in tv series
                    media_metadata['year'] = year_re.group(0)
                else:
                    media_metadata['year'] = h1.findAll('a')[0].contents[0]

            if media_metadata['media_type'] == 'video.movie':
                try:
                    director = soup.findAll(
                        'div',
                        attrs={'itemprop': 'director'})[0]
                except IndexError:
                    #No director
                    media_metadata['director'] = ''
                else:
                    media_metadata['director'] = \
                        director.findAll('span')[0].contents[0]

        return media_metadata, 200

    else:
        return messages.errors['remote_404'], 400


def tv_serie_metadata(media_metadata, soup):
    h2 = soup.findAll('h2', attrs={'class': 'tv_header'})[0]

    #get episode info
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
            media_metadata['director'] = director.findAll('span')[0].contents[0]
    else:
        media_metadata['director'] = director.findAll('span')[0].contents[0]

    #get parent info
    parent_url = h2.contents[1]['href']
    parent_identifier = parent_url.partition('/title/tt')[2]
    parent_url = BASE_URL.format(parent_identifier)
    media_metadata['parent'] = parse_page(parent_url)[0]

    #year
    try:
        h1 = soup.findAll('h1', attrs={'class': 'header'})[0]
        date_airing = h1.findAll('span', attrs={'class': 'nobr'})[0].contents[0]
    except IndexError:
        media_metadata['year'] = None
    else:
        year_re = re.search('\d{4}', date_airing, re.IGNORECASE)
        if year_re:
            media_metadata['year'] = year_re.group(0)


def get_meta_content(meta, soup):
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


def get_image(image_url, folder=''):
    image_url = image_url.strip()
    if image_url and image_url != NO_IMG:
        try:
            opener1 = urllib2.build_opener()
            page1 = opener1.open(image_url)
        except urllib2.HTTPError:
            return ''
        my_picture = page1.read()
        filename = image_url.partition("http://ia.media-imdb.com/images/M/")
        path = settings.STATIC_ROOT
        img_filename = filename[2]
        if folder:
            path += folder + '/'
        filename = path + img_filename
        print img_filename  # test
        fout = open(filename, "wb")
        fout.write(my_picture)
        #la guardo en /temp
        fout.close()
        return img_filename
    return ''