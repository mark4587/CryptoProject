# Mark Doyle
# C00257481
from tornado.web import authenticated
from .auth import AuthHandler
from tornado.gen import coroutine
from .Encrypt_Decrypt import decrypt_field

class UserHandler(AuthHandler):

    @authenticated
    @coroutine
    def get(self):
        # Gets the user from the database by their email
        user = yield self.db.users.find_one({'email': self.current_user['email']})

        if not user:
            # If they're not found, return the error
            self.send_error(404, message="User not found")
            return
        
        # Uses Decrypt Field to decrypt the information
        def decrypt_safe(doc, field):
            try:
                return decrypt_field(
                    doc[field],
                    doc[f"{field}_iv"],
                    doc[f"{field}_tag"]
                ).decode('utf-8')
            except:
                return "Unknown"

        # Show Decrypted User Information
        self.set_status(200)
        self.response = {
            "email": user["email"],
            "displayName": decrypt_safe(user, "displayName"),
            "address": decrypt_safe(user, "address"),
            "dob": decrypt_safe(user, "dob"),
            "phoneNumber": decrypt_safe(user, "phoneNumber"),
            "disabilities": decrypt_safe(user, "disabilities")
        }
        self.write_json()
