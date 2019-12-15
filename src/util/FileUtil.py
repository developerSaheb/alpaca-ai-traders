class FileUtil(object):

    @staticmethod
    def append_to_file(path, data):
        with open(path, "a") as myfile:
            myfile.write(data)

    @staticmethod
    def write_file(path, data):
        with open(path, "w") as myfile:
            myfile.write(data)

    @staticmethod
    def read_file(path):
        with open(path, "r") as myfile:
            return myfile.read()
