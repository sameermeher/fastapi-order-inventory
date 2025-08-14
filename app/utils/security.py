import hmac, hashlib

def compute_signature(secret: str, raw_body: bytes) -> str:
    return hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()

def secure_compare(a: str, b: str) -> bool:
    return hmac.compare_digest(a, b)