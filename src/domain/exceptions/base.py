# src/domain/exceptions/base.py
class DomainError(Exception):
    """Base class for all business logic errors"""
    pass

class EntityAlreadyExistsError(DomainError):
    """Raised when a unique constraint is violated"""
    pass