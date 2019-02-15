#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import unidecode
import re

repo = "/people/galmant/tbbt/"

def normalizeName(fullName):
    """Normalizes characters and actors names.

    Removes parenthesis, commas, diacritics and non-alphanumerics characters,
    except _.

    Parameters
    ----------
    fullName : `str`
        Full name (of a character or a person).

    Returns
    -------
    normName : `str`
        Normalized name.
    """

    fullName = fullName.lower()

    fullName = fullName.split('\n')[0].strip()
    fullName = re.sub(r'\([^()]*\)', '', fullName)  # Remove parenthesis
    fullName = re.sub(r"\'[^'']*\'", '', fullName)  # Remove commas
    fullName = unidecode.unidecode(fullName)  # Remove diacritics
    fullName = fullName.replace(' ', '_')
    # Remove all non-alphanumerics characters (except _)
    fullName = re.sub(r'\W+', '', fullName)
    fullName = re.sub(r"[_]+", '_', fullName)
    return fullName

fullText = ""

seasons = ['Season01', 'Season02', 'Season03', 'Season04', 'Season05', 'Season06' ,'Season07' ,'Season08' ,'Season09' ,'Season10']

for season in seasons:
    for episode in os.listdir(repo + season):
        if "TheBigBangTheory" in episode:
            fname = repo + season + "/" + episode
            writ = episode
        else:
            digits = [int(d) for d in episode.split('-') if d.isdigit()]
            sN, eN = digits[0], digits[1]
            sN = f"Season{sN:02d}"
            eN = f"Episode{eN:02d}"
            
            epi = "TheBigBangTheory." + sN + '.' + eN
            writ = epi
            fname = repo + season + "/" + episode
        with open(fname, 'r') as ep:
            text = ""
            for line in ep:
                lSplit = line.split(": ")
                if len(lSplit) == 2:
                    speaker, phrase = normalizeName(lSplit[0]), lSplit[1]
                    if speaker != "scene":
                        text += writ + ' ' + speaker + ' ' + phrase
        with open('../Plumcot/data/TheBigBangTheory/transcripts/' + writ + '.temp', 'w') as epis:
            epis.write(text)
        fullText += text
                        
with open('../Plumcot/data/TheBigBangTheory/transcripts.txt', 'w') as ep:
    ep.write(fullText)


    