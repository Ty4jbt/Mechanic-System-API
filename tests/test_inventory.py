from app import create_app
from app.models import db, Inventory
import unittest

class TestInventory(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.inventory_item = Inventory(
            name='Test Part',
            price=100.0,
            quantity_in_stock=50
        )

        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.inventory_item)
            db.session.commit()

        self.client = self.app.test_client()

    def test_create_inventory_item(self):
        inventory_payload = {
            "name": "Brake Pads",
            "price": 50.0,
            "quantity_in_stock": 20
        }

        response = self.client.post('/inventory/', json=inventory_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], 'Brake Pads')
        self.assertEqual(response.json['price'], 50.0)
        self.assertEqual(response.json['quantity_in_stock'], 20)

    def test_invalid_creation(self):
        inventory_payload = {
            "name": "Brake Pads",
            # Missing price
            "quantity_in_stock": 20
        }

        response = self.client.post('/inventory/', json=inventory_payload)
        self.assertEqual(response.status_code, 400)

    def test_get_inventory_items(self):
        response = self.client.get('/inventory/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json) > 0)
        self.assertEqual(response.json[0]['name'], 'Test Part')

    def test_get_inventory_item(self):
        response = self.client.get('/inventory/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'Test Part')
        self.assertEqual(response.json['price'], 100.0)

    def test_update_inventory_item(self):
        update_payload = {
            "name": "Updated Part",
            "price": 120.0,
            "quantity_in_stock": 30
        }

        response = self.client.put('/inventory/1', json=update_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'Updated Part')
        self.assertEqual(response.json['price'], 120.0)
        self.assertEqual(response.json['quantity_in_stock'], 30)

    def test_delete_inventory_item(self):
        response = self.client.delete('/inventory/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'successfully deleted inventory item 1')

    def test_popular_inventory(self):
        response = self.client.get('/inventory/popular')
        self.assertEqual(response.status_code, 200)

    def test_search_inventory(self):
        response = self.client.get('/inventory/search?name=Test')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json) > 0)
        self.assertEqual(response.json[0]['name'], 'Test Part')

    def test_low_stock_inventory(self):
        low_stock_item = Inventory(
            name='Low Stock Part',
            price=50.0,
            quantity_in_stock=3
        )

        with self.app.app_context():
            db.session.add(low_stock_item)
            db.session.commit()

        response = self.client.get('/inventory/low-stock')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json) > 0)