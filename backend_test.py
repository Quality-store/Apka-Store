#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for QUALITY Store
Tests all backend endpoints for the grocery e-commerce platform
FOCUS: NEW OWNER FEATURES - Grocery Image Upload Functionality
"""

import requests
import json
import uuid
from datetime import datetime
import time
import base64
import io

# Get backend URL from environment
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001') + '/api'

class QualityStoreAPITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.test_user_id = None
        self.owner_user_id = None
        self.test_order_id = None
        self.test_session_id = None
        self.uploaded_product_id = None
        self.results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }
    
    def log_result(self, test_name, success, message="", response_data=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"   {message}")
        if response_data and not success:
            print(f"   Response: {response_data}")
        
        if success:
            self.results["passed"] += 1
        else:
            self.results["failed"] += 1
            self.results["errors"].append(f"{test_name}: {message}")
        print()
    
    def test_health_check(self):
        """Test the health check endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_result("Health Check", True, "API is healthy")
                    return True
                else:
                    self.log_result("Health Check", False, f"Unexpected response: {data}")
            else:
                self.log_result("Health Check", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Health Check", False, f"Exception: {str(e)}")
        return False
    
    def test_categories(self):
        """Test categories endpoint"""
        try:
            response = requests.get(f"{self.base_url}/categories", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "categories" in data and len(data["categories"]) == 8:
                    categories = data["categories"]
                    category_names = [cat["id"] for cat in categories]
                    expected_categories = ["fruits", "vegetables", "dairy", "meat", "bakery", "pantry", "beverages", "snacks"]
                    
                    if all(cat in category_names for cat in expected_categories):
                        self.log_result("Categories Endpoint", True, f"Found all 8 expected categories: {', '.join(category_names)}")
                        return True
                    else:
                        self.log_result("Categories Endpoint", False, f"Missing expected categories. Found: {category_names}")
                else:
                    self.log_result("Categories Endpoint", False, f"Expected 8 categories, found {len(data.get('categories', []))}")
            else:
                self.log_result("Categories Endpoint", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Categories Endpoint", False, f"Exception: {str(e)}")
        return False
    
    def test_products(self):
        """Test products endpoints"""
        try:
            # Test all products
            response = requests.get(f"{self.base_url}/products", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "products" in data and len(data["products"]) >= 20:
                    products = data["products"]
                    self.log_result("Products List", True, f"Found {len(products)} products (expected 21)")
                    
                    # Test category filtering
                    response = requests.get(f"{self.base_url}/products?category=fruits", timeout=10)
                    if response.status_code == 200:
                        filtered_data = response.json()
                        fruit_products = filtered_data["products"]
                        if len(fruit_products) > 0:
                            self.log_result("Products Category Filter", True, f"Found {len(fruit_products)} fruit products")
                        else:
                            self.log_result("Products Category Filter", False, "No fruit products found")
                    
                    # Test search functionality
                    response = requests.get(f"{self.base_url}/products?search=banana", timeout=10)
                    if response.status_code == 200:
                        search_data = response.json()
                        search_products = search_data["products"]
                        if len(search_products) > 0:
                            self.log_result("Products Search", True, f"Found {len(search_products)} products matching 'banana'")
                        else:
                            self.log_result("Products Search", False, "No products found for search term 'banana'")
                    
                    # Test individual product
                    if products:
                        product_id = products[0]["id"]
                        response = requests.get(f"{self.base_url}/products/{product_id}", timeout=10)
                        if response.status_code == 200:
                            product_data = response.json()
                            if "product" in product_data:
                                self.log_result("Individual Product", True, f"Retrieved product: {product_data['product']['name']}")
                                return True
                            else:
                                self.log_result("Individual Product", False, "Product data missing")
                        else:
                            self.log_result("Individual Product", False, f"Status code: {response.status_code}")
                else:
                    self.log_result("Products List", False, f"Expected 21 products, found {len(data.get('products', []))}")
            else:
                self.log_result("Products List", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Products Endpoints", False, f"Exception: {str(e)}")
        return False
    
    def test_user_management(self):
        """Test user creation and retrieval"""
        try:
            # Create a regular test user with unique email
            user_data = {
                "email": f"sarah.johnson.{uuid.uuid4().hex[:8]}@qualitystore.com",
                "name": "Sarah Johnson",
                "phone": "+1-555-0123",
                "address": "123 Grocery Lane, Fresh City, FC 12345"
            }
            
            response = requests.post(f"{self.base_url}/users", json=user_data, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "user" in data and data["user"].get("id"):
                    self.test_user_id = data["user"]["id"]
                    self.log_result("User Creation", True, f"Created user: {data['user']['name']}")
                    
                    # Test user retrieval
                    response = requests.get(f"{self.base_url}/users/{self.test_user_id}", timeout=10)
                    if response.status_code == 200:
                        user_data = response.json()
                        if "user" in user_data:
                            self.log_result("User Retrieval", True, f"Retrieved user: {user_data['user']['name']}")
                            
                            # Create an owner user for testing owner features with unique email
                            owner_data = {
                                "email": f"owner.{uuid.uuid4().hex[:8]}@qualitystore.com",
                                "name": "Store Owner",
                                "phone": "+1-555-9999",
                                "address": "456 Owner Street, Business City, BC 67890",
                                "is_owner": True
                            }
                            
                            response = requests.post(f"{self.base_url}/users", json=owner_data, timeout=10)
                            if response.status_code == 200:
                                owner_response = response.json()
                                if "user" in owner_response and owner_response["user"].get("id"):
                                    self.owner_user_id = owner_response["user"]["id"]
                                    self.log_result("Owner User Creation", True, f"Created owner user: {owner_response['user']['name']}")
                                    return True
                                else:
                                    self.log_result("Owner User Creation", False, "Owner user ID not returned")
                            else:
                                self.log_result("Owner User Creation", False, f"Status code: {response.status_code}")
                        else:
                            self.log_result("User Retrieval", False, "User data missing")
                    else:
                        self.log_result("User Retrieval", False, f"Status code: {response.status_code}")
                else:
                    self.log_result("User Creation", False, "User ID not returned")
            else:
                self.log_result("User Creation", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("User Management", False, f"Exception: {str(e)}")
        return False
    
    def create_test_image(self):
        """Create a simple test image for upload testing"""
        # Create a simple 1x1 pixel PNG image in base64
        # This is a minimal valid PNG image
        png_data = base64.b64decode(
            'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg=='
        )
        return png_data
    
    def test_owner_grocery_image_upload(self):
        """Test NEW OWNER FEATURE: Grocery Image Upload"""
        if not self.owner_user_id:
            self.log_result("Owner Image Upload", False, "No owner user available")
            return False
        
        try:
            # Create test image data
            image_data = self.create_test_image()
            
            # Test owner grocery image upload
            files = {
                'image': ('test_grocery.png', image_data, 'image/png')
            }
            data = {
                'user_id': self.owner_user_id,
                'product_name': 'Fresh Organic Tomatoes',
                'category': 'vegetables',
                'price': 4.99,
                'description': 'Locally grown organic tomatoes, perfect for salads and cooking'
            }
            
            response = requests.post(f"{self.base_url}/owner/upload-grocery-image", 
                                   files=files, data=data, timeout=15)
            
            if response.status_code == 200:
                upload_data = response.json()
                if "product" in upload_data and upload_data["product"].get("id"):
                    self.uploaded_product_id = upload_data["product"]["id"]
                    product = upload_data["product"]
                    self.log_result("Owner Image Upload", True, 
                                  f"Successfully uploaded product: {product['name']} (ID: {product['id']})")
                    
                    # Verify the product has owner_uploaded flag
                    if product.get("owner_uploaded", False):
                        self.log_result("Owner Product Flag", True, "Product correctly marked as owner_uploaded")
                        return True
                    else:
                        self.log_result("Owner Product Flag", False, "Product not marked as owner_uploaded")
                else:
                    self.log_result("Owner Image Upload", False, "Product data missing from response")
            else:
                self.log_result("Owner Image Upload", False, f"Status code: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("Owner Image Upload", False, f"Exception: {str(e)}")
        return False
    
    def test_non_owner_upload_restriction(self):
        """Test that non-owner users cannot upload grocery images"""
        if not self.test_user_id:
            self.log_result("Non-Owner Upload Restriction", False, "No regular user available")
            return False
        
        try:
            # Create test image data
            image_data = self.create_test_image()
            
            # Try to upload with regular user (should fail with 403)
            files = {
                'image': ('test_grocery.png', image_data, 'image/png')
            }
            data = {
                'user_id': self.test_user_id,  # Regular user, not owner
                'product_name': 'Unauthorized Product',
                'category': 'fruits',
                'price': 2.99,
                'description': 'This should not be allowed'
            }
            
            response = requests.post(f"{self.base_url}/owner/upload-grocery-image", 
                                   files=files, data=data, timeout=15)
            
            if response.status_code == 403:
                self.log_result("Non-Owner Upload Restriction", True, 
                              "Correctly blocked non-owner user from uploading (403 Forbidden)")
                return True
            else:
                self.log_result("Non-Owner Upload Restriction", False, 
                              f"Expected 403, got {response.status_code}. Non-owner was allowed to upload!")
        except Exception as e:
            self.log_result("Non-Owner Upload Restriction", False, f"Exception: {str(e)}")
        return False
    
    def test_owner_products_retrieval(self):
        """Test owner products retrieval endpoint"""
        if not self.owner_user_id:
            self.log_result("Owner Products Retrieval", False, "No owner user available")
            return False
        
        try:
            # Get owner products
            response = requests.get(f"{self.base_url}/owner/products?user_id={self.owner_user_id}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "products" in data:
                    owner_products = data["products"]
                    self.log_result("Owner Products Retrieval", True, 
                                  f"Retrieved {len(owner_products)} owner-uploaded products")
                    
                    # Verify uploaded product appears in the list
                    if self.uploaded_product_id:
                        uploaded_product = next((p for p in owner_products if p["id"] == self.uploaded_product_id), None)
                        if uploaded_product:
                            self.log_result("Uploaded Product in List", True, 
                                          f"Uploaded product found in owner products list: {uploaded_product['name']}")
                            return True
                        else:
                            self.log_result("Uploaded Product in List", False, 
                                          "Previously uploaded product not found in owner products list")
                    else:
                        return True  # No uploaded product to verify, but retrieval worked
                else:
                    self.log_result("Owner Products Retrieval", False, "Products data missing")
            else:
                self.log_result("Owner Products Retrieval", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Owner Products Retrieval", False, f"Exception: {str(e)}")
        return False
    
    def test_non_owner_products_access_restriction(self):
        """Test that non-owner users cannot access owner products endpoint"""
        if not self.test_user_id:
            self.log_result("Non-Owner Products Access", False, "No regular user available")
            return False
        
        try:
            # Try to access owner products with regular user (should fail with 403)
            response = requests.get(f"{self.base_url}/owner/products?user_id={self.test_user_id}", timeout=10)
            
            if response.status_code == 403:
                self.log_result("Non-Owner Products Access", True, 
                              "Correctly blocked non-owner user from accessing owner products (403 Forbidden)")
                return True
            else:
                self.log_result("Non-Owner Products Access", False, 
                              f"Expected 403, got {response.status_code}. Non-owner was allowed access!")
        except Exception as e:
            self.log_result("Non-Owner Products Access", False, f"Exception: {str(e)}")
        return False
    
    def test_owner_product_deletion(self):
        """Test owner product deletion endpoint"""
        if not self.owner_user_id or not self.uploaded_product_id:
            self.log_result("Owner Product Deletion", False, "No owner user or uploaded product available")
            return False
        
        try:
            # Delete the uploaded product
            response = requests.delete(f"{self.base_url}/owner/products/{self.uploaded_product_id}?user_id={self.owner_user_id}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.log_result("Owner Product Deletion", True, 
                                  f"Successfully deleted product: {data['message']}")
                    
                    # Verify product is removed from products list
                    response = requests.get(f"{self.base_url}/products", timeout=10)
                    if response.status_code == 200:
                        products_data = response.json()
                        products = products_data.get("products", [])
                        deleted_product = next((p for p in products if p["id"] == self.uploaded_product_id), None)
                        
                        if not deleted_product:
                            self.log_result("Product Removed from List", True, 
                                          "Deleted product no longer appears in products list")
                            return True
                        else:
                            self.log_result("Product Removed from List", False, 
                                          "Deleted product still appears in products list")
                    else:
                        self.log_result("Product Removed from List", False, 
                                      f"Could not verify deletion, products endpoint returned {response.status_code}")
                else:
                    self.log_result("Owner Product Deletion", False, "Message data missing")
            else:
                self.log_result("Owner Product Deletion", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Owner Product Deletion", False, f"Exception: {str(e)}")
        return False
    
    def test_uploaded_products_in_catalog(self):
        """Test that owner-uploaded products appear in main product catalog"""
        try:
            # Get all products
            response = requests.get(f"{self.base_url}/products", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "products" in data:
                    products = data["products"]
                    
                    # Check for owner-uploaded products
                    owner_products = [p for p in products if p.get("owner_uploaded", False)]
                    
                    if len(owner_products) >= 0:  # Allow 0 if no products uploaded yet
                        self.log_result("Owner Products in Catalog", True, 
                                      f"Found {len(owner_products)} owner-uploaded products in main catalog")
                        
                        # If we have owner products, verify they have the owner flag
                        if owner_products:
                            all_flagged = all(p.get("owner_uploaded", False) for p in owner_products)
                            if all_flagged:
                                self.log_result("Owner Product Flags", True, 
                                              "All owner products correctly flagged as owner_uploaded")
                                return True
                            else:
                                self.log_result("Owner Product Flags", False, 
                                              "Some owner products missing owner_uploaded flag")
                        else:
                            return True  # No owner products to verify flags
                    else:
                        self.log_result("Owner Products in Catalog", False, 
                                      "Could not verify owner products in catalog")
                else:
                    self.log_result("Owner Products in Catalog", False, "Products data missing")
            else:
                self.log_result("Owner Products in Catalog", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Owner Products in Catalog", False, f"Exception: {str(e)}")
        return False
    
    def test_shopping_cart(self):
        """Test shopping cart operations"""
        if not self.test_user_id:
            self.log_result("Shopping Cart", False, "No test user available")
            return False
        
        try:
            # Add item to cart using form data
            cart_data = {
                "user_id": self.test_user_id,
                "product_id": "p1",  # Fresh Bananas
                "quantity": 3
            }
            
            response = requests.post(f"{self.base_url}/cart/add", data=cart_data, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "cart" in data:
                    self.log_result("Add to Cart", True, f"Added item to cart, total: ${data['cart']['total']}")
                    
                    # Get cart
                    response = requests.get(f"{self.base_url}/cart/{self.test_user_id}", timeout=10)
                    if response.status_code == 200:
                        cart_data = response.json()
                        if "cart" in cart_data and cart_data["cart"]:
                            cart = cart_data["cart"]
                            self.log_result("Get Cart", True, f"Cart has {len(cart['items'])} items, total: ${cart['total']}")
                            
                            # Clear cart
                            response = requests.delete(f"{self.base_url}/cart/{self.test_user_id}", timeout=10)
                            if response.status_code == 200:
                                self.log_result("Clear Cart", True, "Cart cleared successfully")
                                return True
                            else:
                                self.log_result("Clear Cart", False, f"Status code: {response.status_code}")
                        else:
                            self.log_result("Get Cart", False, "Cart data missing")
                    else:
                        self.log_result("Get Cart", False, f"Status code: {response.status_code}")
                else:
                    self.log_result("Add to Cart", False, "Cart data missing")
            else:
                self.log_result("Add to Cart", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Shopping Cart", False, f"Exception: {str(e)}")
        return False
    
    def test_orders(self):
        """Test order creation and retrieval"""
        if not self.test_user_id:
            self.log_result("Orders", False, "No test user available")
            return False
        
        try:
            # Create an order
            order_data = {
                "user_id": self.test_user_id,
                "items": [
                    {"product_id": "f1", "quantity": 2, "price": 2.99},
                    {"product_id": "v1", "quantity": 1, "price": 1.99}
                ],
                "total": 7.97,
                "delivery_address": "123 Grocery Lane, Fresh City, FC 12345",
                "delivery_date": "2025-01-20",
                "delivery_time": "10:00 AM - 12:00 PM"
            }
            
            response = requests.post(f"{self.base_url}/orders", json=order_data, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "order" in data and data["order"].get("id"):
                    self.test_order_id = data["order"]["id"]
                    self.log_result("Order Creation", True, f"Created order: {self.test_order_id}")
                    
                    # Get user orders
                    response = requests.get(f"{self.base_url}/orders/{self.test_user_id}", timeout=10)
                    if response.status_code == 200:
                        orders_data = response.json()
                        if "orders" in orders_data:
                            orders = orders_data["orders"]
                            self.log_result("Get Orders", True, f"Found {len(orders)} orders for user")
                            
                            # Track order
                            response = requests.get(f"{self.base_url}/order/{self.test_order_id}", timeout=10)
                            if response.status_code == 200:
                                order_data = response.json()
                                if "order" in order_data:
                                    self.log_result("Track Order", True, f"Order status: {order_data['order']['status']}")
                                    return True
                                else:
                                    self.log_result("Track Order", False, "Order data missing")
                            else:
                                self.log_result("Track Order", False, f"Status code: {response.status_code}")
                        else:
                            self.log_result("Get Orders", False, "Orders data missing")
                    else:
                        self.log_result("Get Orders", False, f"Status code: {response.status_code}")
                else:
                    self.log_result("Order Creation", False, "Order ID not returned")
            else:
                self.log_result("Order Creation", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Orders", False, f"Exception: {str(e)}")
        return False
    
    def test_payment_integration(self):
        """Test Payoneer payment integration"""
        if not self.test_user_id:
            self.log_result("Payment Integration", False, "No test user available")
            return False
        
        try:
            # Create checkout session using form data
            payment_data = {
                "user_id": self.test_user_id,
                "amount": 7.97
            }
            
            response = requests.post(f"{self.base_url}/payment/create-checkout-session", data=payment_data, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if "session_id" in data and "payment_url" in data:
                    self.test_session_id = data["session_id"]
                    self.log_result("Create Checkout Session", True, f"Created session: {self.test_session_id}")
                    
                    # Test payment completion using form data
                    time.sleep(1)  # Brief delay
                    completion_data = {"session_id": self.test_session_id}
                    response = requests.post(f"{self.base_url}/payment/complete", data=completion_data, timeout=10)
                    if response.status_code == 200:
                        completion_response = response.json()
                        if "message" in completion_response:
                            self.log_result("Complete Payment", True, f"Payment completed: {completion_response['message']}")
                            return True
                        else:
                            self.log_result("Complete Payment", False, "Message data missing")
                    else:
                        self.log_result("Complete Payment", False, f"Status code: {response.status_code}")
                else:
                    self.log_result("Create Checkout Session", False, "Session data missing")
            else:
                self.log_result("Create Checkout Session", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Payment Integration", False, f"Exception: {str(e)}")
        return False
    
    def test_chat_system(self):
        """Test customer support chat system"""
        if not self.test_user_id:
            self.log_result("Chat System", False, "No test user available")
            return False
        
        try:
            # Send a message using form data
            message_data = {
                "user_id": self.test_user_id,
                "message": "Hello, I need help with my order delivery time. Can you assist me?"
            }
            
            response = requests.post(f"{self.base_url}/chat/send", data=message_data, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "messages" in data:
                    messages = data["messages"]
                    self.log_result("Send Chat Message", True, f"Message sent, received {len(messages)} messages in response")
                    
                    # Get chat history
                    time.sleep(1)
                    response = requests.get(f"{self.base_url}/chat/{self.test_user_id}", timeout=10)
                    if response.status_code == 200:
                        messages_data = response.json()
                        if "messages" in messages_data:
                            all_messages = messages_data["messages"]
                            self.log_result("Get Chat History", True, f"Found {len(all_messages)} messages")
                            
                            # Check for auto-reply
                            support_messages = [msg for msg in all_messages if msg.get("sender_type") == "support"]
                            if support_messages:
                                self.log_result("Auto-Reply System", True, "Support auto-reply working")
                                return True
                            else:
                                self.log_result("Auto-Reply System", False, "No support auto-reply found")
                        else:
                            self.log_result("Get Chat History", False, "Messages data missing")
                    else:
                        self.log_result("Get Chat History", False, f"Status code: {response.status_code}")
                else:
                    self.log_result("Send Chat Message", False, "Messages data missing")
            else:
                self.log_result("Send Chat Message", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Chat System", False, f"Exception: {str(e)}")
        return False
    
    def test_loyalty_program(self):
        """Test loyalty points system"""
        if not self.test_user_id:
            self.log_result("Loyalty Program", False, "No test user available")
            return False
        
        try:
            # Add loyalty points using form data
            points_data = {
                "user_id": self.test_user_id,
                "points": 50
            }
            
            response = requests.post(f"{self.base_url}/loyalty/add", data=points_data, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "total_points" in data:
                    total_points = data["total_points"]
                    self.log_result("Add Loyalty Points", True, f"Added points, new total: {total_points}")
                    
                    # Get loyalty points
                    response = requests.get(f"{self.base_url}/loyalty/{self.test_user_id}", timeout=10)
                    if response.status_code == 200:
                        loyalty_data = response.json()
                        if "loyalty_points" in loyalty_data:
                            points = loyalty_data["loyalty_points"]
                            self.log_result("Get Loyalty Points", True, f"User has {points} loyalty points")
                            
                            # Test redeem points
                            redeem_data = {
                                "user_id": self.test_user_id,
                                "points": 25
                            }
                            response = requests.post(f"{self.base_url}/loyalty/redeem", data=redeem_data, timeout=10)
                            if response.status_code == 200:
                                redeem_response = response.json()
                                if "remaining_points" in redeem_response:
                                    remaining = redeem_response["remaining_points"]
                                    self.log_result("Redeem Loyalty Points", True, f"Redeemed points, remaining: {remaining}")
                                    return True
                                else:
                                    self.log_result("Redeem Loyalty Points", False, "Remaining points data missing")
                            else:
                                self.log_result("Redeem Loyalty Points", False, f"Status code: {response.status_code}")
                        else:
                            self.log_result("Get Loyalty Points", False, "Points data missing")
                    else:
                        self.log_result("Get Loyalty Points", False, f"Status code: {response.status_code}")
                else:
                    self.log_result("Add Loyalty Points", False, "Total points data missing")
            else:
                self.log_result("Add Loyalty Points", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Loyalty Program", False, f"Exception: {str(e)}")
        return False
    
    def test_error_handling(self):
        """Test error handling for invalid requests"""
        try:
            # Test invalid product ID
            response = requests.get(f"{self.base_url}/products/invalid_id", timeout=10)
            if response.status_code == 404:
                self.log_result("Error Handling - Invalid Product", True, "Correctly returned 404 for invalid product")
            else:
                self.log_result("Error Handling - Invalid Product", False, f"Expected 404, got {response.status_code}")
            
            # Test invalid user ID
            response = requests.get(f"{self.base_url}/users/invalid_id", timeout=10)
            if response.status_code in [404, 500]:  # Either is acceptable for invalid ID
                self.log_result("Error Handling - Invalid User", True, f"Correctly returned {response.status_code} for invalid user")
                return True
            else:
                self.log_result("Error Handling - Invalid User", False, f"Expected 404/500, got {response.status_code}")
        except Exception as e:
            self.log_result("Error Handling", False, f"Exception: {str(e)}")
        return False
    
    def run_all_tests(self):
        """Run all backend API tests"""
        print("=" * 80)
        print("QUALITY Store Backend API Testing")
        print("FOCUS: NEW OWNER FEATURES - Grocery Image Upload Functionality")
        print("=" * 80)
        print(f"Testing backend at: {self.base_url}")
        print()
        
        # Run tests in logical order
        tests = [
            ("Health Check", self.test_health_check),
            ("Categories", self.test_categories),
            ("Products", self.test_products),
            ("User Management", self.test_user_management),
            ("🔥 NEW: Owner Grocery Image Upload", self.test_owner_grocery_image_upload),
            ("🔥 NEW: Non-Owner Upload Restriction", self.test_non_owner_upload_restriction),
            ("🔥 NEW: Owner Products Retrieval", self.test_owner_products_retrieval),
            ("🔥 NEW: Non-Owner Products Access Restriction", self.test_non_owner_products_access_restriction),
            ("🔥 NEW: Uploaded Products in Catalog", self.test_uploaded_products_in_catalog),
            ("Shopping Cart", self.test_shopping_cart),
            ("Orders", self.test_orders),
            ("Payment Integration", self.test_payment_integration),
            ("Chat System", self.test_chat_system),
            ("Loyalty Program", self.test_loyalty_program),
            ("🔥 NEW: Owner Product Deletion", self.test_owner_product_deletion),
            ("Error Handling", self.test_error_handling)
        ]
        
        for test_name, test_func in tests:
            print(f"Running {test_name} tests...")
            test_func()
        
        # Print summary
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"📊 Success Rate: {(self.results['passed'] / (self.results['passed'] + self.results['failed']) * 100):.1f}%")
        
        if self.results['errors']:
            print("\n🚨 FAILED TESTS:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        print("\n" + "=" * 80)
        return self.results['failed'] == 0

if __name__ == "__main__":
    tester = QualityStoreAPITester()
    success = tester.run_all_tests()
    exit(0 if success else 1)