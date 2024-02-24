# FileStorageService layer
class FileStorageError(Exception):
    pass


# Repository layer


class DirectoryError(FileStorageError):
    pass


class FileDeletionError(FileStorageError):
    pass


class FileWriteError(FileStorageError):
    pass


class FileReadError(FileStorageError):
    pass


class FileAlreadyExistsError(FileStorageError):
    pass
