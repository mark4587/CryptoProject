# Mark Doyle
# C00257481
from datetime import datetime, timedelta
from time import mktime
from tornado.escape import json_decode
from tornado.gen import coroutine
from uuid import uuid4
from base64 import b64decode
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

from .base import BaseHandler
from .Encrypt_Decrypt import decrypt_field

#Password Hashing
HASH_ITERATIONS = 100000
HASH_LENGTH = 32

class LoginHandler(BaseHandler):

    @coroutine

    def generate_token(self, email):
        # Creates a token with an expiry of 1hr
        token_uuid = uuid4().hex
        expires_in = datetime.now() + timedelta(hours=1)
        expires_in = mktime(expires_in.utctimetuple())

        token = {
            'token': token_uuid,
            'expiresIn': expires_in,
        }
        # Saves the token to the user's record
        yield self.db.users.update_one({
            'email': email
        }, {
            '$set': token
        })

        return token

    @coroutine
    def post(self):
        try:
            # Decodes the JSON
            body = json_decode(self.request.body)
            email = body['email'].lower().strip()
            password = body['password']
        except:
            # Prompts the user for an email address if it's missing
            self.send_error(400, message='You must provide an email address and password!')
            return
            # If the email/password are invalid or not recognised
        if not email or not password:
            self.send_error(400, message='The email address and password are invalid!')
            return

        # Looks for the user's stored password, hash and display name(hashed)
        user = yield self.db.users.find_one({
            'email': email
        }, {
            'password': 1,
            'salt': 1,
            'displayName': 1,
            'displayName_iv': 1,
            'displayName_tag': 1
        })

        if user is None:
            self.send_error(403, message='The email address and password are invalid!')
            return

        salt = b64decode(user['salt'])
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=HASH_LENGTH,
            salt=salt,
            iterations=HASH_ITERATIONS,
            backend=default_backend()
        )

        try:
            kdf.verify(password.encode('utf-8'), b64decode(user['password']))
        except Exception:
            self.send_error(403, message='The email address and password are invalid!')
            return

        # Decrypt display name using central utility
        try:
            display_name = decrypt_field(
                user['displayName'],
                user['displayName_iv'],
                user['displayName_tag']
            ).decode('utf-8')
        except:
            display_name = "Unknown"

        token = yield self.generate_token(email)

        self.set_status(200)
        self.response = {
            "token": token['token'],
            "expiresIn": token['expiresIn'],
            "displayName": display_name
        }
        self.write_json()
