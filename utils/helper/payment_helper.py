import binascii
import uuid
from datetime import datetime

from authlib.jose import JsonWebEncryption


def toss_hex_decode(key):
    return binascii.unhexlify(key)


def toss_encrypt(target, key):
    # Decode security key
    key = toss_hex_decode(key)
    # Create JWE header
    headers = {
        "alg": "dir",
        "enc": "A256GCM",
        "iat": datetime.now().astimezone().isoformat(),
        "nonce": str(uuid.uuid4()),
    }
    # Encrypt request body
    jwe = JsonWebEncryption()
    encrypted = jwe.serialize_compact(headers, target.encode("utf-8"), key)
    return encrypted


def toss_decrypt(encrypted_jwe, key):
    # Decode security key
    key = toss_hex_decode(key)
    jwe = JsonWebEncryption()
    decrypted = jwe.deserialize_compact(encrypted_jwe, key)
    return decrypted["payload"].decode("utf-8")
