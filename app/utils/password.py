import hashlib
import secrets

alphabet = 'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890'


async def hash_password(password: str, salt: str) -> str:
    return hashlib.sha256((password+salt).encode('utf-8')).hexdigest()


async def make_salt() -> str:
    return ''.join([secrets.choice(alphabet) for _ in range(secrets.randbelow(20))])
