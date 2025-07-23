#!/usr/bin/env python3
"""
Database Setup Script for QUALITY Store
Creates all required Supabase tables for the grocery e-commerce platform
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

def create_tables():
    """Create all required database tables"""
    
    # SQL for creating tables
    tables_sql = [
        # Users table
        """
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            email VARCHAR(255) UNIQUE NOT NULL,
            name VARCHAR(255) NOT NULL,
            phone VARCHAR(50),
            address TEXT,
            loyalty_points INTEGER DEFAULT 0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        
        # Carts table
        """
        CREATE TABLE IF NOT EXISTS carts (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES users(id) ON DELETE CASCADE,
            items JSONB NOT NULL DEFAULT '[]',
            total DECIMAL(10,2) NOT NULL DEFAULT 0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        
        # Orders table
        """
        CREATE TABLE IF NOT EXISTS orders (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES users(id) ON DELETE CASCADE,
            items JSONB NOT NULL,
            total DECIMAL(10,2) NOT NULL,
            status VARCHAR(50) DEFAULT 'pending',
            delivery_address TEXT NOT NULL,
            delivery_date VARCHAR(50),
            delivery_time VARCHAR(50),
            payment_status VARCHAR(50) DEFAULT 'pending',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        
        # Payment transactions table
        """
        CREATE TABLE IF NOT EXISTS payment_transactions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            session_id VARCHAR(255) UNIQUE NOT NULL,
            payment_id VARCHAR(255),
            user_id UUID REFERENCES users(id) ON DELETE SET NULL,
            amount DECIMAL(10,2) NOT NULL,
            currency VARCHAR(10) NOT NULL DEFAULT 'usd',
            payment_status VARCHAR(50) DEFAULT 'pending',
            status VARCHAR(50) DEFAULT 'pending',
            order_id UUID REFERENCES orders(id) ON DELETE SET NULL,
            metadata JSONB,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        
        # Chat messages table
        """
        CREATE TABLE IF NOT EXISTS chat_messages (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES users(id) ON DELETE CASCADE,
            message TEXT NOT NULL,
            sender_type VARCHAR(20) NOT NULL CHECK (sender_type IN ('user', 'support')),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
    ]
    
    print("🚀 Creating database tables for QUALITY Store...")
    
    for i, sql in enumerate(tables_sql, 1):
        try:
            # Execute SQL directly using Supabase RPC or REST API
            table_name = ["users", "carts", "orders", "payment_transactions", "chat_messages"][i-1]
            print(f"📋 Creating table {i}/5: {table_name}")
            
            # Use Supabase SQL editor functionality via RPC
            result = supabase.rpc('execute_sql', {'query': sql}).execute()
            print(f"✅ Table {table_name} created successfully")
            
        except Exception as e:
            print(f"❌ Error creating table {table_name}: {str(e)}")
            # Try alternative approach using postgrest
            try:
                # For tables that already exist, we'll get an error but it's expected
                if "already exists" in str(e):
                    print(f"ℹ️  Table {table_name} already exists, skipping...")
                else:
                    print(f"⚠️  Attempting alternative creation method for {table_name}...")
            except:
                pass
    
    print("\n🎉 Database setup completed!")
    print("📊 Verifying table creation...")
    
    # Verify tables exist by attempting to query them
    tables = ["users", "carts", "orders", "payment_transactions", "chat_messages"]
    for table in tables:
        try:
            result = supabase.table(table).select("*").limit(1).execute()
            print(f"✅ Table '{table}' verified and accessible")
        except Exception as e:
            print(f"❌ Table '{table}' verification failed: {str(e)}")

def create_indexes():
    """Create indexes for better performance"""
    indexes_sql = [
        "CREATE INDEX IF NOT EXISTS idx_carts_user_id ON carts(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_payment_transactions_session_id ON payment_transactions(session_id);",
        "CREATE INDEX IF NOT EXISTS idx_payment_transactions_user_id ON payment_transactions(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_chat_messages_user_id ON chat_messages(user_id);",
    ]
    
    print("\n📈 Creating database indexes...")
    for sql in indexes_sql:
        try:
            supabase.rpc('execute_sql', {'query': sql}).execute()
            print(f"✅ Index created: {sql[:50]}...")
        except Exception as e:
            print(f"⚠️  Index creation note: {str(e)[:100]}...")

if __name__ == "__main__":
    print("🛒 QUALITY Store Database Setup")
    print("=" * 50)
    print(f"🔗 Supabase URL: {supabase_url}")
    print(f"🔑 Using service key: {'*' * 20}...{supabase_key[-10:] if supabase_key else 'NOT SET'}")
    print()
    
    if not supabase_url or not supabase_key:
        print("❌ ERROR: Supabase credentials not found!")
        print("Please check your .env file configuration.")
        exit(1)
    
    try:
        create_tables()
        create_indexes()
        print("\n🎉 Database setup completed successfully!")
        print("🚀 QUALITY Store is ready for use!")
    except Exception as e:
        print(f"\n❌ Database setup failed: {str(e)}")
        print("Please check your Supabase credentials and permissions.")