from app import create_app
from app.models import db, Mechanic
from app.utils.util import encode_mechanic_token
import unittest

class TestMechanic(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.mechanic = Mechanic(
            name='test_mechanic',
            email='mechanic@test.com',
            phone='9876543210',
            password='mechanicpassword',
            salary=50000.0,
        )

        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.mechanic)
            db.session.commit()

        self.client = self.app.test_client()

    def test_create_mechanic(self):
        mechanic_payload = {
            'name': 'Jane Doe',
            'email': 'jd@auto.com',
            'phone': '9876543210',
            'password': 'mechanicpassword',
            'salary': 60000.0,
        }

        response = self.client.post('/mechanics', json=mechanic_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], 'Jane Doe')
        self.assertEqual(response.json['salary'], 60000.0)

    def test_invalid_creation(self):
        mechanic_payload = {
            'name': 'Jane Doe',
            'email': 'jd@auto.com',
            'phone': '9876543210',
            'password': 'mechanicpassword',
            # Missing salary
        }

        response = self.client.post('/mechanics', json=mechanic_payload)
        self.assertEqual(response.status_code, 400)

    def test_login_mechanic(self):
        mechanic_payload = {
            'name': 'Jane Doe',
            'email': 'jd@auto.com',
            'phone': '9876543210',
            'password': 'mechanicpassword',
            'salary': 60000.0,
        }

        self.client.post('/mechanics', json=mechanic_payload)

        credentials = {
            'email': 'jd@auto.com',
            'password': 'mechanicpassword'
        }

        response = self.client.post('/mechanics/login', json=credentials)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'success')
        return response.json['token']
    
    def test_invalid_login(self):
        credentials = {
            'email': 'bad_email@auto.com',
            'password': 'wrongpassword'
        }

        response = self.client.post('/mechanics/login', json=credentials)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message'], 'Invalid email or password')

    def test_get_mechanics(self):
        response = self.client.get('/mechanics/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json) > 0)
        self.assertEqual(response.json[0]['name'], 'test_mechanic')

    def test_update_mechanic(self):
        token = self.test_login_mechanic()

        update_payload = {
            'name': 'Updated Mechanic',
            'phone': '1234567890',
            'email': 'mechanic@test.com',
            'password': 'newpassword',
            'salary': 70000.0,
        }

        headers = {'Authorization': 'Bearer ' + token}
        response = self.client.put('/mechanics/', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'Updated Mechanic')
        self.assertEqual(response.json['salary'], 70000.0)

    def test_delete_mechanic(self):
        token = self.test_login_mechanic()

        headers = {'Authorization': 'Bearer ' + token}

        response = self.client.delete('/mechanics/', headers=headers)
        self.assertEqual(response.status_code, 200)

        mechanic_id = 2
        expected_message = f'successfully deleted mechanic {mechanic_id}'
        self.assertEqual(response.json['message'], expected_message)

    def test_popular_mechanics(self):
        response = self.client.get('/mechanics/popular')
        self.assertEqual(response.status_code, 200)

    def test_search_mechanics(self):
        response = self.client.get('/mechanics/search?name=test')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json) > 0)
        self.assertEqual(response.json[0]['name'], 'test_mechanic')
