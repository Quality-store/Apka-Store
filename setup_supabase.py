#!/usr/bin/env python3
"""
Create Supabase database tables for QUALITY Store
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from backend directory
load_dotenv("/app/backend/.env")

# Supabase client initialization
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")

try:
    supabase: Client = create_client(supabase_url, supabase_key)
    print("✅ Supabase client created successfully")
    
    # Create tables using SQL
    tables_sql = [
        # Users table
        """
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY,
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
            id UUID PRIMARY KEY,
            user_id UUID NOT NULL,
            items JSONB NOT NULL DEFAULT '[]',
            total DECIMAL(10,2) NOT NULL DEFAULT 0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        
        # Orders table
        """
        CREATE TABLE IF NOT EXISTS orders (
            id UUID PRIMARY KEY,
            user_id UUID NOT NULL,
            items JSONB NOT NULL,
            total DECIMAL(10,2) NOT NULL,
            status VARCHAR(50) DEFAULT 'pending',
            delivery_address TEXT NOT NULL,
            delivery_date VARCHAR(50) NOT NULL,
            delivery_time VARCHAR(50) NOT NULL,
            payment_status VARCHAR(50) DEFAULT 'pending',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        
        # Payment transactions table
        """
        CREATE TABLE IF NOT EXISTS payment_transactions (
            id UUID PRIMARY KEY,
            session_id VARCHAR(255) NOT NULL,
            payment_id VARCHAR(255),
            user_id UUID,
            amount DECIMAL(10,2) NOT NULL,
            currency VARCHAR(10) NOT NULL,
            payment_status VARCHAR(50) DEFAULT 'pending',
            order_id UUID,
            metadata JSONB,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        
        # Chat messages table
        """
        CREATE TABLE IF NOT EXISTS chat_messages (
            id UUID PRIMARY KEY,
            user_id UUID NOT NULL,
            message TEXT NOT NULL,
            sender_type VARCHAR(20) NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
    ]
    
    for i, sql in enumerate(tables_sql):
        try:
            result = supabase.rpc('exec_sql', {'sql': sql}).execute()
            print(f"✅ Table {i+1} created successfully")
        except Exception as e:
            print(f"❌ Error creating table {i+1}: {str(e)}")
            # Try alternative method using direct SQL execution
            try:
                # Use the SQL editor approach
                print(f"Trying alternative method for table {i+1}...")
                # This might not work directly, but let's see
            except Exception as e2:
                print(f"❌ Alternative method also failed: {str(e2)}")
    
    print("\n🔍 Checking if tables were created...")
    tables_to_check = ["users", "carts", "orders", "payment_transactions", "chat_messages"]
    for table in tables_to_check:
        try:
            result = supabase.table(table).select("*").limit(1).execute()
            print(f"✅ {table} table exists and is accessible")
        except Exception as e:
            print(f"❌ {table} table still not accessible: {str(e)}")
            
except Exception as e:
    print(f"❌ Failed to create Supabase client: {str(e)}")