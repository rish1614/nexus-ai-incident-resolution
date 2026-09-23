"""
Regression test for a real bug hit during Phase 2 live verification:
passlib 1.7.4 is incompatible with bcrypt>=4.1 (bcrypt removed the
`__about__` attribute passlib's version-detection reads), which surfaces
as a confusing "password cannot be longer than 72 bytes" error on the
*first* hash() call rather than an obvious version-mismatch error.

Fixed by pinning `bcrypt>=4.0.1,<4.1` in pyproject.toml. This test exists
so a future dependency bump that silently drops the pin gets caught here
instead of in a live seed run.
"""

from passlib.context import CryptContext


def test_bcrypt_password_hashing_works():
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    plain = "nexus-dev-only-not-for-production"

    hashed = pwd_context.hash(plain)

    assert hashed.startswith("$2b$")
    assert pwd_context.verify(plain, hashed) is True
    assert pwd_context.verify("wrong-password", hashed) is False
