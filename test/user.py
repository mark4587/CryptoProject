import json
from tornado.web import Application
from api.handlers.registration import RegistrationHandler
from api.handlers.login import LoginHandler
from api.handlers.user import UserHandler
from .base import BaseTest

class UserHandlerTest(BaseTest):

    @classmethod
    def setUpClass(cls):
        # Calls handlers
        cls.my_app = Application([
            (r'/registration', RegistrationHandler),
            (r'/login', LoginHandler),
            (r'/user', UserHandler),
        ])
        super().setUpClass()

    def setUp(self):
        super().setUp()
        # Registers the test user
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

        # Logs in to get token
        login_body = {
            "email": "test@test.com",
            "password": "testPassword123"
        }
        response = self.fetch('/login', method='POST', body=json.dumps(login_body))
        self.token = json.loads(response.body.decode())['token']

    def test_user(self):
        response = self.fetch('/user', method='GET', headers={"X-Token": self.token})
        self.assertEqual(200, response.code)

        body = json.loads(response.body)
        self.assertEqual("test@test.com", body["email"])
        self.assertEqual("testName", body["displayName"])
        self.assertEqual("123 White Street", body["address"])
        self.assertEqual("01-01-2001", body["dob"])
        self.assertEqual("123456789", body["phoneNumber"])
        self.assertEqual("asthma", body["disabilities"])
