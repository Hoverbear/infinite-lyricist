import os


class FileNameIncrementor:
    """
    Provides an automated way to increment file names.
    """

    def __init__(self, filename):
        """
        Creates an incrementor.

            * filename: The root of the filename you wish to increment.
        """
        parts = os.path.splitext(str(filename))
        self.__root_name = parts[0]
        self.__ext = parts[1]
        self.__count = 0


    def next(self):
        """
        Returns the next file name after incrementing.
        """
        name = self.__root_name + str(self.__count) + self.__ext
        self.__count += 1
        return name


    def root_name(self):
        """
        Returns the root name.
        """
        return self.__root_name


    def ext(self):
        """
        Returns the file extension.
        """
        return self.__ext


# Simple test
if __name__ == "__main__":

    fni = FileNameIncrementor("path/to/file.wav")

    for i in range(10):
        print fni.next()

    print "root name =", fni.root_name()
    print "ext =", fni.ext()
