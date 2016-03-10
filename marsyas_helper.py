import marsyas

def run_script(script_file, output_file, *input_files):
    """
    This function assists in running Marsyas scripts.
    """
    # Build the system.
    msm = marsyas.MarSystemManager()
    system = marsyas.system_from_script_file(script_file)
    # Define some variables
    for i, this_input in enumerate(input_files):
        system.updControl("SoundFileSource/input_{}/mrs_string/filename".format(i), marsyas.MarControlPtr.from_string(this_input))
    system.updControl("SoundFileSink/output/mrs_string/filename", marsyas.MarControlPtr.from_string(output_file))
    
    # Tick the system.
    while (system.getControl("SoundFileSource/input_0/mrs_bool/hasData").to_bool()):
        system.tick()

def to_realvec(input_file):
    """
    Transforms an input file into a `marsyas.realvec` of data for further passing, also makes the track mono.
    """
    # Build the system.
    msm = marsyas.MarSystemManager()
    system = marsyas.system_from_script_file("marsystems/to_realvec.mrs")
    # Define some variables
    system.updControl("mrs_string/file", marsyas.MarControlPtr.from_string(input_file))
    # This is a dumb way of doing it but I can't figure out a better way.
    egress = marsyas.realvec()
    # Tick the system.
    while (not system.getControl("mrs_bool/done").to_bool()):
        system.tick()
        tick_data = system.getControl("mrs_realvec/processedData").to_realvec()
        egress.appendRealvec(tick_data)
    return egress
    

def key_detection(ingress):
    """
    Runs a key detection algorithm over the ingress realvec or list.
    """
    if type(ingress) != "list":
        list = list(ingress)
    # Build the system.
    msm = marsyas.MarSystemManager()
    system = marsyas.system_from_script_file(script_file)
    # Define some variables
    for i, this_input in enumerate(input_files):
        system.updControl("RealVecSource/input_{}/mrs_string/filename".format(i), marsyas.MarControlPtr.from_string(this_input))
    system.updControl("SoundFileSink/output/mrs_string/filename", marsyas.MarControlPtr.from_string(output_file))
    
    # Tick the system.
    while (system.getControl("RealVecSource/input_0/mrs_bool/hasData").to_bool()):
        system.tick()


if __name__ == "__main__":
    output = to_realvec("samples/test_1.mp3")
    print(len(output))
    print(list(output)[-100:])
