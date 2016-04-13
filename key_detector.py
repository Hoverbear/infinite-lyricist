import marsyas

def detect_key(music_file):
    """
    Determines the predominant key of a given music file.

    * music_file: The filename of a music file which Marsyas can read.

    Returns one of ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]
    """
    from collections import Counter
    keys = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]

    # Build the system.
    msm = marsyas.MarSystemManager()
    system = marsyas.system_from_script_file("marsystems/key-detection.mrs")
    # Define some variables
    system.updControl("mrs_string/file", marsyas.MarControlPtr.from_string(music_file))
    system.updControl("mrs_real/israte", 22050.0)
    system.updControl("mrs_real/osrate", 22050.0)

    system.updControl("mrs_natural/inSamples", 16384)
    system.updControl("mrs_natural/onSamples", 16384)

    result = []
    # Tick the system.
    while (system.getControl("SoundFileSource/input/mrs_bool/hasData").to_bool()):
        system.tick()
        result.append(system.getControl("mrs_string/key_name").to_string())

    counts = Counter(result).most_common();
    # print(counts)
    return counts[0][0]

if __name__ == "__main__":
    selection = detect_key("instrumentals/wav/song-synth.wav")
    print("Truth: e, Chosen: " + selection)
    selection = detect_key("instrumentals/wav/song-bass.wav")
    print("Truth: a, Chosen: " + selection)
    selection = detect_key("instrumentals/wav/song-guitar.wav")
    print("Truth: a, Chosen: " + selection)
