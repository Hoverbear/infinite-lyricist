import wave
from FileNameIncrementor import FileNameIncrementor


class WavFileWriter:


    def __init__(self, filename_root, wav_params):
        """
        A class for writing wav file data to an arbitary number of consecutive wav files.

        * filename_root: A string containing the path which to write the files.
        * wav_params: Wav file parameters in a tuple which mirrors that returns by wave.getparams().
                      These are the parameters used by all files created by the WavFileWriter.
        """

        self.__fni = FileNameIncrementor(filename_root)
        self.__file_info = []
        self.__data = ""
        self.__wav_params = wav_params


    def add_data(self, data):
        """
        Add data to the wav file which is currently being written.

        * data: A string containing wav file frame data.
        """
        self.__data += data


    def write_to_next_file(self):
        """
        Write the file to the filesystem and advance to the next file.

        If no data has been added by add_data() for the current file then this
        is a no-operation and no file is created.
        """
        if len(self.__data) == 0:
            return

        name = self.__fni.next()

        handle = wave.open(name, 'w')
        handle.setparams(self.__wav_params)
        handle.writeframes(self.__data)
        length_in_seconds = float(handle.getnframes()) / handle.getframerate()
        handle.close()

        self.__file_info.append( (name, length_in_seconds) )
        self.__data = ""


    def get_file_info(self):
        """
        Get the names and lengths of the files which have already been written.
        A cal to write_to_next_file() is required for a file to appear in the list.

        Returns a list of tuples of the from (filename, length in seconds).
        """
        return self.__file_info


