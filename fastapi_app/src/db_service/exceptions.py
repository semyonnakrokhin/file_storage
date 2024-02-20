# Repositories Errors
class RepositoryError(Exception):
    pass


class SessionNotSetError(RepositoryError):
    """Exception raised when no session is set in the repository."""


class DatabaseError(RepositoryError):
    pass


class InvalidAttributeError(RepositoryError):
    pass


class NoConditionsError(RepositoryError):
    pass


# Mappers Errors
class MappingError(Exception):
    pass


# Service Errors
class DatabaseServiceError(Exception):
    pass


class DomainModelCreationError(DatabaseServiceError):
    pass


class DictConversionError(DatabaseServiceError):
    pass


class DataLossError(DatabaseServiceError):
    pass
