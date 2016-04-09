#! /bin/env python2.7

import argparse
import time

from bpm_detector import detect_bpm
from key_detector import detect_key

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

print "Proccessing vocal BPM..."
start = time.time()
vocal_bpm = detect_bpm(vocal_track)
print "Vocal BPM:", vocal_bpm
print "Elapsed seconds:", time.time() - start
print

print "Processing instrumental BPM..."
start = time.time()
instrumental_bpm = detect_bpm(instrumental_track)
print "Instrumental BPM:", instrumental_bpm
print "Elapsed seconds:", time.time() - start
print

print "Processing vocal key..."
start = time.time()
vocal_key = detect_key(vocal_track)
print "Vocal Key:", vocal_key
print "Elapsed seconds:", time.time() - start
print

print "Processing instrumental key..."
start = time.time()
instrumental_key = detect_key(instrumental_track)
print "Instrumental Key:", instrumental_key
print "Elapsed seconds:", time.time() - start
print

