# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db, DataValidationError
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #
    def test_read_a_product(self):
        """it should read a product from the database"""
        product = ProductFactory()
        product.id = None
        product.create()
        found = Product.find(product.id)
        self.assertEqual(found.id, product.id)
        self.assertEqual(found.name, product.name)
        self.assertEqual(found.description, product.description)
        self.assertEqual(found.price, product.price)
        self.assertEqual(found.available, product.available)
        self.assertEqual(found.category, product.category)

    def test_update_a_product(self):
        """it should update a product"""
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        product.description = "testdescription"
        prodid = product.id
        product.update()
        self.assertEqual(product.description, "testdescription")
        self.assertEqual(product.id, prodid)
        products = Product.all()
        self.assertEqual(len(products), 1)
        new_product = products[0]
        self.assertEqual(product.id,  new_product.id)
        self.assertEqual(product.description, "testdescription")

    def test_upate_without_id(self):
        """it should raise an error when updating a product with no id"""
        product = Product(name="Test Product", id=None)
        with self.assertRaises(DataValidationError):
            product.update()

    def test_delete_a_product(self):
        """It should delete a product from the database"""
        product = ProductFactory()
        product.id = None
        product.create()
        products = Product.all()
        self.assertEqual(len(products), 1)
        product.delete()
        products = Product.all()
        self.assertEqual(len(products), 0)

    def test_list_all_products(self):
        """it should get a list with all products"""
        products = Product.all()
        self.assertEqual(len(products), 0)
        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()
        products = Product.all()
        self.assertEqual(len(products), 5)

    def test_find_product_by_name(self):
        """it should find a product by name"""
        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()
        name = products[0].name
        name_count = len([product for product in products if product.name == name])
        found_products = Product.find_by_name(name)
        self.assertEqual(found_products.count(), name_count)
        for product in found_products:
            self.assertEqual(product.name, name)

    def test_find_by_availability(self):
        """it should find products based on their availability"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        products = Product.all()
        availability = products[0].available
        count = len([product for product in products if product.available == availability])
        found_products = Product.find_by_availability(availability)
        self.assertEqual(found_products.count(), count)
        for product in found_products:
            self.assertEqual(product.available, availability)

    def test_find_by_category(self):
        """it should find products based on their category"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        products = Product.all()
        category = products[0].category
        count = len([product for product in products if product.category == category])
        found_products = Product.find_by_category(category)
        self.assertEqual(found_products.count(), count)
        for product in found_products:
            self.assertEqual(product.category, category)

    def test_find_by_price(self):
        """it should find products based on their price"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        products = Product.all()
        price = products[0].price
        self.assertEqual(type(price), Decimal)
        count = len([product for product in products if product.price == price])
        found_products = Product.find_by_price(price)
        self.assertEqual(found_products.count(), count)
        for product in found_products:
            self.assertEqual(product.price, price)
