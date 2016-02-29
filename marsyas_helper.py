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

if __name__ == "__main__":
    # execute only if run as a script
    run_script("./marsystems/template.mrs", "./out.mp3", "./samples/test_1.mp3", "./samples/test_2.mp3")
