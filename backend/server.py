from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from datetime import datetime, timedelta
import base64
from typing import List, Optional
import hashlib
import secrets
import jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

app = FastAPI(title="QUALITY Store API", description="Grocery Store Management System")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
SECRET_KEY = "quality_store_secret_key_2024"
ALGORITHM = "HS256"

# Authorized owner phone numbers (only these 2 can be owners)
AUTHORIZED_OWNER_PHONES = [
    "+85254061680",  # Owner 1
    "+85211223344"   # Owner 2 (example second number)
]

# Sample data with expanded categories and products
SAMPLE_PRODUCTS = [
    # Fruits
    {"id": "1", "name": "Fresh Bananas", "category": "fruits", "price": 2.99, "image_url": "https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?w=300", "description": "Fresh yellow bananas, rich in potassium", "owner_uploaded": False, "stock": 50},
    {"id": "2", "name": "Organic Apples", "category": "fruits", "price": 4.99, "image_url": "https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=300", "description": "Crisp organic apples, perfect for snacking", "owner_uploaded": False, "stock": 30},
    {"id": "3", "name": "Fresh Oranges", "category": "fruits", "price": 3.49, "image_url": "https://images.unsplash.com/photo-1547514701-42782101795e?w=300", "description": "Juicy Valencia oranges, high in Vitamin C", "owner_uploaded": False, "stock": 40},
    {"id": "4", "name": "Red Grapes", "category": "fruits", "price": 5.99, "image_url": "https://images.unsplash.com/photo-1537640538966-79f369143f8f?w=300", "description": "Sweet red grapes, seedless variety", "owner_uploaded": False, "stock": 25},
    
    # Vegetables
    {"id": "5", "name": "Fresh Tomatoes", "category": "vegetables", "price": 3.29, "image_url": "https://images.unsplash.com/photo-1546470427-e5d491d7a6fe?w=300", "description": "Ripe red tomatoes, perfect for cooking", "owner_uploaded": False, "stock": 60},
    {"id": "6", "name": "Green Broccoli", "category": "vegetables", "price": 2.79, "image_url": "https://images.unsplash.com/photo-1459411621453-7b03977f4bfc?w=300", "description": "Fresh green broccoli crowns", "owner_uploaded": False, "stock": 35},
    {"id": "7", "name": "Organic Carrots", "category": "vegetables", "price": 2.49, "image_url": "https://images.unsplash.com/photo-1445282768818-728615cc910a?w=300", "description": "Organic carrots, sweet and crunchy", "owner_uploaded": False, "stock": 45},
    {"id": "8", "name": "Fresh Spinach", "category": "vegetables", "price": 1.99, "image_url": "https://images.unsplash.com/photo-1576045057995-568f588f82fb?w=300", "description": "Fresh baby spinach leaves", "owner_uploaded": False, "stock": 40},
    {"id": "9", "name": "Bell Peppers", "category": "vegetables", "price": 4.29, "image_url": "https://images.unsplash.com/photo-1563565375-f3fdfdbefa83?w=300", "description": "Mixed colored bell peppers", "owner_uploaded": False, "stock": 30},
    
    # Pulses & Legumes
    {"id": "10", "name": "Red Lentils", "category": "pulses", "price": 3.99, "image_url": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=300", "description": "Premium red lentils, 1kg pack", "owner_uploaded": False, "stock": 80},
    {"id": "11", "name": "Chickpeas", "category": "pulses", "price": 4.49, "image_url": "https://images.unsplash.com/photo-1610348725531-843dff563e2c?w=300", "description": "Dried chickpeas, excellent source of protein", "owner_uploaded": False, "stock": 70},
    {"id": "12", "name": "Black Beans", "category": "pulses", "price": 3.79, "image_url": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=300", "description": "Organic black beans, 500g pack", "owner_uploaded": False, "stock": 60},
    {"id": "13", "name": "Green Peas", "category": "pulses", "price": 2.99, "image_url": "https://images.unsplash.com/photo-1586201375318-d1b6c2e96e66?w=300", "description": "Dried green peas, perfect for soups", "owner_uploaded": False, "stock": 55},
    
    # Dairy
    {"id": "14", "name": "Fresh Milk", "category": "dairy", "price": 3.49, "image_url": "https://images.unsplash.com/photo-1563636619-e9143da7973b?w=300", "description": "Fresh whole milk, 1 liter", "owner_uploaded": False, "stock": 90},
    {"id": "15", "name": "Greek Yogurt", "category": "dairy", "price": 4.99, "image_url": "https://images.unsplash.com/photo-1488477181946-6428a0291777?w=300", "description": "Creamy Greek yogurt, 500g", "owner_uploaded": False, "stock": 40},
    {"id": "16", "name": "Cheddar Cheese", "category": "dairy", "price": 6.99, "image_url": "https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d?w=300", "description": "Aged cheddar cheese block", "owner_uploaded": False, "stock": 25},
    
    # Grains & Cereals
    {"id": "17", "name": "Basmati Rice", "category": "grains", "price": 7.99, "image_url": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=300", "description": "Premium basmati rice, 2kg pack", "owner_uploaded": False, "stock": 100},
    {"id": "18", "name": "Whole Wheat Flour", "category": "grains", "price": 4.49, "image_url": "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=300", "description": "Organic whole wheat flour, 1kg", "owner_uploaded": False, "stock": 75},
    {"id": "19", "name": "Rolled Oats", "category": "grains", "price": 3.99, "image_url": "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=300", "description": "Premium rolled oats for breakfast", "owner_uploaded": False, "stock": 65},
    
    # Bakery
    {"id": "20", "name": "Whole Wheat Bread", "category": "bakery", "price": 2.99, "image_url": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=300", "description": "Fresh baked whole wheat bread", "owner_uploaded": False, "stock": 20},
    {"id": "21", "name": "Croissants", "category": "bakery", "price": 5.99, "image_url": "https://images.unsplash.com/photo-1555507036-ab1f4038808a?w=300", "description": "Buttery French croissants, pack of 6", "owner_uploaded": False, "stock": 15},
    
    # Spices & Herbs
    {"id": "22", "name": "Turmeric Powder", "category": "spices", "price": 2.49, "image_url": "https://images.unsplash.com/photo-1599909713857-b6a0e5d36b20?w=300", "description": "Pure turmeric powder, 100g", "owner_uploaded": False, "stock": 50},
    {"id": "23", "name": "Cumin Seeds", "category": "spices", "price": 3.29, "image_url": "https://images.unsplash.com/photo-1599909713857-b6a0e5d36b20?w=300", "description": "Whole cumin seeds, aromatic", "owner_uploaded": False, "stock": 45},
    {"id": "24", "name": "Fresh Basil", "category": "spices", "price": 1.99, "image_url": "https://images.unsplash.com/photo-1618375569909-0b8a69d3eb5c?w=300", "description": "Fresh basil leaves", "owner_uploaded": False, "stock": 30},
]

CATEGORIES = ["fruits", "vegetables", "pulses", "dairy", "grains", "bakery", "spices", "beverages", "snacks", "meat"]

# Data stores
users_store = {}
customer_users = {}
owner_sessions = {}
customer_sessions = {}
uploaded_products = []

class CustomerRegister(BaseModel):
    name: str
    email: str
    password: str
    phone: str

class CustomerLogin(BaseModel):
    email: str
    password: str

class OwnerKeyRequest(BaseModel):
    phone_number: str

class OwnerLoginRequest(BaseModel):
    phone_number: str
    security_key: str

class UserModel(BaseModel):
    name: str
    email: str
    is_owner: bool = False

class ProductUpload(BaseModel):
    name: str
    category: str
    price: float
    description: str
    image_data: str  # base64 encoded

def generate_security_key(phone_number: str) -> str:
    """Generate a unique security key based on phone number and timestamp"""
    # Create a hash based on phone number + secret + current day
    current_day = datetime.now().strftime("%Y-%m-%d")
    raw_data = f"{phone_number}_{SECRET_KEY}_{current_day}"
    
    # Generate SHA256 hash and take first 12 characters
    hash_object = hashlib.sha256(raw_data.encode())
    security_key = hash_object.hexdigest()[:12].upper()
    
    return security_key

def verify_owner_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify if the request is from an authenticated owner"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        phone_number = payload.get("phone_number")
        
        if phone_number not in AUTHORIZED_OWNER_PHONES:
            raise HTTPException(status_code=403, detail="Access denied: Not an authorized owner")
        
        return {"phone_number": phone_number, "is_owner": True}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/categories")
async def get_categories():
    return {"categories": CATEGORIES}

@app.get("/api/products")
async def get_products(search: Optional[str] = None, category: Optional[str] = None):
    products = SAMPLE_PRODUCTS.copy()
    
    if search:
        products = [p for p in products if search.lower() in p["name"].lower()]
    
    if category:
        products = [p for p in products if p["category"] == category]
    
    return {"products": products}

@app.get("/api/products/{product_id}")
async def get_product(product_id: str):
    product = next((p for p in SAMPLE_PRODUCTS if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# Customer Authentication Endpoints
@app.post("/api/customer/register")
async def customer_register(customer: CustomerRegister):
    """Register new customer"""
    # Check if email already exists
    for user_data in customer_users.values():
        if user_data["email"] == customer.email:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new customer
    customer_id = f"customer_{len(customer_users) + 1}"
    customer_users[customer_id] = {
        "id": customer_id,
        "name": customer.name,
        "email": customer.email,
        "password": hashlib.sha256(customer.password.encode()).hexdigest(),  # Hash password
        "phone": customer.phone,
        "created_at": datetime.now().isoformat()
    }
    
    return {
        "message": "Customer registered successfully",
        "customer_id": customer_id
    }

@app.post("/api/customer/login")
async def customer_login(login_data: CustomerLogin):
    """Customer login"""
    hashed_password = hashlib.sha256(login_data.password.encode()).hexdigest()
    
    # Find customer by email and password
    customer = None
    for user_data in customer_users.values():
        if user_data["email"] == login_data.email and user_data["password"] == hashed_password:
            customer = user_data
            break
    
    if not customer:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Generate JWT token
    token_data = {
        "customer_id": customer["id"],
        "email": customer["email"],
        "is_customer": True,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    
    # Store session
    customer_sessions[customer["id"]] = {
        "token": token,
        "login_time": datetime.now().isoformat()
    }
    
    return {
        "message": "Login successful",
        "token": token,
        "customer": {
            "id": customer["id"],
            "name": customer["name"],
            "email": customer["email"]
        }
    }

def verify_customer_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify customer token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        customer_id = payload.get("customer_id")
        
        if not customer_id or customer_id not in customer_users:
            raise HTTPException(status_code=401, detail="Invalid customer token")
        
        return customer_users[customer_id]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/api/customer/profile")
async def get_customer_profile(customer: dict = Depends(verify_customer_token)):
    """Get customer profile"""
    return {
        "customer": {
            "id": customer["id"],
            "name": customer["name"],
            "email": customer["email"],
            "phone": customer["phone"]
        }
    }

# Shopping Cart Endpoints
class CartItem(BaseModel):
    product_id: str
    quantity: int

customer_carts = {}

@app.post("/api/customer/cart/add")
async def add_to_cart(item: CartItem, customer: dict = Depends(verify_customer_token)):
    """Add item to customer cart"""
    customer_id = customer["id"]
    
    # Find product
    product = next((p for p in SAMPLE_PRODUCTS if p["id"] == item.product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check stock
    if item.quantity > product["stock"]:
        raise HTTPException(status_code=400, detail=f"Only {product['stock']} items available in stock")
    
    # Initialize cart if doesn't exist
    if customer_id not in customer_carts:
        customer_carts[customer_id] = []
    
    # Check if item already in cart
    existing_item = next((cart_item for cart_item in customer_carts[customer_id] if cart_item["product_id"] == item.product_id), None)
    
    if existing_item:
        # Update quantity
        new_quantity = existing_item["quantity"] + item.quantity
        if new_quantity > product["stock"]:
            raise HTTPException(status_code=400, detail=f"Cannot add more items. Only {product['stock']} available, you already have {existing_item['quantity']} in cart")
        existing_item["quantity"] = new_quantity
    else:
        # Add new item
        customer_carts[customer_id].append({
            "product_id": item.product_id,
            "quantity": item.quantity,
            "added_at": datetime.now().isoformat()
        })
    
    return {"message": "Item added to cart successfully"}

@app.get("/api/customer/cart")
async def get_cart(customer: dict = Depends(verify_customer_token)):
    """Get customer cart with product details"""
    customer_id = customer["id"]
    
    if customer_id not in customer_carts:
        return {"cart": [], "total": 0}
    
    cart_with_details = []
    total = 0
    
    for cart_item in customer_carts[customer_id]:
        product = next((p for p in SAMPLE_PRODUCTS if p["id"] == cart_item["product_id"]), None)
        if product:
            item_total = product["price"] * cart_item["quantity"]
            total += item_total
            
            cart_with_details.append({
                "product_id": cart_item["product_id"],
                "product_name": product["name"],
                "product_price": product["price"],
                "product_image": product["image_url"],
                "quantity": cart_item["quantity"],
                "item_total": item_total
            })
    
    return {
        "cart": cart_with_details,
        "total": round(total, 2),
        "items_count": len(cart_with_details)
    }

@app.delete("/api/customer/cart/{product_id}")
async def remove_from_cart(product_id: str, customer: dict = Depends(verify_customer_token)):
    """Remove item from cart"""
    customer_id = customer["id"]
    
    if customer_id not in customer_carts:
        raise HTTPException(status_code=404, detail="Cart is empty")
    
    customer_carts[customer_id] = [item for item in customer_carts[customer_id] if item["product_id"] != product_id]
    
    return {"message": "Item removed from cart"}

@app.put("/api/customer/cart/{product_id}")
async def update_cart_quantity(product_id: str, item: CartItem, customer: dict = Depends(verify_customer_token)):
    """Update item quantity in cart"""
    customer_id = customer["id"]
    
    if customer_id not in customer_carts:
        raise HTTPException(status_code=404, detail="Cart is empty")
    
    # Find product to check stock
    product = next((p for p in SAMPLE_PRODUCTS if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if item.quantity > product["stock"]:
        raise HTTPException(status_code=400, detail=f"Only {product['stock']} items available")
    
    # Update cart item
    cart_item = next((item for item in customer_carts[customer_id] if item["product_id"] == product_id), None)
    if cart_item:
        cart_item["quantity"] = item.quantity
        return {"message": "Cart updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Item not found in cart")

# Owner Authentication Endpoints
@app.post("/api/owner/generate-key")
async def generate_owner_key(request: OwnerKeyRequest):
    """Generate security key for authorized owner phone numbers"""
    phone_number = request.phone_number.strip()
    
    # Check if phone number is authorized
    if phone_number not in AUTHORIZED_OWNER_PHONES:
        raise HTTPException(
            status_code=403, 
            detail="Access denied: This phone number is not authorized for owner access"
        )
    
    # Generate security key
    security_key = generate_security_key(phone_number)
    
    return {
        "message": "Security key generated successfully",
        "security_key": security_key,
        "phone_number": phone_number,
        "valid_until": "End of day (keys refresh daily)"
    }

@app.post("/api/owner/login")
async def owner_login(request: OwnerLoginRequest):
    """Login as owner using phone number and security key"""
    phone_number = request.phone_number.strip()
    provided_key = request.security_key.strip().upper()
    
    # Check if phone number is authorized
    if phone_number not in AUTHORIZED_OWNER_PHONES:
        raise HTTPException(status_code=403, detail="Access denied: Not an authorized owner")
    
    # Verify security key
    expected_key = generate_security_key(phone_number)
    if provided_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid security key")
    
    # Generate JWT token
    token_data = {
        "phone_number": phone_number,
        "is_owner": True,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    
    # Store session
    owner_sessions[phone_number] = {
        "token": token,
        "login_time": datetime.now().isoformat()
    }
    
    return {
        "message": "Owner login successful",
        "token": token,
        "phone_number": phone_number,
        "is_owner": True
    }

@app.get("/api/owner/verify")
async def verify_owner_status(owner_data: dict = Depends(verify_owner_token)):
    """Verify current owner status"""
    return {
        "is_owner": True,
        "phone_number": owner_data["phone_number"],
        "message": "Owner access verified"
    }

@app.post("/api/owner/upload-grocery-image")
async def upload_grocery_image(product: ProductUpload, owner_data: dict = Depends(verify_owner_token)):
    """Upload grocery image (owner only)"""
    
    # Create new product
    new_product = {
        "id": f"owner_{len(uploaded_products) + 1}",
        "name": product.name,
        "category": product.category,
        "price": product.price,
        "description": product.description,
        "image_url": product.image_data,  # base64 data URL
        "owner_uploaded": True,
        "uploaded_by": owner_data["phone_number"]
    }
    
    uploaded_products.append(new_product)
    SAMPLE_PRODUCTS.append(new_product)
    
    return {"message": "Product uploaded successfully", "product_id": new_product["id"]}

@app.get("/api/owner/products")
async def get_owner_products(owner_data: dict = Depends(verify_owner_token)):
    """Get products uploaded by current owner"""
    owner_products = [p for p in uploaded_products if p.get("uploaded_by") == owner_data["phone_number"]]
    return {"products": owner_products}

@app.delete("/api/owner/products/{product_id}")
async def delete_owner_product(product_id: str, owner_data: dict = Depends(verify_owner_token)):
    """Delete owner's product"""
    global uploaded_products, SAMPLE_PRODUCTS
    
    # Find product
    product = next((p for p in uploaded_products if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check ownership
    if product.get("uploaded_by") != owner_data["phone_number"]:
        raise HTTPException(status_code=403, detail="You can only delete your own products")
    
    # Remove from both lists
    uploaded_products = [p for p in uploaded_products if p["id"] != product_id]
    SAMPLE_PRODUCTS[:] = [p for p in SAMPLE_PRODUCTS if p["id"] != product_id]
    
    return {"message": "Product deleted successfully"}

# Regular user endpoints (for customers)
@app.post("/api/users")
async def create_user(user: UserModel):
    user_id = f"user_{len(users_store) + 1}"
    users_store[user_id] = user.dict()
    users_store[user_id]["id"] = user_id
    return {"user_id": user_id, "message": "User created successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)