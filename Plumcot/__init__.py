#!/usr/bin/env python
# encoding: utf-8

# The MIT License (MIT)

# Copyright (c) 2019 CNRS

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# AUTHORS
# Hervé BREDIN - http://herve.niderb.fr


from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

from pyannote.database import Database
from pyannote.database.protocol import CollectionProtocol
from pathlib import Path
import pandas as pd
import os
import glob


class BaseEpisodes(CollectionProtocol):
    """Base class of collection protocols"""

    def files_iter(self):
        """Iterate over all episodes of a series"""
        path = Path(__file__).parent / f'data/{self.SERIES}/episodes.txt'
        with open(path, mode='r') as fp:
            lines = fp.readlines()
        for line in lines:
            uri = line.split(',')[0]
            yield {'uri': uri, 'database': 'Plumcot'}


class Plumcot(Database):
    """Plumcot database"""

    def getCharacters(self, seriesId, numSeason=None, numEpisode=None,
                      fullName=False):
        """Get IMDB character's names list.

        Parameters
        ----------
        seriesId : `str`
            Id of the series.
        NumSeason : `str`
            The desired season number. If None, all seasons are processed.
        numEpisode : `str`
            The desired episodeNumber. If None, all episodes are processed.
        fullName : `bool`
            Return id names if False, real names if True.

        Returns
        -------
        namesDict : `dict`
            Dictionnary with episodeId as key and list of IMDB names as value.
        """

        charactersDict = {}

        epName = seriesId
        if numSeason:
            epName += f".Season{numSeason}"
            if numEpisode:
                epName += f".Episode{numEpisode}"

        parent = Path(__file__).parent
        creditsFile = parent / f'data/{seriesId}/credits.txt'
        charactersFile = parent / f'data/{seriesId}/characters.txt'

        charactersListCredits = []

        with open(creditsFile, mode='r', encoding="utf8") as f:
            for line in f:
                lineSplit = line.split(',')
                if epName in lineSplit[0]:
                    charactersListCredits.append(lineSplit)

        charactersList = []
        nameId = 1 if fullName else 0

        with open(charactersFile, mode='r', encoding="utf8") as f:
            for line in f:
                charactersList.append(line.split(',')[nameId])

        for episode in charactersListCredits:
            episodeName = episode[0]
            charactersNameList = []

            for idCharacter, character in enumerate(episode[1:]):
                if int(character):
                    charactersNameList.append(charactersList[idCharacter])

            charactersDict[episodeName] = charactersNameList

        return charactersDict

    def getTranscriptCharacters(self, seriesId, numSeason=None,
                                numEpisode=None):
        """Get transcripts character's names list from .temp transcripts files.

        Parameters
        ----------
        seriesId : `str`
            Id of the series.
        NumSeason : `str`
            The desired season number. If None, all seasons are processed.
        numEpisode : `str`
            The desired episodeNumber. If None, all episodes are processed.

        Returns
        -------
        namesDict : `dict`
            Dictionnary with episodeId as key and list of transcript
            names as value.
        """

        charactersDict = {}

        epTemplate = seriesId
        if numSeason:
            epTemplate += f".Season{numSeason}"
            if numEpisode:
                epTemplate += f".Episode{numEpisode}"

        parent = Path(__file__).parent
        tempTranscripts = glob.glob(f"{parent}/data/{seriesId}/transcripts/"
                                    f"{epTemplate}*.temp")

        for file in tempTranscripts:
            with open(file, mode='r', encoding="utf8") as epFile:
                characters = set()
                for line in epFile:
                    characters.add(line.split()[0])
            epName = file.split("/")[-1].replace('.temp', '')
            charactersDict[epName] = list(characters)

        return charactersDict

    def saveNormalizedNames(self, seriesId, idEp, dicNames):
        """Saves new transcripts files as .txt with normalized names.

        Parameters
        ----------
        seriesId : `str`
            Id of the series.
        seriesId : `str`
            Id of the episode.
        dicNames : `dict`
            Dictionnary with matching names (transcript -> normalized).
        """

        parent = Path(__file__).parent
        transFolder = f"{parent}/data/{seriesId}/transcripts/"

        fileText = ""
        with open(transFolder + idEp + '.temp', mode='r',
                  encoding="utf8") as epFile:
            for line in epFile:
                lineSp = line.split()
                lineSp[0] = dicNames[lineSp[0]]
                fileText += " ".join(lineSp) + '\n'

        with open(transFolder + idEp + '.txt', mode='w',
                  encoding="utf8") as epFile:
            epFile.write(fileText)

    def __init__(self, preprocessors={}, **kwargs):
        super().__init__(preprocessors=preprocessors, **kwargs)

        # load list of series
        path = Path(__file__).parent / 'data/series.txt'
        names = ['short_name', 'human_readable', 'imdb', 'tv', 'movies']
        with open(path, mode='r') as fp:
            data = pd.read_csv(fp, sep=',', header=None,
                               names=names, converters={'movies': bool})

        # for each series, create and register a collection protocol
        # used to iterate over all episodes in chronological order
        for series in data.itertuples():
            Klass = type(series.short_name, (BaseEpisodes, ),
                         {'SERIES': series.short_name})
            self.register_protocol('Collection', series.short_name, Klass)
