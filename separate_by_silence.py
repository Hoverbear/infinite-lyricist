import wave
import marsyas
import sys
from WavFileWriter import WavFileWriter
import struct


def mix_to_mono(input_filename, output_filename):

    mng = marsyas.MarSystemManager()

    nwk = mng.create("Series", "network_mix_to_mono")

    nwk.addMarSystem(mng.create("SoundFileSource", "input"))
    nwk.addMarSystem(mng.create("MixToMono", "mono"))
    nwk.addMarSystem(mng.create("SoundFileSink", "output"))

    nwk.updControl("SoundFileSource/input/mrs_string/filename", marsyas.MarControlPtr.from_string(input_filename))
    nwk.updControl("SoundFileSink/output/mrs_string/filename", marsyas.MarControlPtr.from_string(output_filename))

    while nwk.getControl("SoundFileSource/input/mrs_bool/hasData").to_bool():
        nwk.tick()


def wav_params_to_string(wav_handle):
    return "nchannels=%s sampwidth=%s framerate=%s nframes=%s comptype=%s compname=%s" % wav_handle.getparams()


def wav_sample_iter(wav_handle):

    assert wav_handle.getnchannels() == 1, "Expects wav file with only 1 channel but found {}".format(wav_handle.getnchannels())
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
    min_frame_length = wav_handle.getframerate() * 2

    wfw = WavFileWriter("vocal_split.wav", wav_handle.getparams())

    frame = ""

    for sample, string in wav_sample_iter(wav_handle):
        if sample <= threshold:
            if len(frame) >= min_frame_length:
                wfw.write_frames(frame)
                wfw.next()
                frame = ""
        else:
            frame += string

    if len(frame) >= min_frame_length:
        wfw.write_frames(frame)
        wfw.done()

    return wfw.get_filenames()


if __name__ == "__main__":
    #mono_file = "temp_mono.wav"
    #mix_to_mono(sys.argv[1], mono_file)
    #handle = wave.open(mono_file, 'r')
    handle = wave.open(sys.argv[1], 'r')

    print wav_params_to_string(handle)

    print separate_by_silence(handle, 1)


