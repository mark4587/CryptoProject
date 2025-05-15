from base64 import b64encode, b64decode
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from os import urandom
from api.conf import SHARED_KEY

# Use a 12-byte IV (recommended for AES-GCM)
IV_Length = 12

def encrypt_field(plaintext):
    # Generates a random IV
    iv = urandom(IV_Length)

    # Sets the cipher up with the shared key and IV
    cipher = Cipher(
        algorithms.AES(SHARED_KEY),
        modes.GCM(iv),
        backend=default_backend()
    )
    encryptor = cipher.encryptor()

    # Encrypts the plaintext
    ciphertext = encryptor.update(plaintext.encode('utf-8')) + encryptor.finalize()

    # Returns the components base64-encoded for storage
    return {
        'ciphertext': b64encode(ciphertext).decode('utf-8'),
        'iv': b64encode(iv).decode('utf-8'),
        'tag': b64encode(encryptor.tag).decode('utf-8')
    }

def decrypt_field(ciphertext_b64, iv_b64, tag_b64):
    # Decodes all the base64 encoded inputs
    ciphertext = b64decode(ciphertext_b64)
    iv = b64decode(iv_b64)
    tag = b64decode(tag_b64)

    # Sets up the AES-GCM cipher for decryption
    cipher = Cipher(
        algorithms.AES(SHARED_KEY),
        modes.GCM(iv, tag),
        backend=default_backend()
    )
    decryptor = cipher.decryptor()

    # Decrypts and returns the original plaintext bytes
    return decryptor.update(ciphertext) + decryptor.finalize()
