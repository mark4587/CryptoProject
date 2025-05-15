# Mark Doyle
# C00257481
from tornado.escape import json_decode
from tornado.gen import coroutine
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from base64 import b64encode
from os import urandom

from .base import BaseHandler
from .Encrypt_Decrypt import encrypt_field  

class RegistrationHandler(BaseHandler):

    @coroutine
    def post(self):
        try:
            body = json_decode(self.request.body)
            email = body['email'].lower().strip()
            password = body['password']
            display_name = body.get('displayName', email)
            address = body.get('address', '')
            dob = body.get('dob', '')
            phone_number = body.get('phoneNumber', '')
            disabilities = body.get('disabilities', '')

            # Check if all user fields are strings
            if not all(isinstance(f, str) for f in [email, password, display_name, address, dob, phone_number, disabilities]):
                raise Exception()
        except:
            # Return error if fail is promted or data is invalid
            self.send_error(400, message='Invalid registration data!')
            return

        # Checks if user already exists
        existing_user = yield self.db.users.find_one({'email': email})
        if existing_user:
            self.send_error(409, message='User already exists!')
            return

        salt = urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=HASH_LENGTH,
            salt=salt,
            iterations=HASH_ITERATIONS,
            backend=default_backend()
        )
        hashed_password = b64encode(kdf.derive(password.encode('utf-8'))).decode('utf-8')

        # Use central encrypt function for each personal field
        encrypted_display = encrypt_field(display_name)
        encrypted_address = encrypt_field(address)
        encrypted_dob = encrypt_field(dob)
        encrypted_phone = encrypt_field(phone_number)
        encrypted_disabilities = encrypt_field(disabilities)

        # Creates the user data/document for the database
        user_doc = {
            'email': email,
            'password': hashed_password,
            'salt': b64encode(salt).decode('utf-8'),

            'displayName': encrypted_display['ciphertext'],
            'displayName_iv': encrypted_display['iv'],
            'displayName_tag': encrypted_display['tag'],

            'address': encrypted_address['ciphertext'],
            'address_iv': encrypted_address['iv'],
            'address_tag': encrypted_address['tag'],

            'dob': encrypted_dob['ciphertext'],
            'dob_iv': encrypted_dob['iv'],
            'dob_tag': encrypted_dob['tag'],

            'phoneNumber': encrypted_phone['ciphertext'],
            'phoneNumber_iv': encrypted_phone['iv'],
            'phoneNumber_tag': encrypted_phone['tag'],

            'disabilities': encrypted_disabilities['ciphertext'],
            'disabilities_iv': encrypted_disabilities['iv'],
            'disabilities_tag': encrypted_disabilities['tag'],
        }
