import wave
import sys
from WavFileWriter import WavFileWriter
import struct
import copy


def wav_params_to_string(wav_filename):
    """
    Builds a string of metadata from the parameters of a given wav filename.

    * wav_filename: A filename.

    Returns "nchannels=?? sampwidth=?? framerate=?? nframes=?? comptype=?? compname=??"
    """

    wav_handle = wave.open(wav_filename, 'r')
    s = "nchannels=%s sampwidth=%s framerate=%s nframes=%s comptype=%s compname=%s" % wav_handle.getparams()
    wav_handle.close()
    return s


def wav_sample_iter(wav_handle):
    """
    A generator which returns the next sample in wav file.

    * wav_handl: The Wave_read object returned from wave.open() in read mode.

    Returns a 2-tuple: (integer representing the sample, string representing the sample)

    The wav file must be encoded with a sample width of 2.
    """

    assert wav_handle.getsampwidth() == 2, "Expects wav file with sample width of 2 but found {}".format(wav_handle.getsampwidth())

    nframes = wav_handle.getnframes()

    for i in range(nframes):
        frame = wav_handle.readframes(i)
        frame_len = len(frame)

        if frame_len % 2 != 0:
            raise Expection("Frame length of {} is not an even number".format(frame_len))

        if frame_len == 0:
            yield (0, "0")
        else:
            for x in range(0, frame_len, 2):
                frame_part = frame[x : x+2]
                yield (struct.unpack("H", frame_part)[0], frame_part)


def combine_short_files(wav_file_writer, minimum_length_seconds):
    """
    Combines short files to result files at least as long as a given minimum length.

    * wav_file_writer: An instance of a WavFileWriter which has already created files.
    * minimum_length_seconds: A number representing the minimum length in seconds.

    Returns a list of tuples in the form (filename, length in seconds) containing
    information for the files which were longer than the minimum and the files
    which were created by combining the files which were too short.
    """

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
    """
    Separate a wav file by silence.

    * threshold: An integer between 0 and 65535 which represents the highest
                 sample value to be considered noise. Anything above it will
                 not be considered noise.
                 If a value less than zero is provided, the threshold will be
                 set to zero.
    * minimum_length_seconds: The minimum length in seconds which a sound file must be.

    Returns a list of tuples of (filename, length in seconds) of resulting files.
    """
    wav_handle = wave.open(wav_filename, 'r')

    # threshold value for sample slicing default 0
    threshold = max(threshold, 0)

    # minimum samples in any cut clip
    min_frame_length = wav_handle.getframerate() * 2 * wav_handle.getnchannels()

    wfw = WavFileWriter("/tmp/vocal_split.wav", wav_handle.getparams())

    frame = ""

    for sample, string in wav_sample_iter(wav_handle):
        # if first sample in frame is below the threshold cut here
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
