"""Password hashing and compact HS256 JWT helpers (standard library only)."""
import base64
import hashlib
import hmac
import json
import os
import time
from app.config import settings

def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('ascii')

def _unb64(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + '=' * (-len(value) % 4))

def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.scrypt(password.encode('utf-8'), salt=salt, n=2**14, r=8, p=1)
    return 'scrypt$' + base64.b64encode(salt).decode() + '$' + base64.b64encode(digest).decode()

def verify_password(password: str, encoded: str) -> bool:
    try:
        scheme, salt, digest = encoded.split('$', 2)
        if scheme != 'scrypt':
            return False
        actual = hashlib.scrypt(password.encode('utf-8'), salt=base64.b64decode(salt), n=2**14, r=8, p=1)
        return hmac.compare_digest(actual, base64.b64decode(digest))
    except (ValueError, TypeError):
        return False

def create_access_token(user: dict) -> str:
    now = int(time.time())
    header = _b64(json.dumps({'alg':'HS256','typ':'JWT'}, separators=(',', ':')).encode())
    payload = _b64(json.dumps({'sub':str(user['id']), 'username':user['username'], 'iat':now, 'exp':now+3600}, separators=(',', ':')).encode())
    signing_input = f'{header}.{payload}'.encode('ascii')
    signature = _b64(hmac.new(settings.secret_key.encode(), signing_input, hashlib.sha256).digest())
    return f'{header}.{payload}.{signature}'

def decode_access_token(token: str):
    try:
        header, payload, signature = token.split('.')
        signing_input = f'{header}.{payload}'.encode('ascii')
        expected = _b64(hmac.new(settings.secret_key.encode(), signing_input, hashlib.sha256).digest())
        if not hmac.compare_digest(signature, expected):
            return None
        claims = json.loads(_unb64(payload))
        if claims.get('exp', 0) <= int(time.time()) or claims.get('sub') is None:
            return None
        return int(claims['sub'])
    except (ValueError, TypeError, KeyError, json.JSONDecodeError, UnicodeDecodeError):
        return None
