#!/usr/bin/env python3
"""
Direct Database Setup for QUALITY Store
Creates tables using Supabase admin interface simulation
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv("/app/backend/.env")

# Initialize Supabase client
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

def create_tables_directly():
    """Create tables by inserting sample data to trigger table creation"""
    
    print("🚀 Setting up QUALITY Store database...")
    print("📋 Creating tables through direct operations...")
    
    try:
        # Create users table by inserting a sample user
        print("👥 Creating users table...")
        sample_user = {
            "id": "00000000-0000-0000-0000-000000000001",
            "email": "system@qualitystore.com",
            "name": "System User",
            "phone": "+1-000-000-0000",
            "address": "System Address",
            "loyalty_points": 0
        }
        
        # Try to insert - this will create the table structure automatically
        result = supabase.table("users").upsert(sample_user).execute()
        print("✅ Users table created/verified")
        
    except Exception as e:
        print(f"ℹ️  Users table info: {str(e)}")
    
    try:
        # Create carts table 
        print("🛒 Creating carts table...")
        sample_cart = {
            "id": "00000000-0000-0000-0000-000000000001",
            "user_id": "00000000-0000-0000-0000-000000000001",
            "items": [],
            "total": 0.0
        }
        
        result = supabase.table("carts").upsert(sample_cart).execute()
        print("✅ Carts table created/verified")
        
    except Exception as e:
        print(f"ℹ️  Carts table info: {str(e)}")
    
    try:
        # Create orders table
        print("📦 Creating orders table...")
        sample_order = {
            "id": "00000000-0000-0000-0000-000000000001",
            "user_id": "00000000-0000-0000-0000-000000000001",
            "items": [],
            "total": 0.0,
            "status": "pending",
            "delivery_address": "Sample Address",
            "delivery_date": "2024-01-01",
            "delivery_time": "10:00 AM",
            "payment_status": "pending"
        }
        
        result = supabase.table("orders").upsert(sample_order).execute()
        print("✅ Orders table created/verified")
        
    except Exception as e:
        print(f"ℹ️  Orders table info: {str(e)}")
    
    try:
        # Create payment_transactions table
        print("💳 Creating payment_transactions table...")
        sample_payment = {
            "id": "00000000-0000-0000-0000-000000000001",
            "session_id": "cs_test_sample",
            "payment_id": "pi_test_sample",
            "user_id": "00000000-0000-0000-0000-000000000001",
            "amount": 0.0,
            "currency": "usd",
            "payment_status": "pending",
            "order_id": "00000000-0000-0000-0000-000000000001",
            "metadata": {}
        }
        
        result = supabase.table("payment_transactions").upsert(sample_payment).execute()
        print("✅ Payment transactions table created/verified")
        
    except Exception as e:
        print(f"ℹ️  Payment transactions table info: {str(e)}")
    
    try:
        # Create chat_messages table
        print("💬 Creating chat_messages table...")
        sample_message = {
            "id": "00000000-0000-0000-0000-000000000001",
            "user_id": "00000000-0000-0000-0000-000000000001",
            "message": "Welcome to QUALITY Store!",
            "sender_type": "support"
        }
        
        result = supabase.table("chat_messages").upsert(sample_message).execute()
        print("✅ Chat messages table created/verified")
        
    except Exception as e:
        print(f"ℹ️  Chat messages table info: {str(e)}")
    
    # Clean up sample data
    print("\n🧹 Cleaning up sample data...")
    try:
        supabase.table("chat_messages").delete().eq("id", "00000000-0000-0000-0000-000000000001").execute()
        supabase.table("payment_transactions").delete().eq("id", "00000000-0000-0000-0000-000000000001").execute()
        supabase.table("orders").delete().eq("id", "00000000-0000-0000-0000-000000000001").execute()
        supabase.table("carts").delete().eq("id", "00000000-0000-0000-0000-000000000001").execute()
        supabase.table("users").delete().eq("id", "00000000-0000-0000-0000-000000000001").execute()
        print("✅ Sample data cleaned up")
    except Exception as e:
        print(f"ℹ️  Cleanup info: {str(e)}")

def verify_tables():
    """Verify that all tables are accessible"""
    print("\n📊 Verifying table accessibility...")
    
    tables = ["users", "carts", "orders", "payment_transactions", "chat_messages"]
    accessible_tables = []
    
    for table in tables:
        try:
            result = supabase.table(table).select("*").limit(1).execute()
            print(f"✅ Table '{table}' is accessible")
            accessible_tables.append(table)
        except Exception as e:
            print(f"❌ Table '{table}' not accessible: {str(e)}")
    
    return accessible_tables

if __name__ == "__main__":
    print("🛒 QUALITY Store Direct Database Setup")
    print("=" * 50)
    
    if not supabase_url or not supabase_key:
        print("❌ ERROR: Supabase credentials not found!")
        exit(1)
    
    try:
        create_tables_directly()
        accessible = verify_tables()
        
        print(f"\n🎉 Database setup completed!")
        print(f"📊 {len(accessible)}/5 tables are accessible")
        
        if len(accessible) == 5:
            print("🚀 QUALITY Store database is fully ready!")
        else:
            print("⚠️  Some tables may need manual creation in Supabase dashboard")
            print("🔗 Please visit: https://supabase.com/dashboard")
            
    except Exception as e:
        print(f"\n❌ Database setup failed: {str(e)}")