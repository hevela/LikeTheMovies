import re
import urllib2
from bs4 import BeautifulSoup
from django.shortcuts import render

from helpers import messages

from LikeTheMovies import settings

NO_IMG = 'http://ia.media-imdb.com/images/G/01/imdb/images/logos/' \
           'imdb_fb_logo-1730868325._V379391653_.png'

BASE_URL = 'http://www.imdb.com/title/tt{0}'

def crawl():

    for i in range(1, 9999999):
        url = BASE_URL.format(str(i).zfill(7))
        print url
        response, code = parse_page(url)



def parse_page(url):
    req = urllib2.Request(url, headers={'User-Agent': "Magic Browser"})
    response = urllib2.urlopen(req)
    text = response.read()
    code = response.getcode()
    if 200 >= code < 400:
        soup = BeautifulSoup(text)

        media_metadata = dict(
            media_type=get_meta_content({'property': 'og:type'}, soup),
            title=get_meta_content({'property': 'og:title'}, soup),
            description=get_meta_content({'property': 'og:description'}, soup)
        )

        image_url = get_meta_content({'property': 'og:image'}, soup)
        media_metadata['media_image'] = get_image(image_url)

        if media_metadata['media_type'] == 'video.episode':
            tv_serie_metadata(media_metadata, soup)
        else:
            #year
            h1 = soup.findAll('h1', attrs={'class': 'header'})[0]
            date_airing = h1.findAll('span',
                                     attrs={'class': 'nobr'})[0].contents[0]
            year_re = re.search('\d{4}', date_airing, re.IGNORECASE)
            if year_re:
                #year without link, like in tv series
                media_metadata['year'] = year_re.group(0)
            else:
                media_metadata['year'] = h1.findAll('a')[0].contents[0]
                if media_metadata['media_type'] == 'video.movie':
                    director = soup.findAll('div',
                                            attrs={'itemprop': 'director'})[0]
                    media_metadata['director'] = \
                        director.findAll('span')[0].contents[0]

        return media_metadata, 200

    else:
        return messages.errors['remote_404'], 400


def tv_serie_metadata(media_metadata, soup):
    h2 = soup.findAll('h2', attrs={'class': 'tv_header'})[0]

    #get episode info
    info = h2.findAll('span', attrs={'class': 'nobr'})[0].contents[0].strip()
    media_metadata['episode_info'] = info

    try:
        director = soup.findAll('div', attrs={'itemprop': 'director'})[0]
    except IndexError:
        director = soup.findAll('div', attrs={'itemprop': 'name'})[0]

    media_metadata['director'] = director.findAll('span')[0].contents[0]

    #get parent info
    parent_url = h2.contents[1]['href']
    parent_identifier = parent_url.partition('/title/tt')[2]
    parent_url = BASE_URL.format(parent_identifier)
    media_metadata['parent'] = parse_page(parent_url)[0]

    #year
    h1 = soup.findAll('h1', attrs={'class': 'header'})[0]
    date_airing = h1.findAll('span', attrs={'class': 'nobr'})[0].contents[0]
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


def get_image(image_url):
    image_url = image_url.strip()
    if image_url and image_url != NO_IMG:
        opener1 = urllib2.build_opener()
        page1 = opener1.open(image_url)
        my_picture = page1.read()
        filename = image_url.partition("http://ia.media-imdb.com/images/M/")
        path = settings.STATIC_ROOT
        img_filename = filename[2]
        filename = path + img_filename
        print img_filename  # test
        fout = open(filename, "wb")
        fout.write(my_picture)
        #la guardo en /temp
        fout.close()
        return img_filename
    return ''