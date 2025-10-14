# Created by emeday, 2025
# Thin adapter the IAM service can import, keeping the hexagonal boundaries.
# It delegates to the shared library so we have a single password policy.

from ev_shared.security.passwords import hash_password, verify_password, identify_scheme

__all__ = ["hash_password", "verify_password", "identify_scheme"]
