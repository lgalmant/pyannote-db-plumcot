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

    def get_characters(self, id_series, season_number=None,
                       episode_number=None, full_name=False):
        """Get IMDB character's names list.

        Parameters
        ----------
        id_series : `str`
            Id of the series.
        season_number : `str`
            The desired season number. If None, all seasons are processed.
        episode_number : `str`
            The desired episodeNumber. If None, all episodes are processed.
        full_name : `bool`
            Return id names if False, real names if True.

        Returns
        -------
        namesDict : `dict`
            Dictionnary with episodeId as key and list of IMDB names as value.
        """

        # Template for processed episodes
        ep_name = id_series
        if season_number:
            ep_name += f".Season{season_number}"
            if episode_number:
                ep_name += f".Episode{episode_number}"

        parent = Path(__file__).parent
        credits_file = parent / f'data/{id_series}/credits.txt'
        characters_file = parent / f'data/{id_series}/characters.txt'

        # Get credits as list
        characters_list_credits = []
        with open(credits_file, mode='r', encoding="utf8") as f:
            for line in f:
                line_split = line.split(',')
                if ep_name in line_split[0]:
                    characters_list_credits.append(line_split)

        # Get character names as list
        characters_list = []
        id_name = 1 if full_name else 0
        with open(characters_file, mode='r', encoding="utf8") as f:
            for line in f:
                characters_list.append(line.split(',')[id_name])

        # Create character's list by episode
        characters_dict = {}
        for episode in characters_list_credits:
            episode_name = episode[0]
            characters_name_list = []

            for id_character, character in enumerate(episode[1:]):
                if int(character):
                    characters_name_list.append(characters_list[id_character])

            characters_dict[episode_name] = characters_name_list

        return characters_dict

    def get_transcript_characters(self, id_series, season_number=None,
                                  episode_number=None):
        """Get transcripts character's names list from .temp transcripts files.

        Parameters
        ----------
        id_series : `str`
            Id of the series.
        season_number : `str`
            The desired season number. If None, all seasons are processed.
        episode_number : `str`
            The desired episodeNumber. If None, all episodes are processed.

        Returns
        -------
        namesDict : `dict`
            Dictionnary with episodeId as key and dictionnary as value with
            transcripts as key and number of speech turns as value
        """

        # Template for processed episodes
        ep_template = id_series
        if season_number:
            ep_template += f".Season{season_number}"
            if episode_number:
                ep_template += f".Episode{episode_number}"

        parent = Path(__file__).parent
        temp_transcripts = glob.glob(f"{parent}/data/{id_series}/transcripts/"
                                     f"{ep_template}*.temp")

        # Get transcript character names list by episode
        characters_dict = {}
        for file in temp_transcripts:
            with open(file, mode='r', encoding="utf8") as ep_file:
                characters = {}
                for line in ep_file:
                    charac = line.split()[0]
                    if charac not in characters:
                        characters[charac] = 1
                    else:
                        characters[charac] += 1
            # Get episode name
            ep_name = file.split("/")[-1].replace('.temp', '')
            characters_dict[ep_name] = characters

        return characters_dict

    def save_normalized_names(self, id_series, id_ep, dic_names):
        """Saves new transcripts files as .txt with normalized names.

        Parameters
        ----------
        id_series : `str`
            Id of the series.
        id_ep : `str`
            Id of the episode.
        dic_names : `dict`
            Dictionnary with matching names (transcript -> normalized).
        """

        parent = Path(__file__).parent
        trans_folder = f"{parent}/data/{id_series}/transcripts/"

        # Read .temp file and replace speaker names
        file_text = ""
        with open(trans_folder + id_ep + '.temp', mode='r',
                  encoding="utf8") as ep_file:
            for line in ep_file:
                line_split = line.split()
                line_split[0] = dic_names[line_split[0]]
                file_text += " ".join(line_split) + '\n'

        # Write changes
        with open(trans_folder + id_ep + '.txt', mode='w',
                  encoding="utf8") as ep_file:
            ep_file.write(file_text)

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
