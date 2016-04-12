# The Infinite Lyricist

A CSC-475 at the University of Victoria project by Andrew Hobden, Brody Holden, and Pascale Mendes.

## Prerequisites

You must be using Python 2.7.x (Not 3.x) and have a valid Marsyas installation with Swig bindings enabled in the build.

Additionally, you should install the following via `pip`:

* `pydub`

## Quick Run

Combine a provided instrumental track with your own vocal file by running:

```bash
python infinite_lyricist.py \  
    your-vocal-track.wav \  
    song/wav/song-bass+guitar+synth+drums.wav \  
    00:08-00:14:5000,00:15-00:22:5000,00:23-00:31:5000,00:32-00:39:500,00:40-00:46:5000,00:47-00:56
```

## Details of Running

Run with `./infinite-lyricist vocal.wav instrumental.wav timecodelist`, where `timecodelist` is a comma separated list of starts and ends times for the different sections of the instrumental track.

Timecode lists are in the form `start0-end0,start1-end1,...,startN-endN`, where

* `start` is a timecode denoting the start of section

* `end` is a timecode denoting the end of a section

* 0, 1, ..., N are the number of the sections

The format of `start` and `end` is `MM:SS:FFFF`, where:

* `MM` is one or two digits denoting minutes

* `SS` is one or two digits denoting seconds

* `FFFF` is one to four digits denoting milliseconds

* Any number of leading zeros is permitted.
