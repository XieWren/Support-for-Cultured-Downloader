# Import Standard Libraries
from typing import Union, Optional, Callable

# import local files
if (__package__ is None or __package__ == ""):
    from crucial import install_dependency
    from constants import CONSTANTS as C
    from functional import validate_schema
else:
    from .crucial import install_dependency
    from .constants import CONSTANTS as C
    from .functional import validate_schema

# Import Third-party Libraries
import requests

try:
    from cryptography.hazmat.backends import default_backend
except (ModuleNotFoundError, ImportError):
    install_dependency(dep="cryptography>=37.0.4")
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding, rsa, types
from cryptography.hazmat.primitives import hashes, serialization

def generate_rsa_key_pair() -> tuple[bytes, bytes]:
    """Generates a 2048 bits private and public key pair.

    Returns:
        A tuple containing the private and public keys (bytes).
            (privateKey, publicKey)
    """
    privateKey = rsa.generate_private_key(
        public_exponent=65537, # as recommended by the cryptography library documentation
        key_size=2048,
    )
    publicKey = privateKey.public_key()
    return (
        privateKey.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ),
        publicKey.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ),
    )

def rsa_encrypt(plaintext: Union[str, bytes], digestMethod: Optional[Callable] = hashes.SHA512) -> bytes:
    """Encrypts a plaintext using the public key (RSA-OAEP-SHA) from Cultured Downloader API.

    Args:
        plaintext (str|bytes): 
            The plaintext to encrypt.
        digestMethod (cryptography.hazmat.primitives.hashes.HashAlgorithm):
            The hash algorithm to use for the encryption (defaults to SHA512).

    Returns:
        The encrypted plaintext (bytes).

    Raises:
        TypeError:
            If the digest method is not a subclass of cryptography.hazmat.primitives.hashes.HashAlgorithm.
        Exception:
            If the JSON response from the Cultured Downloader API does not match the schema or the response status code was not 200 OK.
    """
    if (not issubclass(digestMethod, hashes.HashAlgorithm)):
        raise TypeError("digestMethod must be a subclass of cryptography.hazmat.primitives.hashes.HashAlgorithm")

    res = requests.get(f"{C.WEBSITE_URL}/api/v1/rsa/public-key")
    if (res.status_code != 200):
        raise Exception(f"Server Response: {res.status_code} {res.reason}")

    res = res.json()
    if (not validate_schema(schema=C.SERVER_PUBLIC_KEY_SCHEMA, data=res)):
        raise Exception("Invalid json response from Cultured Downloader website")

    publicKey = serialization.load_pem_public_key(
        data=res["public_key"].encode("utf-8"), 
        backend=default_backend()
    )

    if (isinstance(plaintext, str)):
        plaintext = plaintext.encode("utf-8")

    # Construct the padding
    hashAlgo = digestMethod()
    mgf = padding.MGF1(algorithm=hashAlgo)
    pad = padding.OAEP(mgf=mgf, algorithm=hashAlgo, label=None)

    # Encrypt the plaintext using the public key
    return publicKey.encrypt(plaintext=plaintext, padding=pad)

def rsa_decrypt(ciphertext: bytes, privateKey: str | types.PRIVATE_KEY_TYPES, 
                digestMethod: Optional[Callable] = hashes.SHA512, decode: Optional[bool] = False) -> Union[str, bytes]:
    """Decrypts a ciphertext using the private key (RSA-OAEP-SHA) that was generated by generate_rsa_key_pair().

    Args:
        ciphertext (bytes): 
            The ciphertext to decrypt.
        digestMethod (cryptography.hazmat.primitives.hashes.HashAlgorithm):
            The hash algorithm to use for the decryption (defaults to SHA512).
        decode (bool):
            Whether to decode the decrypted plaintext to a string (defaults to False).

    Returns:
        The decrypted ciphertext (bytes|str).

    Raises:
        TypeError:
            If the digest method is not a subclass of cryptography.hazmat.primitives.hashes.HashAlgorithm or
            the private key is not a subclass of cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey.
    """
    if (not issubclass(digestMethod, hashes.HashAlgorithm)):
        raise TypeError("digestMethod must be a subclass of cryptography.hazmat.primitives.hashes.HashAlgorithm")

    if (isinstance(privateKey, str)):
        # Extract and parse the public key as a PEM-encoded RSA private key
        privateKey = serialization.load_pem_private_key(
            data=privateKey.encode("utf-8"), 
            password=None,
            backend=default_backend()
        )
    elif (not isinstance(privateKey, types.PRIVATE_KEY_TYPES)):
        raise TypeError("privateKey must be an instance of cryptography.hazmat.primitives.asymmetric.types.PRIVATE_KEY_TYPES")

    # Construct the padding
    hashAlgo = digestMethod()
    mgf = padding.MGF1(algorithm=hashAlgo)
    pad = padding.OAEP(mgf=mgf, algorithm=hashAlgo, label=None)

    # Decrypt the ciphertext using the private key
    ciphertext = privateKey.decrypt(ciphertext=ciphertext, padding=pad)
    return ciphertext.decode("utf-8") if (decode) else ciphertext