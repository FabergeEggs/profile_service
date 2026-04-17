class DomainError(Exception):
    """Base domain exception"""
    pass

class ProfileNotFoundError(DomainError):
    """Profile not found in repository"""
    def __init__(self, user_id: str):
        self.user_id = user_id
        super().__init__(f"Profile not found for user: {user_id}")

class ProfileAlreadyExistsError(DomainError):
    """Profile already exists for this user"""
    def __init__(self, user_id: str):
        self.user_id = user_id
        super().__init__(f"Profile already exists for user: {user_id}")

class InvalidProfileDataError(DomainError):
    """Invalid profile data provided"""
    pass

class UnauthorizedAccessError(DomainError):
    """User not authorized to perform this action"""
    def __init__(self, message: str = "Unauthorized access"):
        self.message = message
        super().__init__(message)
