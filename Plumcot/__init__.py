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

    def __init__(self, preprocessors={}, **kwargs):
        super().__init__(preprocessors=preprocessors, **kwargs)

        # load list of series
        path = Path(__file__).parent / 'data/series.txt'
        names = ['short_name', 'human_readable', 'imdb', 'tv', 'movies']
        with open(path, mode='r') as fp:
            data = pd.read_csv(fp, sep=',', header=None, names=names,
                                 converters={'movies': bool})

        # for each series, create and register a collection protocol
        # used to iterate over all episodes in chronological order
        for series in data.itertuples():
            Klass = type(series.short_name, (BaseEpisodes, ),
                         {'SERIES': series.short_name})
            self.register_protocol('Collection', series.short_name, Klass)
