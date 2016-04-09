import wave
import sys
from WavFileWriter import WavFileWriter
import struct


def wav_params_to_string(wav_handle):
    return "nchannels=%s sampwidth=%s framerate=%s nframes=%s comptype=%s compname=%s" % wav_handle.getparams()


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


def separate_by_silence(wav_handle, threshold):
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

    return wfw.get_file_info()


if __name__ == "__main__":
    handle = wave.open(sys.argv[1], 'r')

    print wav_params_to_string(handle)

    filenames = separate_by_silence(handle, 1)
    print filenames


