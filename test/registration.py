from json import dumps
from tornado.escape import json_decode
from tornado.web import Application
from api.handlers.registration import RegistrationHandler
from .base import BaseTest

class RegistrationHandlerTest(BaseTest):

    @classmethod
    def setUpClass(cls):
        # Calls handlers 
        cls.my_app = Application(
        [
            (r'/registration', RegistrationHandler),
        ])
        super().setUpClass()

  # User Information
    def test_registration(self):
        email = 'test@test.com'
        display_name = 'testName'
        address = '123 White Street'
        dob = '01-01-2001'
        phone_number = '123456789'
        disabilities = 'asthma'

      # Creates the user with the pulled information 
        body = {
            'email': email,
            'password': 'testPassword123',
            'displayName': display_name,
            'address': address,
            'dob': dob,
            'phoneNumber': phone_number,
            'disabilities': disabilities
        }

        response = self.fetch('/registration', method='POST', body=dumps(body))
        # Checks server connection with 200 code
        self.assertEqual(200, response.code)

        # Decodes the JSON information and is placed into 'data'
        data = json_decode(response.body)
        self.assertEqual(email, data['email'])
        self.assertEqual(display_name, data['displayName'])
        self.assertEqual(address, data['address'])
        self.assertEqual(dob, data['dob'])
        self.assertEqual(phone_number, data['phoneNumber'])
        self.assertEqual(disabilities, data['disabilities'])
