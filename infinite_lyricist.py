#! /bin/env python2.7
import argparse
import time
import random
import wave

from pydub import AudioSegment

from bpm_detector import detect_bpm
from key_detector import detect_key
from phase_vocoder import time_shift, pitch_shift
from separate_by_silence import separate_by_silence
from phase_vocoder import time_shift
from phase_vocoder import pitch_shift
from fix_header import fix_header
from WavFileWriter import WavFileWriter
from timecodes import parse_timecodes


def infinite_lyricist(vocal_track, instrumental_track, timecodes, output_track):

    """Generates a mashup from the given inputs.

    * vocal_track: The file name of the input vocal track.
    * instrumental_track: The file name of the input instrumental track.
    * timecodes: The timecodes for vocals in the format `mm:ss:fff-mm:ss:fff,...`
    * output_track: The output track name."""

    # print "Detecting instrumental BPM..."
    # start = time.time()
    instrumental_bpm = detect_bpm(instrumental_track)
    # print "Instrumental BPM:", instrumental_bpm
    # print "Elapsed seconds:", time.time() - start
    # print

    # print "Detecting instrumental key..."
    # start = time.time()
    instrumental_key = detect_key(instrumental_track)
    # print "Instrumental Key:", instrumental_key
    # print "Elapsed seconds:", time.time() - start
    # print

    # print "Splitting vocal track by silence..."
    # start = time.time()
    split_vocals = separate_by_silence(vocal_track, threshold=1, minimum_length_seconds=4.0)
    # print "Vocal sections (filename, length in seconds):", split_vocals
    # print "Elapsed seconds:", time.time() - start
    # print

    # print "Detecting key and BMP of vocal sections:"
    vocal_sections = []
    for fname, length in split_vocals:
        # start = time.time()
        key = detect_key(fname)
        try:
            bpm = detect_bpm(fname)
        except:
            bpm = None
        # print fname + ":"
        # print "  key:", key
        # print "  BMP:", bpm
        # print "  Elapsed seconds:", time.time() - start
        if bpm:
            vocal_sections.append( (fname, length, key, bpm) )

    # print
    # print vocal_sections
    # print
    # print "Matching vocal tempos to instrumental tempo:"

    # Get first clip and initialize iterator
    wav_handle = wave.open(split_vocals[0][0], 'r')
    wfw = WavFileWriter("/tmp/vocal_time-shift.wav", wav_handle.getparams())

    v_s = list(vocal_sections)
    bpm_matched_vocals = []
    for i in range(len(v_s)):
        
        start = time.time()
        bpm = v_s[i][3]
        fname = v_s[i][0]
        
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

    instrumental_sound = AudioSegment.from_wav(instrumental_track)

    # Overlay the vocal sections over the instrumental
    while (len(timecodes) > 0) and (len(vocal_sections) > 0):
        # Get a random section of the instrumental
        tc = timecodes.pop(random.randrange(len(timecodes)))

        # print "timecode=", tc

        # Find a vocal section that fits in the duration of the instructional section
        can_fit = []
        vs_index = 0
        for vs in vocal_sections:
            # print vs[1]
            vs_length_milliseconds = vs[1] * 1000
            if vs_length_milliseconds <= tc["duration"]:
                # print "There is a clip match"
                can_fit.append(vs_index)
            vs_index += 1

        # Sort by clip duration so we get better matches
        can_fit.sort(key=lambda x: vocal_sections[x][1], reverse=True)
        the_chosen_one = None;
        if len(can_fit) == 0:
            # No vocal section is short enough for this duration
            # print "vs_index:", vs_index
            # print "len(vocal_sections):", len(vocal_sections)
            # print "vs_index >= len(vocal_sections):", vs_index >= len(vocal_sections)
        #if vs_index >= len(vocal_sections):
            continue
        else:
            top = can_fit;
            if top > 5:
                top = 5
            the_chosen_one = can_fit.pop(random.randrange(top))

        vocal = vocal_sections.pop(the_chosen_one)
        # print "vocal=", vocal
        vocal_sound = AudioSegment.from_wav(vocal[0])

        # convert from mono to stereo to match instrumental. did not solve issue
        vocal_sound = vocal_sound.set_channels(2)

        # Overlay the audio
        instrumental_sound = instrumental_sound.overlay(vocal_sound, position=tc["start"])
        # vocal_sound.export("vocal"+str(vs_index)+".wav", format="wav")

    instrumental_sound.export(output_track, format="wav")




if __name__ == "__main__":
    # First, let's parse the command line options.
    parser = argparse.ArgumentParser(description='Mashes a vocal track onto a instrumental track.')
    parser.add_argument('vocal_input', metavar='vocal_input', help='The vocal input')
    parser.add_argument('instrumental_input', metavar='instrumental_input', help='The instrumental input')
    parser.add_argument('instrumental_timecodes', metavar='instrumental_timecodes', help="""
        Comma separated timecodes that mark the start of sections in the instrumental input.
        Each timecode consists of a start timestamp and an end timestamp separate by a dash.
        The timestamp format is:
            MM:SS:FFF M=minutes, S=seconds, F=milliseconds (optional).
        Example timecodes for the provided song:
            00:08-00:14:500,00:15-00:22:500,00:23-00:31:500,00:32-00:39:500,00:40-00:46:500,00:47-00:56
    """)
    parser.add_argument('output_track', metavar='output_track', help='The output destination')


    # Now we parse them and pick up the existing files or error out.
    args = parser.parse_args()
    vocal_track = args.vocal_input
    instrumental_track = args.instrumental_input
    output_track = args.output_track
    timecodes = parse_timecodes(args.instrumental_timecodes)


    print "Generating a mashup based on those parameters. Please wait a minute or two..."
    infinite_lyricist(vocal_track, instrumental_track, timecodes, output_track)
    print "Mashup generated as " + str(output_track) + ", enjoy!"
