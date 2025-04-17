from app import create_app
from app.models import db, Customer
from app.utils import encode_customer_token
import unittest

class TestCustomer(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.customer = Customer(name='test_user', email='test@email.com', phone='1234567890', password='password123')
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.customer)
            db.session.commit()
        self.token = encode_customer_token(1)
        self.client = self.app.test_client()

    def test_create_customer(self):
        customer_payload = {
            "name": "John Doe",
            "email": "jd@email.com",
            "phone": "1234567890",
            "password": "password123"
        }

        response = self.client.post('/customers', json=customer_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], 'John Doe')

    def test_invalid_creation(self):
        customer_payload = {
            "name": "John Doe",
            "phone": "1234567890",
            "password": "password123"
        }

        response = self.client.post('/customers', json=customer_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['email'], 'Missing data for required field.')

    def test_login_customer(self):
        credentials = {
            'email': 'test@email.com',
            'password': 'password123'
        }

        response = self.client.post('/customers/login', json=credentials)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'success')
        return response.json['token']
    
    def test_invalid_login(self):
        credentials = {
            'email': 'bad_email@email.com',
            'password': 'wrongpassword'
        }

        response = self.client.post('/customers/login', json=credentials)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message'], 'Invalid email or password')

    def test_update_customer(self):
        update_payload = {
            'name': 'Updated Name',
            'phone': '',
            'email': '',
            'password': ''
        }

        headers = {'Authorization': 'Bearer ' + self.test_login_customer()}

        response = self.client.put('/customers/', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'Updated Name')
        self.assertEqual(response.json['email'], 'test@email.com')