# The Infinite Lyricist

A CSC-475 at the University of Victoria project by Andrew Hobden, Brody Holden, and Pascale Mendes.

## Prerequisites

You must be using Python 2.7.x (Not 3.x) and have a valid Marsyas installation with Swig bindings enabled in the build.

The `make` utility is required to run the quick demos.

Additionally, you should install the following via `pip`:

* `pydub`

## Quick Demos

Generate a mashup with vocals at the start of the instrumental track:

```bash
make dp-start
```

Generate a mashup with timecodes that have the same duration:

```bash
make dp-same-length-sections
```

Generate a mashup with timecodes that have different durations:

```bash
make dp-different-length-sections
```

The Infinite Lyricist has an element to randomness to it. It can generate two different mashups using the same parameters:

```bash
make dp-pair
```

Generate a mashup with many sections:

```bash
make dp-lots-of-sections
```

## Using Your Own Tracks

To combine one of the provided instrumental tracks with your own vocal file, run:

```bash
python infinite_lyricist.py \  
    your-vocal-track.wav \  
    instrumentals/wav/song-bass+guitar+synth+drums.wav \  
    00:08-00:14:500,00:15-00:22:500,00:23-00:31:500,00:32-00:39:500,00:40-00:46:500,00:47-00:56 \
    output.wav
```

Of course you can use your own instrumental track as well. Input files must be `.wav` files. We recommend stripping any ID3 tags off input tracks as we found they could contribute to unexpected output.

You must provide timecodes for when sections start and end in the instrumental track.

## Details of Using Your Own Tracks

Run with `./infinite-lyricist vocal.wav instrumental.wav timecodelist outputtrack`, where `outputtrack` is the filename of system output with the `.wav` extension, and `timecodelist` is a comma separated list of starts and ends times for the different sections of the instrumental track.

Timecode lists are in the form `start0-end0,start1-end1,...,startN-endN`, where

* `start` is a timecode denoting the start of section

* `end` is a timecode denoting the end of a section

* 0, 1, ..., N are the number of the sections

The format of `start` and `end` is `MM:SS:FFFF`, where:

* `MM` is one or two digits denoting minutes

* `SS` is one or two digits denoting seconds

* `FFF` is one to four digits denoting milliseconds

* Any number of leading zeros is permitted.
