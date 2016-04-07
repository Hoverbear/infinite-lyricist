import marsyas

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
