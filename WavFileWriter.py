import wave
from FileNameIncrementor import FileNameIncrementor


class WavFileWriter:


    def __init__(self, filename_root, wav_params):
        self.__fni = FileNameIncrementor(filename_root)
        self.__filenames = []
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
        handle.close()

        self.__filenames.append(name)
        self.__data = ""


    def get_filenames(self):
        return self.__filenames


