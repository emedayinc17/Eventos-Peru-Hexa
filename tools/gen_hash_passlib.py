from passlib.hash import bcrypt_sha256, bcrypt

password = "Admin_2025!"

# Generate bcrypt_sha256 hash (preferred by backend)
hash_sha256 = bcrypt_sha256.hash(password)
print(f"BCRYPT_SHA256: {hash_sha256}")

# Generate standard bcrypt hash (legacy support)
hash_bcrypt = bcrypt.hash(password)
print(f"BCRYPT: {hash_bcrypt}")
