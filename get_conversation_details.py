#!/usr/bin/env python3
"""
Script to get conversation details by Conversation ID and extract audio/PDF links
"""

import asyncio
import sys
import os
import psycopg2
from datetime import datetime

# Mock settings class for database connection
class MockSettings:
    def __init__(self):
        # Use the production database URL
        self.database_url = "postgresql://fedfina:fedfinaTh1515T0p53cr3t@pg-rw.postgres.svc.cluster.local:5432/fedfina"

# Mock database service for getting conversation details
class MockDatabaseService:
    def __init__(self, settings):
        self.settings = settings
        self.connection_string = settings.database_url

    def _get_connection(self):
        """Get database connection"""
        return psycopg2.connect(self.connection_string)

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

async def get_conversation_details():
    """Get conversation details for the specified conversation IDs"""

    print("🎵 Getting Conversation Details and File Links")
    print("=" * 60)

    # Conversation IDs to process
    conversation_ids = [
        "conv_0801k3qmfm8dfpkbc150hgm646cd",
        "conv_2801k3qjantmfxksxyfk0m4yb9hc",
        "conv_3901k3jj16zze9jsgjejfeffgccg",
        "conv_7801k3jhwrt2edzaj78nt6xtk9mw",
        "conv_9301k3gdewf0fa9bc05e44y53kw2",
        "conv_7301k3gd9q3xftc9g6bkdx8z6054"
    ]

    try:
        # Initialize database service
        settings = MockSettings()
        db_service = MockDatabaseService(settings)

        print(f"Processing {len(conversation_ids)} conversation IDs...")
        print()

        # Process each conversation ID
        for i, conv_id in enumerate(conversation_ids, 1):
            print(f"🔍 [{i}/{len(conversation_ids)}] Processing: {conv_id}")

            conversation = await db_service.get_conversation_by_id(conv_id)

            if conversation:
                print(f"   ✅ Found conversation details:")
                print(f"      Account ID: {conversation['account_id']}")
                print(f"      Email: {conversation['email_id']}")
                print(f"      Created: {conversation['created_at']}")

                # Extract and display file links
                audio_url = conversation.get('audio_url')
                report_url = conversation.get('report_url')

                print("      📁 Files:")
                if audio_url:
                    print(f"         🎵 Audio: {audio_url}")
                else:
                    print("         🎵 Audio: Not available")

                if report_url:
                    print(f"         📄 PDF Report: {report_url}")
                else:
                    print("         📄 PDF Report: Not available")
            else:
                print("   ❌ Conversation not found in database")
                print("      📁 Files: None available")
            print()

        print("✅ Processing completed!")

    except Exception as e:
        print(f"❌ Script failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(get_conversation_details())
