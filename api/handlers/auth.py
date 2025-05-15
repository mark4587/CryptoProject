# Mark Doyle
# C00257481
from datetime import datetime
from time import mktime
from tornado.gen import coroutine

from .base import BaseHandler
from .Encrypt_Decrypt import decrypt_field

class AuthHandler(BaseHandler):

    @coroutine
    def prepare(self):
        super(AuthHandler, self).prepare()

        if self.request.method == 'OPTIONS':
            return

        # Try's to get the token from the request headers
        try:
            token = self.request.headers.get('X-Token')
            if not token:
              # Raises exception if the token is missing
              raise Exception()
        except:
            # If there's no token, it denies access and returns 400
            self.current_user = None
            self.send_error(400, message='You must provide a token!')
            return

        # Looks user up in the database by the token
        user = yield self.db.users.find_one({
            'token': token
        }, {
            'email': 1,
            'displayName': 1,
            'displayName_iv': 1,
            'displayName_tag': 1,
            'expiresIn': 1
        })

        # If no user's found with the token, it denies access
        if user is None:
            self.current_user = None
            self.send_error(403, message='Your token is invalid!')
            return

        # Check if the token's expired
        current_time = mktime(datetime.now().utctimetuple())
        if current_time > user['expiresIn']:
            self.current_user = None
            self.send_error(403, message='Your token has expired!')
            return

        # Decrypts the display name for current_user context
        try:
            display_name = decrypt_field(
                user['displayName'],
                user['displayName_iv'],
                user['displayName_tag']
            ).decode('utf-8')
        except:
            display_name = "Unknown"

        # If the token's valid and not expired, it stores the user in self.current_user
        self.current_user = {
            'email': user['email'],
            'display_name': display_name
        }
