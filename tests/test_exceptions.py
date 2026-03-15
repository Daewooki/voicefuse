from voicefuse.exceptions import (
    VoiceFuseError,
    ProviderError,
    AuthenticationError,
    RateLimitError,
    UnsupportedFeatureError,
    AllProvidersFailedError,
)


def test_exception_hierarchy():
    assert issubclass(ProviderError, VoiceFuseError)
    assert issubclass(AuthenticationError, ProviderError)
    assert issubclass(RateLimitError, ProviderError)
    assert issubclass(UnsupportedFeatureError, VoiceFuseError)
    assert issubclass(AllProvidersFailedError, VoiceFuseError)


def test_provider_error_carries_provider_name():
    err = ProviderError("API failed", provider="openai")
    assert err.provider == "openai"
    assert "API failed" in str(err)


def test_authentication_error_has_status_code():
    err = AuthenticationError("Bad key", provider="openai")
    assert err.status_code == 401
    assert err.provider == "openai"


def test_rate_limit_error_has_status_code():
    err = RateLimitError("Too many requests", provider="openai")
    assert err.status_code == 429


def test_all_providers_failed_carries_errors():
    errors = [
        ProviderError("fail1", provider="openai"),
        ProviderError("fail2", provider="elevenlabs"),
    ]
    err = AllProvidersFailedError(errors=errors)
    assert len(err.errors) == 2
    assert "All 2 providers failed" in str(err)
