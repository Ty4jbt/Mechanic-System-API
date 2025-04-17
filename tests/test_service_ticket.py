from app import create_app
from app.models import db, ServiceTicket, Customer, Mechanic, Inventory
from app.utils.util import encode_customer_token
import unittest
from datetime import date

class TestServiceTicket(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')

        self.customer = Customer(
            name='test_customer',
            email='customer@test.com',
            phone='1234567890',
            password='customerpassword'
        )

        self.mechanic = Mechanic(
            name='test_mechanic',
            email='mechanic@test.com',
            phone='9876543210',
            password='mechanicpassword',
            salary=50000.0
        )

        self.inventory_item = Inventory(
            name='Test Part',
            price=100.0,
            quantity_in_stock=50
        )

        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add_all([self.customer, self.mechanic, self.inventory_item])
            db.session.commit()

            self.service_ticket = ServiceTicket(
                customer_id=1,
                date_created=date.today(),
                desc='Test description',
                VIN='1HGCM82633A123456',
                total_cost=200.0,
            )

            self.service_ticket.mechanics.append(self.mechanic)

            db.session.add(self.service_ticket)
            db.session.commit()

        self.client = self.app.test_client()

    def test_create_service_ticket(self):
        service_ticket_payload = {
            "customer_id": 1,
            "desc": "Test description",
            "VIN": "1HGCM82633A123456",
            "date_created": date.today().isoformat(),
            "mechanic_ids": [1]
        }

        response = self.client.post('/service_tickets', json=service_ticket_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['desc'], 'Test description')
        self.assertEqual(response.json['VIN'], '1HGCM82633A123456')
        self.assertEqual(response.json['customer']['id'], 1)
        self.assertEqual(len(response.json['mechanics']), 1)
        self.assertEqual(response.json['mechanics'][0]['id'], 1)

    def test_invalid_creation(self):
        service_ticket_payload = {
            "customer_id": 1,
            "desc": "Test description",
            # Missing VIN
            "date_created": date.today().isoformat(),
            "mechanics": [1]
        }

        response = self.client.post('/service_tickets', json=service_ticket_payload)
        self.assertEqual(response.status_code, 400)

    def test_get_service_tickets(self):
        response = self.client.get('/service_tickets')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json) > 0)
        self.assertEqual(response.json[0]['desc'], 'Test description')

    def test_update_service_ticket(self):
        with self.app.app_context():
            another_mechanic = Mechanic(
                name='another_mechanic',
                email='another@test.com',
                phone='1231231234',
                password='anotherpassword',
                salary=60000.0
            )

            db.session.add(another_mechanic)
            db.session.commit()

        update_payload = {
            'add_mechanic_ids': [2],
            'remove_mechanic_ids': [],
        }

        response = self.client.put('/service_tickets/1', json=update_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json['mechanics']), 2)

    def test_delete_service_ticket(self):
        response = self.client.delete('/service_tickets/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Succesfully deleted service ticket', response.json['message'])

    def test_add_inventory_to_service_ticket(self):
        inventory_payload = {
            "inventory_ids": [1],
            "quantities": [2]
        }

        response = self.client.post('/service_tickets/1/inventory', json=inventory_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['service_ticket']['id'], 1)
        self.assertAlmostEqual(response.json['total_cost'], 200.0)

        inventory_response = self.client.get('/inventory/1')
        self.assertEqual(inventory_response.json['quantity_in_stock'], 48)

    def test_get_ticket_inventory(self):
        inventory_payload = {
            'inventory_ids': [1],
            'quantities': [2]
        }

        self.client.post('/service_tickets/1/inventory', json=inventory_payload)

        response = self.client.get('/service_tickets/1/inventory')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json['items']) > 0)
        self.assertEqual(response.json['items_with_quantity'][0]['name'], 'Test Part')
        self.assertEqual(response.json['items_with_quantity'][0]['quantity'], 2)

    def test_remove_inventory_from_ticket(self):
        inventory_payload = {
            "inventory_ids": [1],
            "quantities": [2]
        }
        self.client.post('/service_tickets/1/inventory', json=inventory_payload)
        
        initial_inventory = self.client.get('/inventory/1')
        initial_quantity = initial_inventory.json['quantity_in_stock']
        
        response = self.client.delete('/service_tickets/1/inventory/1')
        self.assertEqual(response.status_code, 200)
        
        inventory_response = self.client.get('/inventory/1')
        self.assertEqual(inventory_response.json['quantity_in_stock'], initial_quantity + 2)

    def test_get_service_ticket_receipt(self):
        inventory_payload = {
            "inventory_ids": [1],
            "quantities": [2]
        }

        self.client.post('/service_tickets/1/inventory', json=inventory_payload)
        
        response = self.client.get('/service_tickets/1/receipt')
        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(response.json['total_cost'], 200.0)
        self.assertEqual(response.json['service_ticket']['id'], 1)
        self.assertEqual(len(response.json['items']), 1)
        self.assertEqual(response.json['items'][0]['name'], 'Test Part')
        self.assertEqual(response.json['items'][0]['quantity'], 2)

    def test_get_customer_tickets(self):
        with self.app.app_context():
            token = encode_customer_token(1)
        
        headers = {'Authorization': 'Bearer ' + token}
        
        response = self.client.get('/service_tickets/my-tickets', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json) > 0)
        self.assertEqual(response.json[0]['customer']['id'], 1)