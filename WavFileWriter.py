import wave
from FileNameIncrementor import FileNameIncrementor


class WavFileWriter:


    def __init__(self, filename_root, wav_params):
        self.__fni = FileNameIncrementor(filename_root)
        self.__file_info = []
        self.__data = ""
        self.__wav_params = wav_params


    def add_data(self, data):
        self.__data += data


    def write_to_next_file(self):
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

    def get_next_name(self):
        name = self.__fni.next()
        return name


    # Returns a list of tuples of (filename, length_in_seconds).
    def get_file_info(self):
        return self.__file_info


