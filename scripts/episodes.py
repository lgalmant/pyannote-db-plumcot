#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Usage: episodes.py SOURCEFILE [SERIES]

Arguments:
    SOURCEFILE    input series list file
    SERIES        optionnal normalized name of a series

"""

from docopt import docopt
import codecs  # for encoding the data as utf-8
import requests
from bs4 import BeautifulSoup


def scrapPage(idSeries, pageIMDB):
    """Extracts episodes list of a series.

    Given an IMDB page, extracts episodes information in this format:
    unique episode identifier, name of the episode, IMDB.com episode page,
    TV.com episode page.

    Parameters
    ----------
    pageIMDB : `str`
        IMDB page with the list of episodes.

    Returns
    -------
    cast : `str`
        String with the correct format, one line per episode.
    """
    urlIDMB = requests.get(pageIMDB).text
    soup = BeautifulSoup(urlIDMB, 'lxml')
    seriesData = ""

    nbSeasons = len(soup.find(id="bySeason").find_all('option')) + 1

    for season in range(1, nbSeasons):
        linkSeason = pageIMDB + "?season=" + str(season)
        urlIDMB = requests.get(linkSeason).text
        soup = BeautifulSoup(urlIDMB, 'lxml')

        table = soup.find('div', {'class': 'eplist'})
        episodesTable = table.find_all('div', class_="list_item")

        for episode in episodesTable:
            infos = episode.find('div', {'class': 'info'})
            nbEpisode = infos.find('meta').get('content')
            link = infos.find('a')
            imdbLink = "https://www.imdb.com" + link.get('href')
            title = link.get('title')

            epNorm = idSeries + '.Season' + str(season) + '.Episode' +\
                str(nbEpisode)
            epString = epNorm + ',' + title + ',' + imdbLink + ',' + '\n'
            seriesData += epString

    return seriesData


def writeData(series, data):
    """Writes characters information in `characters.txt`.

    Parameters
    ----------
    series : `str`
        Folder of the series.
    data : `str`
        Data to write.
    """

    with codecs.open("data/"+series+"/episodes.txt", "w", "utf-8") as chars:
        chars.write(data)


def main(args):
    sourceFile = args["SOURCEFILE"]
    onlyOne = args["SERIES"]
    if onlyOne:
        series = args["SERIES"]

    with open(sourceFile, 'r') as f:
        for line in f:
            sp = line.split(',')
            idSeries = sp[0]
            print(idSeries)
            isMovie = int(sp[4])

            if not isMovie and (not onlyOne or idSeries == series):
                link = sp[2]
                data = scrapPage(idSeries, link + "episodes")
                finalText = "".join(data)
                writeData(idSeries, finalText)


if __name__ == '__main__':
    args = docopt(__doc__)
    main(args)
