#!/usr/bin/env python3
"""
Test Supabase connection and create tables if needed
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from backend directory
load_dotenv("/app/backend/.env")

# Supabase client initialization
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")

print(f"Supabase URL: {supabase_url}")
print(f"Supabase Key: {supabase_key[:20]}..." if supabase_key else "No key")

try:
    supabase: Client = create_client(supabase_url, supabase_key)
    print("✅ Supabase client created successfully")
    
    # Test connection by trying to list tables
    try:
        # Try to query users table
        result = supabase.table("users").select("*").limit(1).execute()
        print("✅ Users table exists and is accessible")
        print(f"Users table data: {result.data}")
    except Exception as e:
        print(f"❌ Users table error: {str(e)}")
        
    # Try other tables
    tables_to_check = ["carts", "orders", "payment_transactions", "chat_messages"]
    for table in tables_to_check:
        try:
            result = supabase.table(table).select("*").limit(1).execute()
            print(f"✅ {table} table exists and is accessible")
        except Exception as e:
            print(f"❌ {table} table error: {str(e)}")
            
except Exception as e:
    print(f"❌ Failed to create Supabase client: {str(e)}")