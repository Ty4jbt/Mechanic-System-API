from app import create_app
from app.models import db, Order, Mechanic, Inventory, OrderItems
import unittest
from datetime import date

class TestOrders(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')

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
            db.session.add_all([self.mechanic, self.inventory_item])
            db.session.commit()

        self.client = self.app.test_client()

    def test_create_order(self):
        initial_inventory = self.client.get('/inventory/1')
        initial_quantity = initial_inventory.json['quantity_in_stock']

        order_payload = {
            'mechanic_id': 1,
            'inventory_items': [
                {
                    'inventory_id': 1,
                    'quantity': 2
                }
            ]
        }

        response = self.client.post('/orders', json=order_payload)

        self.assertEqual(response.status_code, 201)
        self.assertAlmostEqual(response.json['total_cost'], 200.0, places=2)
        self.assertEqual(response.json['order']['mechanic_id'], 1)

        order_response = self.client.get('/orders/1')
        self.assertEqual(order_response.status_code, 200)
        self.assertEqual(order_response.json['id'], 1)

        self.assertTrue('order_items' in order_response.json)
        self.assertEqual(len(order_response.json['order_items']), 1)

        inventory_response = self.client.get('/inventory/1')
        expected_quantity = initial_quantity + 2
        self.assertEqual(inventory_response.json['quantity_in_stock'], expected_quantity)

        receipt_response = self.client.get('/orders/1/receipt')
        self.assertEqual(receipt_response.status_code, 200)
        self.assertAlmostEqual(receipt_response.json['total_cost'], 200.0, places=2)

    def test_invalid_creation(self):
        order_payload = {
            'mechanic_id': 1,
            'inventory_items': [
                {
                    'inventory_id': 44,
                    'quantity': 2
                }
            ]
        }

        response = self.client.post('/orders', json=order_payload)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['message'], 'Inventory item with ID not found')

    def test_get_orders(self):
        order_payload = {
            'mechanic_id': 1,
            'inventory_items': [
                {
                    'inventory_id': 1,
                    'quantity': 2
                }
            ]
        }

        self.client.post('/orders', json=order_payload)

        response = self.client.get('/orders')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json) > 0)
        self.assertEqual(response.json[0]['mechanic_id'], 1)

    def test_get_order_by_id(self):
        order_payload = {
            'mechanic_id': 1,
            'inventory_items': [
                {
                    'inventory_id': 1,
                    'quantity': 2
                }
            ]
        }

        self.client.post('/orders', json=order_payload)

        response = self.client.get('/orders/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['id'], 1)
        self.assertEqual(response.json['mechanic_id'], 1)

    def test_get_order_receipt(self):
        order_payload = {
            'mechanic_id': 1,
            'inventory_items': [
                {
                    'inventory_id': 1,
                    'quantity': 2
                }
            ]
        }

        self.client.post('/orders', json=order_payload)

        response = self.client.get('/orders/1/receipt')
        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(response.json['total_cost'], 200.0)
        self.assertEqual(response.json['order']['id'], 1)
        self.assertEqual(len(response.json['items']), 1)
        self.assertEqual(response.json['items'][0]['name'], 'Test Part')
        self.assertEqual(response.json['items'][0]['quantity'], 2)