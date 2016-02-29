import marsyas

def run_script(script_file, input_file, output_file):
    """
    This function assists in running Marsyas scripts.
    """
    # Build the system.
    msm = marsyas.MarSystemManager()
    system = marsyas.system_from_script_file(script_file)
    # Define some variables
    system.updControl("SoundFileSource/input/mrs_string/filename", marsyas.MarControlPtr.from_string(input_file))
    system.updControl("SoundFileSink/output/mrs_string/filename", marsyas.MarControlPtr.from_string(output_file))
    
    # Tick the system.
    while (system.getControl("SoundFileSource/input/mrs_bool/hasData").to_bool()):
        system.tick()

if __name__ == "__main__":
    # execute only if run as a script
    run_script("./marsystems/template.mrs", "./samples/test.mp3", "./out.mp3")
