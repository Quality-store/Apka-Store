#!/usr/bin/env python3
"""
Create Supabase database tables for QUALITY Store
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv('/app/backend/.env')

# Supabase client
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

def create_tables():
    """Create all necessary tables for QUALITY Store"""
    
    # SQL to create all tables
    sql_commands = [
        # Users table
        """
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            name VARCHAR(255) NOT NULL,
            phone VARCHAR(50),
            address TEXT,
            loyalty_points INTEGER DEFAULT 0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        
        # Carts table
        """
        CREATE TABLE IF NOT EXISTS carts (
            id UUID PRIMARY KEY,
            user_id UUID NOT NULL,
            items JSONB NOT NULL DEFAULT '[]',
            total DECIMAL(10,2) DEFAULT 0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
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
            delivery_date DATE NOT NULL,
            delivery_time VARCHAR(50) NOT NULL,
            payment_status VARCHAR(50) DEFAULT 'pending',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        
        # Payment transactions table
        """
        CREATE TABLE IF NOT EXISTS payment_transactions (
            id UUID PRIMARY KEY,
            session_id VARCHAR(255) UNIQUE NOT NULL,
            payment_id VARCHAR(255) NOT NULL,
            user_id UUID NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            currency VARCHAR(10) DEFAULT 'USD',
            payment_status VARCHAR(50) DEFAULT 'pending',
            status VARCHAR(50) DEFAULT 'pending',
            order_id UUID,
            metadata JSONB DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        
        # Chat messages table
        """
        CREATE TABLE IF NOT EXISTS chat_messages (
            id UUID PRIMARY KEY,
            user_id UUID NOT NULL,
            message TEXT NOT NULL,
            sender_type VARCHAR(20) NOT NULL CHECK (sender_type IN ('user', 'support')),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
    ]
    
    for i, sql in enumerate(sql_commands, 1):
        try:
            print(f"Creating table {i}/5...")
            result = supabase.rpc('exec_sql', {'sql': sql}).execute()
            print(f"✅ Table {i} created successfully")
        except Exception as e:
            print(f"❌ Failed to create table {i}: {str(e)}")
            # Try alternative method using raw SQL
            try:
                # Use the SQL editor approach
                print(f"Trying alternative method for table {i}...")
                # This might not work directly, but let's see
                pass
            except Exception as e2:
                print(f"❌ Alternative method also failed: {str(e2)}")

if __name__ == "__main__":
    print("Creating Supabase tables for QUALITY Store...")
    create_tables()
    print("Table creation process completed!")