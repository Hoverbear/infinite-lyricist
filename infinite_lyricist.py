#! /bin/env python2.7

import argparse
import time
from pydub import AudioSegment
import random

from bpm_detector import detect_bpm
from key_detector import detect_key
from separate_by_silence import separate_by_silence

def parse_timecodes(timecode_str):
    start_times = []
    for st in timecode_str.split(','):
        parts = st.split(':')
        minutes = int(parts[0])
        seconds = int(parts[1])
        if len(parts) == 3:
            milliseconds = int(parts[2])
        else:
            milliseconds = 0
        total_milliseconds = (minutes * 60000) + (seconds * 1000) + milliseconds
        start_times.append(total_milliseconds)

    durations = [j-i for i, j in zip(start_times[:-1], start_times[1:])]

    timecodes = []
    for i in range(len(durations)):
        timecodes.append( {
            "start": start_times[i],
            "duration": durations[i]
        } )

    return timecodes

# First, let's parse the command line options.
parser = argparse.ArgumentParser(description='Mashes a vocal track onto a instrumental track.')
parser.add_argument('vocal_input', metavar='vocal_input', help='The vocal input')
parser.add_argument('instrumental_input', metavar='instrumental_input', help='The instrumental input')
parser.add_argument('instrumental_timecodes', metavar='instrumental_timecodes', help='Comma separated timecodes that mark the start of sections in the instrumental input. MM:SS:FFFF M=minutes, S=seconds, F=milliseconds (optional). Example: 00:00,00:08:00,00:15,00:23,00:32,00:40,00:47,00:56')

# Now we parse them and pick up the existing files or error out.
args = parser.parse_args()
vocal_track = args.vocal_input
instrumental_track = args.instrumental_input
timecodes = parse_timecodes(args.instrumental_timecodes)

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
    try:
        bpm = detect_bpm(fname)
    except:
        bpm = None
    print fname + ":"
    print "  key:", key
    print "  BMP:", bpm
    print "  Elapsed seconds:", time.time() - start
    if bpm:
        vocal_sections.append( (fname, length, key, bpm) )
print

print vocal_sections

instrumental_sound = AudioSegment.from_file(instrumental_track)

# Overlay the vocal sections over the instrumental
while (len(timecodes) > 0) and (len(vocal_sections) > 0):
    # Get a random section of the instrumental
    tc = timecodes.pop(random.randrange(len(timecodes)))

    print "timecode=", tc

    # Find a vocal section that fits in the duration of the instructional section
    any_can_fit = False
    vs_index = 0
    for vs in vocal_sections:
        vs_length_milliseconds = vs[1] * 1000
        if vs_length_milliseconds <= tc["duration"]:
            any_can_fit = True
            break
        vs_index += 1

    # No vocal section is short enough for this duration
    if not any_can_fit:
        print "vs_index:", vs_index
        print "len(vocal_sections):", len(vocal_sections)
        print "vs_index >= len(vocal_sections):", vs_index >= len(vocal_sections)
    #if vs_index >= len(vocal_sections):
        continue

    vocal = vocal_sections.pop(vs_index)
    print "vocal=", vocal
    vocal_sound = AudioSegment.from_file(vocal[0])

    # Overlay the audio
    instrumental_sound = instrumental_sound.overlay(vocal_sound, position=tc["start"])


instrumental_sound.export("output.wav", format="wav")


