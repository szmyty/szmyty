"""Custom exceptions for the magazine production engine."""


class MagazineError(Exception):
    """Base exception for all magazine errors."""


class DependencyError(MagazineError):
    """Raised when a required external tool is missing."""


class PageBuildError(MagazineError):
    """Raised when a page build step fails."""


class EditionBuildError(MagazineError):
    """Raised when an edition build step fails."""


class AIRuntimeError(MagazineError):
    """Raised when the AI runtime is unavailable or misconfigured."""


class ModelfileError(MagazineError):
    """Raised when the AI Modelfile is missing or invalid."""


class SubprocessTimeoutError(MagazineError):
    """Raised when a subprocess exceeds the configured timeout."""
