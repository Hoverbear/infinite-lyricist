import marsyas

def detect_key(music_file):
    """
    This function assists in running Marsyas scripts.
    """
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
        result.append(list(system.getControl("mrs_realvec/output").to_realvec()))
    
    instance_count = [0]*12
    for line in result:
        for index,value in enumerate(line):
            if value == 1:
                instance_count[index] += 1
    print(instance_count) 
    return keys[instance_count.index(max(instance_count))]

if __name__ == "__main__":
    selection = detect_key("samples/aminor.mp3")
    print(selection)
    selection = detect_key("samples/asharp.mp3")
    print(selection)
    selection = detect_key("samples/fmajor.mp3")
    print(selection)
