#! /bin/env python2.7

import argparse
import time

from bpm_detector import detect_bpm
from key_detector import detect_key
from separate_by_silence import separate_by_silence

# First, let's parse the command line options.
parser = argparse.ArgumentParser(description='Mashes a vocal track onto a instrumental track.')
parser.add_argument('vocal_input', metavar='vocal_input', help='The vocal input')
parser.add_argument('instrumental_input', metavar='instrumental_input', help='The instrumental input')

# Now we parse them and pick up the existing files or error out.
args = parser.parse_args()
vocal_track = args.vocal_input
instrumental_track = args.instrumental_input

# Debug
print args
print

print "Detecting vocal BPM..."
start = time.time()
vocal_bpm = detect_bpm(vocal_track)
print "Vocal BPM:", vocal_bpm
print "Elapsed seconds:", time.time() - start
print

print "Detecting instrumental BPM..."
start = time.time()
instrumental_bpm = detect_bpm(instrumental_track)
print "Instrumental BPM:", instrumental_bpm
print "Elapsed seconds:", time.time() - start
print

print "Detecting vocal key..."
start = time.time()
vocal_key = detect_key(vocal_track)
print "Vocal Key:", vocal_key
print "Elapsed seconds:", time.time() - start
print

print "Detecting instrumental key..."
start = time.time()
instrumental_key = detect_key(instrumental_track)
print "Instrumental Key:", instrumental_key
print "Elapsed seconds:", time.time() - start
print

print "Splitting vocal track by silence..."
start = time.time()
split_vocals = separate_by_silence(vocal_track, threshold=1, minimum_length_seconds=4.0)
print "Vocal sections (filename, length in seconds):", split_vocals
print "Elapsed seconds:", time.time() - start
print

print "Detecting key and BMP of vocal sections:"
vocal_sections = []
for fname, length in split_vocals:
    start = time.time()
    key = detect_key(fname)
    bpm = detect_bpm(fname)
    print fname + ":"
    print "  key:", key
    print "  BMP:", bpm
    print "  Elapsed seconds:", time.time() - start
    vocal_sections.append( (fname, length, key, bpm) )
print

print vocal_sections

