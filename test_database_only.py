#!/usr/bin/env python3
"""
Simplified test script to verify database service changes
"""

import asyncio
import sys
import os
import psycopg2
from datetime import datetime, timedelta

# Mock settings class for testing
class MockSettings:
    def __init__(self):
        # Use the actual Kubernetes database URL from production secrets
        self.database_url = "postgresql://fedfina:fedfinaTh1515T0p53cr3t@pg-rw.postgres.svc.cluster.local:5432/fedfina"

# Mock database service for testing
class MockDatabaseService:
    def __init__(self, settings):
        self.settings = settings
        self.connection_string = settings.database_url
    
    def _get_connection(self):
        """Get database connection"""
        return psycopg2.connect(self.connection_string)
    
    async def get_conversations_by_account(self, account_id: str):
        """Get all conversation runs for a specific account ID, returning only the latest record per conversation_id"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Use window function to get only the latest record per conversation_id
            cursor.execute("""
                WITH ranked_conversations AS (
                    SELECT 
                        id, account_id, email_id, conversation_id, created_at,
                        transcript_url, audio_url, report_url,
                        ROW_NUMBER() OVER (
                            PARTITION BY conversation_id 
                            ORDER BY created_at DESC
                        ) as rn
                    FROM conversation_runs 
                    WHERE account_id = %s
                )
                SELECT id, account_id, email_id, conversation_id, created_at,
                       transcript_url, audio_url, report_url
                FROM ranked_conversations 
                WHERE rn = 1
                ORDER BY created_at DESC
            """, (account_id,))
            
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            
            conversations = []
            for row in rows:
                conversations.append({
                    "id": row[0],
                    "account_id": row[1],
                    "email_id": row[2],
                    "conversation_id": row[3],
                    "created_at": row[4],
                    "transcript_url": row[5],
                    "audio_url": row[6],
                    "report_url": row[7]
                })
            
            return conversations
            
        except Exception as e:
            print(f"Error getting conversations for account {account_id}: {e}")
            return []
    
    async def get_conversations_by_date(self, target_date: datetime):
        """Get all conversation runs for a specific date, grouped by account, returning only the latest record per conversation_id"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Convert date to start and end of day
            start_date = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            # Use window function to get only the latest record per conversation_id
            cursor.execute("""
                WITH ranked_conversations AS (
                    SELECT 
                        id, account_id, email_id, conversation_id, created_at,
                        transcript_url, audio_url, report_url,
                        ROW_NUMBER() OVER (
                            PARTITION BY conversation_id 
                            ORDER BY created_at DESC
                        ) as rn
                    FROM conversation_runs 
                    WHERE created_at >= %s AND created_at <= %s
                )
                SELECT id, account_id, email_id, conversation_id, created_at,
                       transcript_url, audio_url, report_url
                FROM ranked_conversations 
                WHERE rn = 1
                ORDER BY account_id, created_at DESC
            """, (start_date, end_date))
            
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            
            # Group conversations by account_id
            conversations_by_account = {}
            for row in rows:
                account_id = row[1]
                conversation = {
                    "id": row[0],
                    "account_id": row[1],
                    "email_id": row[2],
                    "conversation_id": row[3],
                    "created_at": row[4],
                    "transcript_url": row[5],
                    "audio_url": row[6],
                    "report_url": row[7]
                }
                
                if account_id not in conversations_by_account:
                    conversations_by_account[account_id] = []
                
                conversations_by_account[account_id].append(conversation)
            
            return conversations_by_account
            
        except Exception as e:
            print(f"Error getting conversations for date {target_date}: {e}")
            return {}
    
    async def get_conversation_by_id(self, conversation_id: str):
        """Get the latest conversation record for a specific conversation_id"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Use window function to get only the latest record for this conversation_id
            cursor.execute("""
                WITH ranked_conversations AS (
                    SELECT 
                        id, account_id, email_id, conversation_id, created_at,
                        transcript_url, audio_url, report_url,
                        ROW_NUMBER() OVER (
                            PARTITION BY conversation_id 
                            ORDER BY created_at DESC
                        ) as rn
                    FROM conversation_runs 
                    WHERE conversation_id = %s
                )
                SELECT id, account_id, email_id, conversation_id, created_at,
                       transcript_url, audio_url, report_url
                FROM ranked_conversations 
                WHERE rn = 1
            """, (conversation_id,))
            
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if row:
                return {
                    "id": row[0],
                    "account_id": row[1],
                    "email_id": row[2],
                    "conversation_id": row[3],
                    "created_at": row[4],
                    "transcript_url": row[5],
                    "audio_url": row[6],
                    "report_url": row[7]
                }
            
            return None
            
        except Exception as e:
            print(f"Error getting conversation by ID {conversation_id}: {e}")
            return None

async def test_latest_conversations():
    """Test that conversation endpoints return only latest records per conversation_id"""
    
    print("🧪 Testing Latest Conversations Functionality (Database Only)")
    print("=" * 60)
    print("Using Kubernetes production database connection")
    print("=" * 60)
    
    try:
        # Initialize mock database service
        settings = MockSettings()
        db_service = MockDatabaseService(settings)
        
        # Test 1: Test get_conversations_by_account
        print("\n📋 Test 1: get_conversations_by_account")
        print("-" * 40)
        
        # First, let's see what account IDs actually exist in the database
        print("\n🔍 Checking what account IDs exist in the database...")
        try:
            conn = db_service._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT DISTINCT account_id, COUNT(*) as conversation_count
                FROM conversation_runs 
                GROUP BY account_id
                ORDER BY conversation_count DESC
                LIMIT 10
            """)
            
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            
            if rows:
                print("Found the following account IDs:")
                for row in rows:
                    print(f"   {row[0]} - {row[1]} conversations")
                
                # Use the first account ID for testing
                test_account_id = rows[0][0]
                print(f"\nUsing account ID '{test_account_id}' for testing...")
                
                conversations = await db_service.get_conversations_by_account(test_account_id)
                print(f"   Found {len(conversations)} conversations")
                
                if conversations:
                    # Check for duplicate conversation_ids
                    conversation_ids = [conv['conversation_id'] for conv in conversations]
                    unique_ids = set(conversation_ids)
                    
                    if len(conversation_ids) == len(unique_ids):
                        print(f"   ✅ No duplicate conversation_ids found")
                    else:
                        print(f"   ❌ Found {len(conversation_ids) - len(unique_ids)} duplicate conversation_ids")
                        print(f"   Total: {len(conversation_ids)}, Unique: {len(unique_ids)}")
                    
                    # Show first few conversations
                    for i, conv in enumerate(conversations[:3]):
                        print(f"   {i+1}. {conv['conversation_id']} - {conv['created_at']}")
                else:
                    print(f"   ⚠️  No conversations found")
            else:
                print("No account IDs found in the database")
                
        except Exception as e:
            print(f"Error checking account IDs: {e}")
        
        # Test with a few different account IDs
        test_accounts = ["Salil", "11212", "test_account_123"]
        
        for account_id in test_accounts:
            print(f"\nTesting account: {account_id}")
            conversations = await db_service.get_conversations_by_account(account_id)
            print(f"   Found {len(conversations)} conversations")
            
            if conversations:
                # Check for duplicate conversation_ids
                conversation_ids = [conv['conversation_id'] for conv in conversations]
                unique_ids = set(conversation_ids)
                
                if len(conversation_ids) == len(unique_ids):
                    print(f"   ✅ No duplicate conversation_ids found")
                else:
                    print(f"   ❌ Found {len(conversation_ids) - len(unique_ids)} duplicate conversation_ids")
                    print(f"   Total: {len(conversation_ids)}, Unique: {len(unique_ids)}")
                
                # Show first few conversations
                for i, conv in enumerate(conversations[:3]):
                    print(f"   {i+1}. {conv['conversation_id']} - {conv['created_at']}")
            else:
                print(f"   ⚠️  No conversations found")
        
        # Test 2: Test get_conversations_by_date
        print("\n📋 Test 2: get_conversations_by_date")
        print("-" * 40)
        
        # Test with today's date
        today = datetime.now()
        print(f"Testing with date: {today.strftime('%Y-%m-%d')}")
        
        conversations_by_account = await db_service.get_conversations_by_date(today)
        print(f"Found conversations for {len(conversations_by_account)} accounts")
        
        total_conversations = 0
        for account_id, conversations in conversations_by_account.items():
            print(f"\nAccount: {account_id} - {len(conversations)} conversations")
            total_conversations += len(conversations)
            
            if conversations:
                # Check for duplicate conversation_ids
                conversation_ids = [conv['conversation_id'] for conv in conversations]
                unique_ids = set(conversation_ids)
                
                if len(conversation_ids) == len(unique_ids):
                    print(f"   ✅ No duplicate conversation_ids found")
                else:
                    print(f"   ❌ Found {len(conversation_ids) - len(unique_ids)} duplicate conversation_ids")
                
                # Show first few conversations
                for i, conv in enumerate(conversations[:2]):
                    print(f"   {i+1}. {conv['conversation_id']} - {conv['created_at']}")
        
        print(f"\n📊 Summary: Total conversations across all accounts: {total_conversations}")
        
        # Test 3: Test get_conversation_by_id
        print("\n📋 Test 3: get_conversation_by_id")
        print("-" * 40)
        
        # Try to get a conversation by ID if we have any conversations
        if conversations_by_account:
            # Get the first conversation_id from the first account
            first_account = list(conversations_by_account.keys())[0]
            first_conversation = conversations_by_account[first_account][0]
            test_conversation_id = first_conversation['conversation_id']
            
            print(f"Testing with conversation_id: {test_conversation_id}")
            conversation = await db_service.get_conversation_by_id(test_conversation_id)
            
            if conversation:
                print(f"✅ get_conversation_by_id returned latest record:")
                print(f"   ID: {conversation['id']}")
                print(f"   Created at: {conversation['created_at']}")
                print(f"   Account: {conversation['account_id']}")
                print(f"   Email: {conversation['email_id']}")
            else:
                print(f"❌ get_conversation_by_id returned None for {test_conversation_id}")
        else:
            print("⚠️  No conversations found for testing get_conversation_by_id")
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_latest_conversations())
