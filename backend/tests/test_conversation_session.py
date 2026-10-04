from uuid import UUID
import pytest
from conversation_session import issue_session, verify_session


def test_session_roundtrip_and_expiry():
    token = issue_session('s' * 40, 1000)
    assert isinstance(verify_session(token, 's' * 40, 1001), UUID)
    for now in (999, 1000 + 30 * 86400):
        with pytest.raises(ValueError):
            verify_session(token, 's' * 40, now)


def test_session_rejects_tampering_and_missing_secret():
    token = issue_session('s' * 40, 1000)
    for changed, secret in ((token + 'x', 's' * 40), (token, 'x' * 40), (token, '')):
        with pytest.raises(ValueError):
            verify_session(changed, secret, 1001)
    with pytest.raises(ValueError):
        issue_session('', 1000)
