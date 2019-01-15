# How to contribute

1. Clone the repository.
2. Make changes.
3. Open a pull request.

Make sure all files are UTF8.

Make sure to follow conventions and file formats described in this document.

Open an issue if something is not clear -- we will decide on a solution and update this document accordingly.

# series.txt

`series.txt` contains one line per TV (or movie) series.
Each line provides a (CamelCase) identifier, a full name, a link to its IMDB.com page, a link to its TV.com page, and a boolean set to 1 if the line corresponds to a movie.

```
$ cat series.txt
TheBigBangTheory,The Big Bang Theory,https://www.imdb.com/title/tt0898266/,http://www.tv.com/shows/the-big-bang-theory/,0
```

## One sub-directory per series / movies

For each entries in `series.txt`, there is a corresponding sub-directory called after its CamelCase identifier into the scripts folder and into the data folder.

# Scripts

All the scripts need to put on the `scripts` folder into the corresponding serie's name.
We assume that we launch all the script from this root directory where README is stored.

```
characters.py
credits.py
alignment.py
(entities.py)
TheBigBangTheory/
  transcripts.py
```

# Data

All the clean data with be put at the root directory of the serie into a `.txt` file.
We also download all the webpages where we extract the informations into the `html_pages` folder into the corresponding task folder.

```
TheBigBangTheory/
  characters.txt
  credits.txt
  transcripts.txt
  alignment.txt
  entities.txt
  html_pages/
    characters/
    credits/
    transcripts/
      season01.episode01.html
      season01.episode02.html
      season01.episode03.html
    alignment/
    entities/
```

### `characters.txt`

This file provides the list of characters (gathered from TV.com or IMDB.com). It contains one line per character with the following information: underscore-separated identifier, actor's normalized name, character's full name, actor's full name, IMDB.com character page.

```
leonard_hofstadter,johnny_galecki,Leonard Hofstadter,Johnny Galecki,https://www.imdb.com/title/tt0898266/characters/nm0301959
```

The creation of this file should be automated as much as possible. Ideally, a script would take `series.txt` as input and generate all `characters.txt` file at once (or just one if an optional series identifier is provided)
`-v fileName` creates a file with `characters.txt` to easily verify the characters normalization.

```bash
python characters.py series.txt TheBigBangTheory -v normVerif.txt
```

Note: Leo is in charge of creating this script.

### `episodes.txt`

This file provides the list of episodes (gathered from TV.com or IMDB.com). It contains one line per episode with the following information: unique episode identifier, name of the episode, IMDB.com episode page, TV.com episode page.

```
TheBigBangTheory.Season01.Episode01,Pilot,https://www.imdb.com/title/tt0775431/,http://www.tv.com/shows/the-big-bang-theory/pilot-939386/
```

The creation of this file should be automated as much as possible. Ideally, a script would take `series.txt` as input and generate all `episodes.txt` file at once (or just one if an optional series identifier is provided)

```bash
python episodes.py series.txt TheBigBangTheory
```

For movies, we can use something like `HarryPotter.Episode01` as "episode" unique identifier.

Note: Leo can probably do this script.

### `credits.txt`

This file provides the list of characters credited in each episode. It contains one line per episode. Each episode is denoted by its normalized identifier (e.g. `TheBigBangTheory.Season01.Episode01`).

The line starts with one field for the episode and then the list of credited characters (in alphabetical order, usign their underscore-separated identifier).

For instance, the line below tells that 3 characters appear in episode 1 of season 1 of The Big Bang Theory

```
TheBigBangTheory.Season01.Episode01 leonard_hofstadter penny sheldon_cooper
```

The creation of this file should be automated as much as possible. Ideally, a script would take `series.txt` and `characters.txt` as input and generate all `credits.txt` at once (or just one if an optional series identifier is provided)

```bash
python credits.py series.txt TheBigBangTheory/characters.txt
```

Note: Leo is in charge of creating this script

### `transcripts.txt`

This file provides the manual transcripts of all episodes in `episodes.txt`. It contains one line per speech turn.

The expected file format is the following: unique series identifier, unique character identifier, followed by the actual transcription.

```
TheBigBangTheory.Season01.Episode01 sheldon_cooper How are you, Leonard?
TheBigBangTheory.Season01.Episode01 leonard_hoffstadter Good, and you?
```

It is unlikely that we will be able to code *one script to rule them all* generic enough to process all series. It will most likely need a lot of manual cleaning.

This is why we will start by focusing on a sub-sample of the (eventually bigger) corpus.

Note: here is a "who is doing what" split

* Harry Potter : Ruiqing
* The Big Bang Theory : Leo
* Lost : Benjamin
* Game of Thrones : Aman
* Buffy the Vampire Slayer : Hervé
* Battlestar Galactica : Benjamin
* The Good Wife : Claude

### `alignment.stm`

This file provides the forced-aligned transcripts of all episodes in episodes.txt. It contains one line per word using the [`stm`](http://www1.icsi.berkeley.edu/Speech/docs/sctk-1.2/infmts.htm#stm_fmt_name_0) or [`ctm`](https://web.archive.org/web/20170119114252/http://www.itl.nist.gov/iad/mig/tests/rt/2009/docs/rt09-meeting-eval-plan-v2.pdf) file format.

```
TheBigBangTheory.Season01.Episode01 1 sheldon_cooper start_time end_time <> How
TheBigBangTheory.Season01.Episode01 1 sheldon_cooper start_time end_time <> are
TheBigBangTheory.Season01.Episode01 1 sheldon_cooper start_time end_time <> you
TheBigBangTheory.Season01.Episode01 1 sheldon_cooper start_time end_time <> ,
TheBigBangTheory.Season01.Episode01 1 sheldon_cooper start_time end_time <> Leonard
TheBigBangTheory.Season01.Episode01 1 sheldon_cooper start_time end_time <> ?
```

Note : Benjamin and Hervé will take care of it.

### `entities.txt`

This file contains named entities annotation of `alignment.stm`.

The proposed file format is the following:

```
word_id file_id channel_id speaker_id start_time end_time <> word named_entity_type normalized_name coreference_id
```

```
1 TheBigBangTheory.Season01.Episode01 1 sheldon_cooper start_time end_time <> How     <>     <>                  <>
2 TheBigBangTheory.Season01.Episode01 1 sheldon_cooper start_time end_time <> are     <>     <>                  <>
3 TheBigBangTheory.Season01.Episode01 1 sheldon_cooper start_time end_time <> you     <>     <>                  5/6
4 TheBigBangTheory.Season01.Episode01 1 sheldon_cooper start_time end_time <> ,       <>     <>                  <>
5 TheBigBangTheory.Season01.Episode01 1 sheldon_cooper start_time end_time <> Leonard PERSON leonard_hofstadter  <>
6 TheBigBangTheory.Season01.Episode01 1 sheldon_cooper start_time end_time <> Hofstadter PERSON leonard_hofstadter  <>
7 TheBigBangTheory.Season01.Episode01 1 sheldon_cooper start_time end_time <> ?       <>     <>                  <>
```

```
1 TheBigBangTheory.Season01.Episode01 1 sheldon_cooper start_time end_time <> How     <>     <>                  <>
2 TheBigBangTheory.Season01.Episode01 1 sheldon_cooper start_time end_time <> are     <>     <>                  <>
3 TheBigBangTheory.Season01.Episode01 1 sheldon_cooper start_time end_time <> you     <>     <>                  5/7
4 TheBigBangTheory.Season01.Episode01 1 sheldon_cooper start_time end_time <> ,       <>     <>                  <>
5 TheBigBangTheory.Season01.Episode01 1 sheldon_cooper start_time end_time <> Sheldon PERSON sheldon_cooper  <>
6 TheBigBangTheory.Season01.Episode01 1 sheldon_cooper start_time end_time <> and <> <>  <>
7 TheBigBangTheory.Season01.Episode01 1 sheldon_cooper start_time end_time <> Leonard PERSON leonard_hofstadter  <>
8 TheBigBangTheory.Season01.Episode01 1 sheldon_cooper start_time end_time <> ?       <>     <>                  <>
```

Note: Leo has a script to do that, though the (automatic) output will need a manual correction pass.


### scene / narrative stuff

Aman will come up with a file format and data.
