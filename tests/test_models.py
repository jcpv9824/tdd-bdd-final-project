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
import random 


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

    def test_read_a_product(self):
        """It should Read a Product"""
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        # Fetch it back
        found_product = Product.find(product.id)
        self.assertEqual(found_product.id, product.id)
        self.assertEqual(found_product.name, product.name)
        self.assertEqual(found_product.description, product.description)
        self.assertEqual(found_product.price, product.price)
    
    def test_update_a_product_without_id(self):
        """Updating a product without id"""

        #Crear un producto en base de datos
        product = ProductFactory()
        product.create()
        product_db = Product.find(product.id)
        self.assertEqual(product.name, product_db.name)

        #Actualizar nombre del producto sin id
        product.name = "Pooh"
        product.id = None
        self.assertRaises(DataValidationError, product.update)

    def test_update_a_product(self):
        """Updating a product"""

        #Crear un producto en base de datos
        product = ProductFactory()
        product.create()
        product_db = Product.find(product.id)
        self.assertEqual(product.name, product_db.name)

        #Actualizar nombre del producto
        product.name = "Pooh"
        product.update()
        product_db_updated = Product.find(product.id)
        self.assertEqual(product_db_updated.name, "Pooh")

    def test_delete_a_product(self):
        """Deleting a product"""

         #Crear un producto en base de datos
        product = ProductFactory()
        product.create()
        self.assertEqual(len(Product.all()), 1)

        #Eliminar producto de la base de datos
        product.delete()
        self.assertEqual(len(Product.all()), 0)

    def test_to_dict(self):
        """Serializes a Product into a dictionary"""

        product = ProductFactory()
        product_dic = product.serialize()
        self.assertEqual(product.name, product_dic["name"])
        self.assertEqual(product.id, product_dic["id"])
        self.assertEqual(product.description, product_dic["description"])
        self.assertEqual(float(product.price), float(product_dic["price"]))
        self.assertEqual(product.available, product_dic["available"])

    def test_list_all_products(self):
        """Listing all products"""
        #Crear productos en base de datos
        number_of_products = random.randint(2,15)
        for i in range(number_of_products):
            product = ProductFactory()
            product.create()
        #Obtener todos los productos
        self.assertEqual(len(Product.all()),number_of_products)

    def test_search_by_name(self):
        """Searching a product by name"""
        #Crear productos en base de datos
        number_of_products = random.randint(2,15)
        for i in range(number_of_products):
            product = ProductFactory()
            product.create()
        name = Product.all()[0].name

        #Se cuentan cuantos nombres productos con nombre iguales se generaron
        count = 0
        for i in Product.all():
            if i.name == name:
                count += 1
        #Se buscan los productos que tienen el mismo nombre y se cuentan
        found = Product.find_by_name(name)
        self.assertEqual(count, found.count())

    def test_search_by_category(self):
        """Searching a product by category"""
        # Crear productos en base de datos
        number_of_products = random.randint(2, 15)
        selected_category = Category.CLOTHS  # O cualquier otra categoría de tu elección
        for i in range(number_of_products):
            product = ProductFactory(category=selected_category)
            product.create()

        # Se cuentan cuántos productos de la categoría seleccionada se generaron
        count = 0
        for product in Product.all():
            if product.category == selected_category:
                count += 1

        # Se buscan los productos de esa categoría y se cuentan
        found_products = Product.find_by_category(selected_category)
        self.assertEqual(count, found_products.count())
        
    def test_search_by_availability(self):
        """Searching a product by availability"""
        #Crear productos en base de datos
        number_of_products = random.randint(2,15)
        for i in range(number_of_products):
            product = ProductFactory()
            product.create()
        availability = Product.all()[0].available

        #Se cuentan cuantos productos se generaron de disponibilidad aleatorea
        count = 0
        for i in Product.all():
            if i.available == availability:
                count += 1

        #Se buscan los productos que tienen la misma disponibilidad y se cuentan
        found = Product.find_by_availability(availability)
        self.assertEqual(count, found.count())

    def test_deserialize_product(self):
        """Deseliziling a product"""

        #A product is selialized
        product = ProductFactory()
        product_dic = product.serialize()
        self.assertEqual(product.name, product_dic["name"])
        self.assertEqual(product.id, product_dic["id"])
        self.assertEqual(product.description, product_dic["description"])
        self.assertEqual(float(product.price), float(product_dic["price"]))
        self.assertEqual(product.available, product_dic["available"])

        #The product is deserialized
        result = Product()
        result.deserialize(product_dic)
        self.assertEqual(result.name, product_dic["name"])
        self.assertEqual(result.description, product_dic["description"])
        self.assertEqual(float(result.price), float(product_dic["price"]))
        self.assertEqual(result.available, product_dic["available"])
    
    def test_deserialize_without_boolean(self):
        """Deserializing a product without a boolean"""

        # Un producto es serializado
        product = ProductFactory()
        product_dict = product.serialize()
        self.assertEqual(product.name, product_dict["name"])
        self.assertEqual(product.description, product_dict["description"])
        self.assertEqual(float(product.price), float(product_dict["price"]))
        self.assertEqual(product.available, product_dict["available"])

        # El producto es deserializado con un valor no booleano en 'available'
        product_dict["available"] = "No boolean value"
        result = Product()
        with self.assertRaises(DataValidationError): 
            result.deserialize(product_dict)

    def test_find_by_price(self):
        """finding products by price"""
        #Crear productos en base de datos
        number_of_products = random.randint(2,15)
        price = 200
        price_str = "200 "
        for i in range(number_of_products):
            product = ProductFactory(price = price)
            product.create()

        #Se cuentan cuantos productos cuestan 200
        count = 0
        for product in Product.all():
            if product.price == price:
                count += 1

        #Se buscan los productos que tienen el mismo precio y se cuentan
        found = Product.find_by_price(price_str)
        self.assertEqual(count, found.count())
    
    def test_deserialize_missing_attribute(self):
        """Deserializing a product with missing attribute"""
        product_dict = ProductFactory().serialize()
        del product_dict["name"]  # Eliminar un atributo necesario
        new_product = Product()
        with self.assertRaises(DataValidationError):
            new_product.deserialize(product_dict)

    def test_deserialize_with_invalid_category(self):
        """Deserializing a product with invalid 'category'"""
        product_dict = ProductFactory().serialize()
        product_dict["category"] = "InvalidCategory"
        new_product = Product()
        with self.assertRaises(DataValidationError):
            new_product.deserialize(product_dict)

    def test_deserialize_with_no_data(self):
        """Deserializing a product with no data"""
        product_dict = ProductFactory().serialize()
        product_dict = None
        new_product = Product()
        with self.assertRaises(DataValidationError):
            new_product.deserialize(product_dict)


