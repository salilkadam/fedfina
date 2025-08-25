#!/usr/bin/env python3
"""
Generate Test Conversation Data
This script creates sample conversation data in the database for testing the conversations API.
"""

import asyncio
import psycopg2
import os
from datetime import datetime, timedelta
import uuid

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://user:password@localhost:5432/fedfina_db')

def create_test_conversations():
    """Create test conversation data in the database"""
    
    # Test account IDs
    test_accounts = [
        "Salil",
        "11212", 
        "test123",
        "demo-account",
        "sample_user"
    ]
    
    # Sample conversation IDs
    sample_conversation_ids = [
        "conv_0801k299y9g1eesa8jmdsvj5pfsc",
        "conv_1234567890abcdef1234567890abcdef",
        "conv_abcdef1234567890abcdef1234567890",
        "conv_test1234567890abcdef1234567890ab",
        "conv_demo1234567890abcdef1234567890ab"
    ]
    
    # Sample email IDs
    sample_emails = [
        "salil.kadam@bionicaisolutions.com",
        "test@example.com",
        "demo@fedfina.com",
        "user@test.com",
        "admin@sample.com"
    ]
    
    try:
        # Connect to database
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        print("🗄️ Connected to database successfully")
        
        # Check if conversation_runs table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'conversation_runs'
            );
        """)
        
        if not cursor.fetchone()[0]:
            print("❌ conversation_runs table does not exist. Creating it...")
            
            # Create conversation_runs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversation_runs (
                    id SERIAL PRIMARY KEY,
                    account_id VARCHAR(255) NOT NULL,
                    email_id VARCHAR(255) NOT NULL,
                    conversation_id VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW(),
                    transcript_url TEXT,
                    audio_url TEXT,
                    report_url TEXT
                )
            """)
            
            # Create index on account_id
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversation_runs_account_id 
                ON conversation_runs(account_id)
            """)
            
            conn.commit()
            print("✅ conversation_runs table created successfully")
        
        # Clear existing test data
        cursor.execute("DELETE FROM conversation_runs WHERE account_id IN %s", 
                      (tuple(test_accounts),))
        print(f"🧹 Cleared existing test data for accounts: {test_accounts}")
        
        # Generate test conversations
        test_conversations = []
        for i, account_id in enumerate(test_accounts):
            # Create 2-3 conversations per account
            num_conversations = (i % 3) + 2
            
            for j in range(num_conversations):
                conversation_id = sample_conversation_ids[(i + j) % len(sample_conversation_ids)]
                email_id = sample_emails[(i + j) % len(sample_emails)]
                
                # Create timestamp with some variation
                timestamp = datetime.now() - timedelta(days=i*2 + j, hours=j*3)
                
                # Generate sample URLs
                transcript_url = f"https://minio.example.com/transcripts/{account_id}/{conversation_id}.txt"
                audio_url = f"https://minio.example.com/audio/{account_id}/{conversation_id}.mp3"
                report_url = f"https://minio.example.com/reports/{account_id}/{conversation_id}.pdf"
                
                test_conversations.append({
                    'account_id': account_id,
                    'email_id': email_id,
                    'conversation_id': conversation_id,
                    'created_at': timestamp,
                    'transcript_url': transcript_url,
                    'audio_url': audio_url,
                    'report_url': report_url
                })
        
        # Insert test data
        for conv in test_conversations:
            cursor.execute("""
                INSERT INTO conversation_runs 
                (account_id, email_id, conversation_id, created_at, transcript_url, audio_url, report_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                conv['account_id'],
                conv['email_id'],
                conv['conversation_id'],
                conv['created_at'],
                conv['transcript_url'],
                conv['audio_url'],
                conv['report_url']
            ))
        
        conn.commit()
        print(f"✅ Inserted {len(test_conversations)} test conversations")
        
        # Verify the data
        for account_id in test_accounts:
            cursor.execute("""
                SELECT COUNT(*) FROM conversation_runs WHERE account_id = %s
            """, (account_id,))
            count = cursor.fetchone()[0]
            print(f"   📊 Account '{account_id}': {count} conversations")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Test data generation completed successfully!")
        print("You can now test the API with:")
        for account_id in test_accounts:
            print(f"   curl 'https://fedfina.bionicaisolutions.com/api/v1/conversations/{account_id}'")
        
    except Exception as e:
        print(f"❌ Error generating test data: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    print("🚀 Generating test conversation data...")
    create_test_conversations()
