"""VoiceFuse exception hierarchy."""


class VoiceFuseError(Exception):
    """Base exception for all VoiceFuse errors."""


class ProviderError(VoiceFuseError):
    """An upstream voice AI provider returned an error."""

    def __init__(self, message: str, *, provider: str, status_code: int | None = None):
        self.provider = provider
        self.status_code = status_code
        super().__init__(f"[{provider}] {message}")


class AuthenticationError(ProviderError):
    """API key is missing or invalid for a provider."""

    def __init__(self, message: str, *, provider: str):
        super().__init__(message, provider=provider, status_code=401)


class RateLimitError(ProviderError):
    """Provider rate limit exceeded."""

    def __init__(self, message: str, *, provider: str, retry_after: float | None = None):
        self.retry_after = retry_after
        super().__init__(message, provider=provider, status_code=429)


class UnsupportedFeatureError(VoiceFuseError):
    """Requested feature is not supported by this provider."""

    def __init__(self, message: str, *, provider: str, feature: str):
        self.provider = provider
        self.feature = feature
        super().__init__(f"[{provider}] {message}")


class AllProvidersFailedError(VoiceFuseError):
    """All providers in the fallback chain failed."""

    def __init__(self, *, errors: list[Exception]):
        self.errors = errors
        super().__init__(f"All {len(errors)} providers failed: {[str(e) for e in errors]}")
