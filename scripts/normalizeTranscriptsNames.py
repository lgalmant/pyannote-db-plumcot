#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Usage: extractionTool.py IDSERIES [-s SEASON] [-e EPISODE]

Arguments:
    IDSERIES     Id of the series

Options:
    -s SEASON    Season number to iterate on (all seasons if not specified)
    -e EPISODE   Episode number (all episodes of the season if not specified)

"""

import pyannote.database
from docopt import docopt
from Plumcot import Plumcot
import affinegap
import numpy as np
from scipy.optimize import linear_sum_assignment
import os.path


def automaticAlignment(refs, hyps):
    """Aligns IMDB character's names with transcripts characters names.

    Parameters
    ----------
    refs : `list`
        List of character's names from transcripts.
    hyps : `list`
        List of character's names from IMDB.

    Returns
    -------
    namesDict : `dict`
        Dictionnary with character's names as key and normalized name as value.
    """

    namesDict = {}
    size = max(len(refs), len(hyps))
    min_size = min(len(refs), len(hyps))
    dists = np.ones([size, size])
    for i, ref in enumerate(refs):
        for j, hyp in enumerate(hyps):
            dists[i, j] = affinegap.normalizedAffineGapDistance(
                    ref, hyp, matchWeight=0, mismatchWeight=1, gapWeight=0,
                    spaceWeight=1)
    row_ind, col_ind = linear_sum_assignment(dists)

    for i, ref in enumerate(refs):
        if col_ind[i] < min_size:
            namesDict[ref] = hyps[col_ind[i]]
        else:
            namesDict[ref] = ""

    return namesDict


def normalizeNames(idSeries, seasonNumber, episodeNumber):
    """Manual normalization.

    Parameters
    ----------
    idSeries : `str`
        Id of the series.
    seasonNumber : `str`
        The desired season number. If None, all seasons are processed.
    episodeNumber : `str`
        The desired episodeNumber. If None, all episodes are processed.

    Returns
    -------
    namesDict : `dict`
        Dictionnary with character's names as key and normalized name as value.
    """

    db = Plumcot()

    tbbt = db.get_protocol('Collection', idSeries)

    imdbCharsSeries = tbbt.getCharacters(seasonNumber, episodeNumber)
    transCharsSeries = tbbt.getTranscriptCharacters(seasonNumber,
                                                    episodeNumber)

    for idEp, imdbChars in imdbCharsSeries.items():
        if idEp not in transCharsSeries:
            continue
        transChars = transCharsSeries[idEp]

        link = f"../Plumcot/data/{idSeries}/transcripts/{idEp}.txt"
        if os.path.isfile(link):
            exists = f"{idEp} already processed. [y] to processe, n to skip: "
            co = input(exists)
            if co == 'n':
                continue

        dicNames = automaticAlignment(transChars, imdbChars)
        save = True

        while True:
            print(f"----------------------------\n{idEp}. Here is the list "
                  "of normalized names from IMDB: ")
            names = ""
            for name in imdbChars:
                names += name + ', '
            print(names[:-2], '\n')

            print("Automatic alignment:")
            for name, normName in dicNames.items():
                print(name, ' -> ', normName)

            request = input("\nType the name of the character which you want "
                            "to change normalized name (end to save, stop "
                            "to skip): ")
            if request == "end":
                break
            if request == "stop" or request == "skip":
                save = False
                break
            if request not in dicNames:
                print("This name doesn't match with any characters.\n")
            else:
                newName = input("\nType the new character's name "
                                "(unk for unknown character): ")
                if newName == "unk" or not newName:
                    newName = f"{request}#unknown#{idEp}"
                dicNames[request] = newName

        if save:
            tbbt.saveNormalizedNames(idEp, dicNames)


def main(args):
    idSeries = args["IDSERIES"]
    seasonNumber = args['-s']
    if seasonNumber:
        seasonNumber = f"{int(seasonNumber):02d}"
    episodeNumber = args['-e']
    if episodeNumber:
        episodeNumber = f"{int(episodeNumber):02d}"

    normalizeNames(idSeries, seasonNumber, episodeNumber)


if __name__ == '__main__':
    args = docopt(__doc__)
    main(args)
