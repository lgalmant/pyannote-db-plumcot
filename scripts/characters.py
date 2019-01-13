#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import codecs #for encoding the data as utf-8
import sys
import unidecode
import re

"""
Normalizes characters and actors names.
"""
def normalizeName(fullName):
    fullName = fullName.lower()
    
    fullName = fullName.split('\n')[0].strip()
    fullName = re.sub(r'\([^()]*\)', '', fullName)#Remove parenthesis
    fullName = re.sub(r"\'[^'']*\'", '', fullName)#Remove commas
    fullName = unidecode.unidecode(fullName)#Remove diacritics
    fullName = fullName.replace(' ', '_')
    fullName = re.sub(r'\W+', '', fullName)#Remove all non-alphanumerics characters (except _)
    fullName = re.sub(r"[_]+", '_', fullName)
    return fullName

"""
Takes the IMDB page of a series and extracts the characters information.
Returns an array with all characters information.
"""
def scrapPage(pageIDMB):
    urlIDMB=requests.get(pageIDMB).text
    soup=BeautifulSoup(urlIDMB,'lxml')
    seriesTable=soup.find('table',{'class':'cast_list'}).find_all('tr')
    
    cast = []
    
    for char in seriesTable:
        charInfo = char.find_all('td')
        if len(charInfo) == 4:
            actorName = charInfo[1].text.strip()
            
            charNorm = charInfo[3].find('a')
            charLink = ""
            if not charNorm:
                charName = charInfo[3].text.split('\n')[0].strip()
            elif charNorm.get('href') != "#":
                charName = charNorm.text.strip()
                charLink = "https://www.imdb.com" + charNorm.get('href').strip().split('?')[0]
            else:
                charName = charNorm.previous_sibling.split('\n')[0].strip()
            
            normActorName = normalizeName(actorName)
            normCharName = normalizeName(charName)
            if normCharName and normActorName:
                cast.append((normCharName, normActorName, charName, actorName, charLink))
                
    return cast

"""
Returns the string corresponding to the pageIDMB file
"""
def getData(pageIDMB):
    textFile = []
    cast = scrapPage(pageIDMB)
    
    for normCharName, normActorName, charName, actorName, charLink in cast:
        text = normCharName + ',' + normActorName + ',' + charName + ',' + actorName + ',' + charLink + '\n'
        text = text.encode('utf-8')
        textWrite = text.decode('utf-8')
        textFile.append(textWrite)
            
    return textFile


def writeData(series, data):
    with codecs.open("data/"+series+"/characters.txt","w","utf-8") as chars:
        chars.write(data)

    
def main():
    sourceFile = sys.argv[1]
    onlyOne = len(sys.argv) > 2
    if onlyOne:
        series = sys.argv[2]
    
    with open(sourceFile, 'r') as f:
        for line in f:
            sp = line.split(',')
            idSeries = sp[0]
            isMovie = int(sp[4])
            
            if not onlyOne or idSeries == series:
                if not isMovie:
                    link = sp[2]
                    finalText = "".join(getData(link + "fullcredits/"))
                    writeData(idSeries, finalText)
                        
                else:
                    sagaChars = []
                    with open(idSeries+"/episodes.txt", 'r') as fMovie:
                        for lineMovie in fMovie:
                            link = lineMovie.split(',')[2]
                            movieChars = getData(link + "fullcredits/")
                            sagaChars.extend(movieChars)
                    #sagaChars = list(set(sagaChars)) to remove duplicates
                    finalText = "".join(sagaChars)
                    writeData(idSeries, finalText)
            
        
if __name__ == '__main__':
    main()