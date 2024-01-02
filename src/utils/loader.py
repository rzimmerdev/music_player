import os


class Loader:
    @staticmethod
    def filename(path):
        return os.path.splitext(os.path.basename(path))[0]

    @staticmethod
    def get_files(path):
        files = []
        for root, directories, filenames in os.walk(path):
            for filename in filenames:
                files.append(os.path.join(root, filename))

        return files
