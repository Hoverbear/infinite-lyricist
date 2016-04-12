#! /bin/env python2.7
import argparse
import time
from pydub import AudioSegment
import random
import wave

from WavFileWriter import WavFileWriter

from bpm_detector import detect_bpm
from key_detector import detect_key
from separate_by_silence import separate_by_silence
from phase_vocoder import time_shift
from phase_vocoder import pitch_shift
from fix_header import fix_header

def parse_timecode(timecode_str):
    """
    Parse a timecode.

    The timecode format:
        MM:SS:FFFF, where:
            MM is one or two digits denoting minutes
            SS is one or two digits denoting seconds
            FFFF is one to four digits denoting milliseconds

            Any number of leading zeros is permitted.

    * timecode_str: A string containing a timecode.

    Returns the milliseconds represented by the timecode.
    """
    parts = timecode_str.split(':')
    minutes = int(parts[0])
    seconds = int(parts[1])
    if len(parts) == 3:
        milliseconds = int(parts[2])
    else:
        milliseconds = 0
    total_milliseconds = (minutes * 60000) + (seconds * 1000) + milliseconds
    return total_milliseconds

def parse_timecodes(timecode_str):
    """
    Parse a comma separated list of timecodes.
    Format:
        start0-end0,start1-end1,...,startN-endN, where
            start is a timecode denoting the start of section
            end is a timecode denoting the end of a section
            0, 1, ..., N are the number of sections
            The format start and end timecodes are as defined in parse_timecode().

    * timecode_str: A string of comma separated time codes.

    Returns the parsed timecodes as a list of dicts with "start" and "duration" as keys.
    """
    start_times = []
    end_times = []

    for st in timecode_str.split(','):
        start, end = st.split('-')
        start, end = parse_timecode(start), parse_timecode(end)
        start_times.append(start)
        end_times.append(end)

    durations = [j-i for i, j in zip(start_times, end_times)]

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
parser.add_argument('instrumental_timecodes', metavar='instrumental_timecodes', help="""
    Comma separated timecodes that mark the start of sections in the instrumental input.
    Each timecode consists of a start timestamp and an end timestamp separate by a dash.
    The timestamp format is:
        MM:SS:FFFF M=minutes, S=seconds, F=milliseconds (optional).
    Example timecodes for the provided song:
        00:08-00:14:5000,00:15-00:22:5000,00:23-00:31:5000,00:32-00:39:500,00:40-00:46:5000,00:47-00:56
""")

# Now we parse them and pick up the existing files or error out.
args = parser.parse_args()
vocal_track = args.vocal_input
instrumental_track = args.instrumental_input
timecodes = parse_timecodes(args.instrumental_timecodes)

# Debug
print args
print

print "Detecting instrumental BPM..."
start = time.time()
instrumental_bpm = detect_bpm(instrumental_track)
print "Instrumental BPM:", instrumental_bpm
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

print

print "Matching vocal tempos to instrumental tempo:"

# Get first clip and initialize iterator
wav_handle = wave.open(split_vocals[0][0], 'r')
wfw = WavFileWriter("/tmp/vocal_time-shift.wav", wav_handle.getparams())

v_s = list(vocal_sections)
bpm_matched_vocals = []
for i in range(len(v_s)):
    start = time.time()
    bpm = v_s[i][3]

    #find closest integer multiple of bpm to the instrumental bpm
    reg = abs(instrumental_bpm-bpm)
    double = abs(instrumental_bpm-(2*bpm))
    half = abs((2*instrumental_bpm) - bpm)
    difference = min(reg, double, half)

    if(difference == double):
        tempochange = 2*bpm/float(instrumental_bpm)
        bpm = bpm*2
    elif(difference == half):
        tempochange = bpm/float(2*instrumental_bpm)
        bpm = bpm/2
    else:
        tempochange = bpm/float(instrumental_bpm)

    ipol = int(16/tempochange)
    outfile = wfw.get_next_name()
    bpm_matched_vocals.append(time_shift(I=ipol, music_file=fname, outfile=outfile))
    length = fix_header(outfile)
    vocal_sections[i] = (outfile, length, vocal_sections[i][2], bpm/tempochange)
    print outfile + ":"
    print " bpm:", vocal_sections[i][3]
    print " length:", vocal_sections[i][1]
    print " Elapsed Seconds:", time.time() - start

wav_handle.close()

print

print vocal_sections



instrumental_sound = AudioSegment.from_wav(instrumental_track)

# Overlay the vocal sections over the instrumental
i = 0
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
            print "There is a clip match"
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
    vocal_sound = AudioSegment.from_wav(vocal[0])

    # convert from mono to stereo to match instrumental. did not solve issue
    # vocal_sound = vocal_sound.set_channels(2)

    # Overlay the audio
    instrumental_sound = instrumental_sound.overlay(vocal_sound, position=tc["start"])
    vocal_sound.export("vocal"+str(i)+".wav", format="wav")
    i += 1


instrumental_sound.export("output.wav", format="wav")


