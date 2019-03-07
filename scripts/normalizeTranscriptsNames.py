#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Usage: normalizeTranscriptsNames.py <id_series> [-s SEASON] [-e EPISODE]

Arguments:
    id_series    Id of the series

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
from pathlib import Path
import Plumcot as PC
import json


def automatic_alignment(id_series, id_ep, refs, hypsT):
    """Aligns IMDB character's names with transcripts characters names.

    Parameters
    ----------
    id_series : `str`
        Id of the series.
    id_ep : `str`
        Id of the episode.
    refs : `list`
        List of character's names from transcripts.
    hypsT : `list`
        List of character's names from IMDB.

    Returns
    -------
    names_dict : `dict`
        Dictionnary with character's names as key and normalized name as value.
    """

    names_dict = {}
    save_dict = {}

    hyps = hypsT[:]

    # Loading user previous matching names
    savePath = Path(__file__).parent / f"{id_series}.json"
    if os.path.isfile(savePath):
        with open(savePath, 'r') as f:
            save_dict = json.load(f)

        # Process data to take user matching names in account
        for trans_name in list(refs):
            if trans_name in save_dict:
                names_dict[trans_name] = save_dict[trans_name]
                refs.remove(trans_name)
                if save_dict[trans_name] in hyps:
                    hyps.remove(save_dict[trans_name])

    size = max(len(refs), len(hyps))
    min_size = min(len(refs), len(hyps))
    dists = np.ones([size, size])
    for i, ref in enumerate(refs):
        for j, hyp in enumerate(hyps):
            # Affine gap distance is configured to penalize gap openings,
            # regardless of the gap length to maximize matching between
            # firstName_lastName and firstName for example.
            dists[i, j] = affinegap.normalizedAffineGapDistance(
                    ref, hyp, matchWeight=0, mismatchWeight=1, gapWeight=0,
                    spaceWeight=1)
    # We use Hungarian algorithm which solves the "assignment problem" in a
    # polynomial time.
    row_ind, col_ind = linear_sum_assignment(dists)

    # Add names ignored by Hungarian algorithm when sizes are not equal
    for i, ref in enumerate(refs):
        if col_ind[i] < min_size:
            names_dict[ref] = hyps[col_ind[i]]
        else:
            names_dict[ref] = unknown_char(ref, id_ep)

    return names_dict


def normalize_names(id_series, season_number, episode_number):
    """Manual normalization.

    Parameters
    ----------
    id_series : `str`
        Id of the series.
    season_number : `str`
        The desired season number. If None, all seasons are processed.
    episode_number : `str`
        The desired episode_number. If None, all episodes are processed.

    Returns
    -------
    names_dict : `dict`
        Dictionnary with character's names as key and normalized name as value.
    """

    # Plumcot database object
    db = Plumcot()

    # Retrieve IMDB normalized character names
    imdb_chars_series = db.get_characters(id_series, season_number,
                                          episode_number)
    # Retrieve transcripts normalized character names
    trans_chars_series = db.get_transcript_characters(id_series, season_number,
                                                      episode_number)

    # Iterate over episode IMDB character names
    for id_ep, imdb_chars in imdb_chars_series.items():
        if id_ep not in trans_chars_series:
            continue
        trans_chars = trans_chars_series[id_ep]

        link = Path(PC.__file__).parent / 'data' / f'{id_series}'\
            / 'transcripts' / f'{id_ep}.txt'
        # If episode has already been processed
        if os.path.isfile(link):
            exists = f"{id_ep} already processed. [y] to processe, n to skip: "
            co = input(exists)
            if co == 'n':
                continue

        # Get automatic alignment as a dictionnary
        dic_names = automatic_alignment(id_series, id_ep, trans_chars,
                                        imdb_chars)
        save = True

        # User input loop
        while True:
            print(f"----------------------------\n{id_ep}. Here is the list "
                  "of normalized names from IMDB: ")
            names = ""
            for name in imdb_chars:
                names += name + ', '
            print(names[:-2], '\n')

            print("Automatic alignment:")
            for name, norm_name in dic_names.items():
                print(name, ' -> ', norm_name)

            request = input("\nType the name of the character which you want "
                            "to change normalized name (end to save, stop "
                            "to skip): ")
            # Stop and save
            if request == "end":
                break
            # Stop without saving
            if request == "stop" or request == "skip":
                save = False
                break
            # Wrong name
            if request not in dic_names:
                print("This name doesn't match with any characters.\n")
            else:
                new_name = input("\nType the new character's name "
                                 "(unk for unknown character): ")
                # Unknown character
                if new_name == "unk" or not new_name:
                    new_name = unknown_char(request, id_ep)
                dic_names[request] = new_name

        # Save changes and create .txt file
        if save:
            save_matching(id_series, dic_names)
            db.save_normalized_names(id_series, id_ep, dic_names)


def unknown_char(char_name, id_ep):
    """Transforms character name into unknown version."""

    return f"{char_name}#unknown#{id_ep}"


def save_matching(id_series, dic_names):
    """Saves user matching names

    Parameters
    ----------
    id_series : `str`
        Id of the series.
    dic_names : `dict`
        Dictionnary with matching names (transcript -> normalized).
    """

    save_dict = {}
    savePath = Path(__file__).parent / f"{id_series}.json"
    if os.path.isfile(savePath):
        with open(savePath, 'r') as f:
            save_dict = json.load(f)

    for name_trans, name_norm in dic_names.items():
        if "#unknown" not in name_norm:
            save_dict[name_trans] = name_norm

    with open(Path(__file__).parent / f"{id_series}.json", 'w') as f:
        json.dump(save_dict, f)


def main(args):
    id_series = args["<id_series>"]
    season_number = args['-s']
    if season_number:
        season_number = f"{int(season_number):02d}"
    episode_number = args['-e']
    if episode_number:
        episode_number = f"{int(episode_number):02d}"

    normalize_names(id_series, season_number, episode_number)


if __name__ == '__main__':
    args = docopt(__doc__)
    main(args)
