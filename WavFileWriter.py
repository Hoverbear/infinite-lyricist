import wave
from FileNameIncrementor import FileNameIncrementor


class WavFileWriter:


    def __init__(self, filename_root, wav_params):
        self.__fni = FileNameIncrementor(filename_root)
        self.__filenames = []
        self.__curr_name = None
        self.__curr_handle = None
        self.__wav_params = wav_params
        self.__curr_frame_lenght = 0


    def __open_curr(self):
        name = self.__fni.next()
        self.__curr_name = name
        self.__curr_handle = wave.open(name, 'w')
        self.__curr_handle.setparams(self.__wav_params)
        self.__curr_frame_length = 0


    def write_frames(self, data):
        if self.__curr_handle == None:
            self.__open_curr()

        self.__curr_handle.writeframes(data)
        self.__curr_frame_length += len(data)


    def next(self):
        if self.__curr_handle == None:
            #print "WavFileWriter.next() skip None"
            return

        if self.__curr_frame_length == 0:
            #print "WavFileWriter.next() skip length is zero"
            return

        #print "WavFileWriter.next() write"

        self.__filenames.append(self.__curr_name)
        self.__curr_handle.close()
        self.__open_curr()


    def done(self):
        if self.__curr_handle == None:
            return

        self.__filenames.append(self.__curr_name)
        self.__curr_handle.close()


    def get_filenames(self):
        return self.__filenames


