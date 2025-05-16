import json
from tornado.web import Application
from api.handlers.login import LoginHandler
from api.handlers.registration import RegistrationHandler
from .base import BaseTest

class LoginHandlerTest(BaseTest):

    @classmethod
    def setUpClass(cls):
        # Calls the login and registration handlers
        cls.my_app = Application([
            (r'/login', LoginHandler),
            (r'/registration', RegistrationHandler),
        ])
        super().setUpClass()

    def setUp(self):
        super().setUp()
        # Hard-coded user
        body = {
            "email": "test@test.com",
            "password": "testPassword123",
            "displayName": "testName",
            "address": "123 White Street",
            "dob": "01-01-2001",
            "phoneNumber": "123456789",
            "disabilities": "asthma"
        }
        self.fetch('/registration', method='POST', body=json.dumps(body))

    def test_login(self):
        body = {
            "email": "test@test.com",
            "password": "testPassword123"
        }
        response = self.fetch('/login', method='POST', body=json.dumps(body))
        self.assertEqual(200, response.code)

    # Testing Case Sensitivity
    def test_login_case_insensitive(self):
        body = {
            "email": "TEST@TEST.com",
            "password": "testPassword123"
        }
        response = self.fetch('/login', method='POST', body=json.dumps(body))
        self.assertEqual(200, response.code)

  # Testing if a wrong password is accepted
    def test_login_wrong_password(self):
        body = {
            "email": "test@test.com",
            "password": "wrongPassword"
        }
        response = self.fetch('/login', method='POST', body=json.dumps(body))
        self.assertEqual(403, response.code)

    # Test if an unkown user can log in
    def test_login_nonexistent_user(self):
        body = {
            "email": "unknownUserl@fakeUser.com",
            "password": "password"
        }
        response = self.fetch('/login', method='POST', body=json.dumps(body))
        self.assertEqual(403, response.code)
