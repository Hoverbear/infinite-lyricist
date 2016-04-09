import wave
import sys
from WavFileWriter import WavFileWriter
import struct
import copy


def wav_params_to_string(wav_filename):
    wav_handle = wave.open(wav_filename, 'r')
    s = "nchannels=%s sampwidth=%s framerate=%s nframes=%s comptype=%s compname=%s" % wav_handle.getparams()
    wav_handle.close()
    return s


def wav_sample_iter(wav_handle):

    assert wav_handle.getsampwidth() == 2, "Expects wav file with sample width of 2 but found {}".format(wav_handle.getsampwidth())

    nframes = wav_handle.getnframes()

    for i in range(nframes):
        frame = wav_handle.readframes(i)
        frame_len = len(frame)

        if frame_len % 2 != 0:
            raise Expection("Frame lenght of {} is not an even number".format(frame_len))

        if frame_len == 0:
            yield (0, "0")
        else:
            for x in range(0, frame_len, 2):
                frame_part = frame[x : x+2]
                yield (struct.unpack("H", frame_part)[0], frame_part)


def combine_short_files(wav_file_writer, minimum_length_seconds):

    wfw = wav_file_writer
    too_short_list = []
    running_length = 0
    must_copy_next = False

    # Copy because changing something while iterating over it is bad.
    file_info = copy.deepcopy(wfw.get_file_info())

    for fname, length in file_info:
        if must_copy_next == False:
            if length >= minimum_length_seconds:
                continue

        if running_length < minimum_length_seconds:
            w = wave.open(fname, 'r')
            wfw.add_data(w.readframes(w.getnframes()))
            running_length += float(w.getnframes()) / w.getframerate()
            w.close()
            too_short_list.append(fname)

            if running_length >= minimum_length_seconds:
                wfw.write_to_next_file()
                running_length = 0
                must_copy_next = False
            else:
                must_copy_next = True

    # Remove filenames for files that were too short.
    final_file_info = []
    for tup in wfw.get_file_info():
        if not tup[0] in too_short_list:
            final_file_info.append(tup)

    return final_file_info


def separate_by_silence(wav_filename, threshold, minimum_length_seconds):
    wav_handle = wave.open(wav_filename, 'r')

    threshold = max(threshold, 0)

    min_frame_length = wav_handle.getframerate() * 2 * wav_handle.getnchannels()

    wfw = WavFileWriter("vocal_split.wav", wav_handle.getparams())

    frame = ""

    for sample, string in wav_sample_iter(wav_handle):
        if sample <= threshold:
            if len(frame) >= min_frame_length:
                wfw.add_data(frame)
                wfw.write_to_next_file()
                frame = ""
        else:
            frame += string

    if len(frame) >= min_frame_length:
        wfw.add_data(frame)
        wfw.write_to_next_file()

    wav_handle.close()

    return combine_short_files(wfw, minimum_length_seconds)


if __name__ == "__main__":
    print wav_params_to_string(sys.argv[1])
    print separate_by_silence(sys.argv[1], 1, 4.0)


