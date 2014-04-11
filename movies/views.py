import urllib2
from bs4 import BeautifulSoup
from django.shortcuts import render


def crawl():
    base_url = 'http://www.imdb.com/title/tt'

    for i in range(1, 2911368):

        req = urllib2.Request(url, headers={'User-Agent': "Magic Browser"})
    response = urllib2.urlopen(req)
    text = response.read()
    code = response.getcode()
    if 200 >= code < 400:
        soup = BeautifulSoup(text)
        title = soup.title.contents[0]
        try:
            subtitle = soup.h1.contents[0].text
        except AttributeError:
            subtitle = ""
        images = self.get_images(soup, url)
        description = self.get_description(soup)

        return dict(title=title, url=url, subtitle=subtitle, images=images,
                    description=description), 200

    else:
        return OEMBED_ERRORS['remote_server_error'], 400