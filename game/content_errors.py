class ContentError(Exception):
    """Base error for content loading and lookup failures."""


class ContentValidationError(ContentError):
    """Raised when content does not satisfy the documented format."""


class DuplicateContentIdError(ContentValidationError):
    """Raised when a content file defines the same id more than once."""


class MissingContentReferenceError(ContentValidationError):
    """Raised when an id references content that does not exist."""
