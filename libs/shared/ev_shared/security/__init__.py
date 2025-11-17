# Created by emeday 2025

from .passwords import verify_password, hash_password, needs_rehash

# Expose a shared JWT decoder so callers can `from ev_shared.security import decode_jwt`
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from datetime import datetime, timezone
from ev_shared.config import load_settings


def decode_jwt(token: str, leeway: int = 60, algorithms: Optional[list[str]] = None) -> Dict[str, Any]:
	"""Decode token using settings from ev_shared.config.load_settings().
	Uses manual exp check with `leeway` because python-jose may not accept a leeway kwarg
	depending on the installed version.
	Raises jose.JWTError on signature/parse failure or RuntimeError if secret missing.
	"""
	s = load_settings()
	secret = getattr(s, "JWT_SECRET", None)
	algo = getattr(s, "JWT_ALG", getattr(s, "JWT_ALGORITHM", "HS256"))
	if not secret:
		raise RuntimeError("JWT_SECRET not configured")
	used_algorithms = algorithms or [algo]

	# Decode without letting jose enforce exp (we'll check manually to allow leeway)
	try:
		payload = jwt.decode(token, secret, algorithms=used_algorithms, options={"verify_exp": False})
	except JWTError:
		# re-raise to caller
		raise

	# Manual expiration check with leeway seconds
	exp = payload.get("exp")
	if exp is not None:
		try:
			exp_ts = int(exp)
			now_ts = int(datetime.now(timezone.utc).timestamp())
			if now_ts > exp_ts + int(leeway):
				raise JWTError("Token expired")
		except ValueError:
			# invalid exp claim
			raise JWTError("Invalid exp claim")

	return payload

