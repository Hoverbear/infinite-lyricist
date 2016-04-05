import marsyas

# The output mix_to_mono doesn't seem to play well with separate_by_silence().
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

def detect_key(music_file):
    """
    This function assists in running Marsyas scripts.
    """
    from collections import Counter

    keys = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]
    # Build the system.
    msm = marsyas.MarSystemManager()
    system = marsyas.system_from_script_file("marsystems/key-detection.mrs")
    # Define some variables
    system.updControl("mrs_string/file", marsyas.MarControlPtr.from_string(music_file))

    result = []
    # Tick the system.
    while (system.getControl("SoundFileSource/input/mrs_bool/hasData").to_bool()):
        system.tick()
        result.append(system.getControl("mrs_string/key_name").to_string())

    counts = Counter(result).most_common();
    print(counts)
    return counts[0][0]


if __name__ == "__main__":
    selection = detect_key("song/wav/song-synth.wav")
    print("Truth: e, Chosen: " + selection)
    selection = detect_key("song/wav/song-bass.wav")
    print("Truth: a, Chosen: " + selection)
    selection = detect_key("song/wav/song-guitar.wav")
    print("Truth: a, Chosen: " + selection)
