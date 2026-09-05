import binascii
import uuid
from datetime import datetime

try:
    from joserfc.jwe import decrypt_compact, encrypt_compact
    from joserfc.jwk import OctKey

    _USE_JOSERFC = True
except ImportError:
    from authlib.jose import JsonWebEncryption

    _USE_JOSERFC = False


def toss_hex_decode(key):
    return binascii.unhexlify(key)


def toss_encrypt(target, key):
    raw_key = toss_hex_decode(key)
    protected = {
        "alg": "dir",
        "enc": "A256GCM",
        "iat": datetime.now().astimezone().isoformat(),
        "nonce": str(uuid.uuid4()),
    }
    if _USE_JOSERFC:
        jwk = OctKey.import_key(raw_key)
        return encrypt_compact(protected, target.encode("utf-8"), jwk)
    jwe = JsonWebEncryption()
    return jwe.serialize_compact(protected, target.encode("utf-8"), raw_key)


def toss_decrypt(encrypted_jwe, key):
    raw_key = toss_hex_decode(key)
    if _USE_JOSERFC:
        jwk = OctKey.import_key(raw_key)
        obj = decrypt_compact(encrypted_jwe, jwk)
        return obj.plaintext.decode("utf-8")
    jwe = JsonWebEncryption()
    decrypted = jwe.deserialize_compact(encrypted_jwe, raw_key)
    return decrypted["payload"].decode("utf-8")
