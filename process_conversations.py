#!/usr/bin/env python3
"""
Script to process multiple ElevenLabs conversation IDs via the Postprocess API
"""

import os
import json
import requests
import time
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# API Configuration
API_BASE_URL = "https://fedfina.bionicaisolutions.com/api/v1"
API_KEY = "development-secret-key-change-in-production"
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# Conversation IDs to process
CONVERSATION_IDS = [
    "conv_0801k3qmfm8dfpkbc150hgm646cd",
    "conv_2801k3qjantmfxksxyfk0m4yb9hc",
    "conv_3901k3jj16zze9jsgjejfeffgccg",
    "conv_7801k3jhwrt2edzaj78nt6xtk9mw",
    "conv_9301k3gdewf0fa9bc05e44y53kw2",
    "conv_7301k3gd9q3xftc9g6bkdx8z6054",
    "conv_9501k22nwhfpeyh8vkz521d80zwh",
    "conv_5401k22qazxmeejvn3zfd6g2x7y4"
]

class ConversationProcessor:
    """Handles processing of ElevenLabs conversations"""

    def __init__(self, output_dir: str = "Output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def process_conversation(self, conversation_id: str, email_id: str = "test@example.com", account_id: str = "test_account") -> Dict[str, Any]:
        """
        Process a single conversation via the API

        Args:
            conversation_id: The ElevenLabs conversation ID
            email_id: Email address for reports
            account_id: Account identifier

        Returns:
            API response data
        """
        url = f"{API_BASE_URL}/postprocess/conversation"
        payload = {
            "conversation_id": conversation_id,
            "email_id": email_id,
            "account_id": account_id,
            "send_email": True  # Enable email sending with new Postfix relay
        }

        print(f"🚀 Processing conversation: {conversation_id}")

        try:
            response = self.session.post(url, json=payload, timeout=300)  # 5 minute timeout
            response.raise_for_status()

            data = response.json()
            print(f"✅ Successfully processed {conversation_id}")
            return data

        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to process {conversation_id}: {e}")
            return {"error": str(e), "conversation_id": conversation_id}

    def download_file(self, url: str, filepath: Path) -> bool:
        """
        Download a file from a URL to the specified filepath

        Args:
            url: The download URL
            filepath: Path to save the file

        Returns:
            True if successful, False otherwise
        """
        try:
            response = self.session.get(url, timeout=60)
            response.raise_for_status()

            filepath.parent.mkdir(parents=True, exist_ok=True)

            with open(filepath, 'wb') as f:
                f.write(response.content)

            print(f"📥 Downloaded: {filepath.name}")
            return True

        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to download {url}: {e}")
            return False

    def get_secure_download_urls(self, account_id: str) -> Dict[str, Dict[str, str]]:
        """
        Get secure download URLs for all conversations in an account

        Args:
            account_id: The account ID to get conversations for

        Returns:
            Dictionary mapping conversation_id to file URLs
        """
        url = f"{API_BASE_URL}/conversations/{account_id}"

        try:
            response = self.session.get(url, timeout=60)
            response.raise_for_status()

            data = response.json()
            if data.get("status") == "success":
                conversations = data.get("conversations", [])
                url_map = {}

                for conv in conversations:
                    conv_id = conv.get("conversation_id")
                    if conv_id:
                        url_map[conv_id] = {
                            "transcript_url": conv.get("transcript_url"),
                            "audio_url": conv.get("audio_url"),
                            "report_url": conv.get("report_url")
                        }

                print(f"✅ Retrieved secure download URLs for {len(url_map)} conversations")
                return url_map
            else:
                print(f"❌ Failed to get conversations: {data}")
                return {}

        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to get secure download URLs: {e}")
            return {}

    def process_all_conversations(self, conversation_ids: List[str], account_id: str = "test_account") -> List[Dict[str, Any]]:
        """
        Process all conversation IDs and download their artifacts using secure URLs

        Args:
            conversation_ids: List of conversation IDs to process
            account_id: Account ID to use for getting secure URLs

        Returns:
            List of processing results
        """
        results = []

        # First, process all conversations via postprocess API
        print("🚀 Step 1: Processing conversations via Postprocess API")
        for i, conversation_id in enumerate(conversation_ids, 1):
            print(f"\n{'='*60}")
            print(f"Processing {i}/{len(conversation_ids)}: {conversation_id}")
            print(f"{'='*60}")

            # Create subfolder for this conversation
            conv_dir = self.output_dir / conversation_id
            conv_dir.mkdir(exist_ok=True)

            # Process the conversation
            result = self.process_conversation(conversation_id)

            if "error" not in result:
                # Save the API response
                response_file = conv_dir / "api_response.json"
                with open(response_file, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"✅ API response saved for {conversation_id}")

            results.append(result)

            # Add a small delay between requests to be respectful to the API
            if i < len(conversation_ids):
                print("⏳ Waiting 2 seconds before next request...")
                time.sleep(2)

        # Second, get secure download URLs
        print("\n🚀 Step 2: Getting secure download URLs from Conversations API")
        secure_urls = self.get_secure_download_urls(account_id)

        # Third, download files using secure URLs
        print("\n🚀 Step 3: Downloading files using secure URLs")
        successful_downloads = 0
        total_downloads_attempted = 0

        for conversation_id in conversation_ids:
            conv_dir = self.output_dir / conversation_id

            if conversation_id in secure_urls:
                urls = secure_urls[conversation_id]
                print(f"\n📥 Downloading files for {conversation_id}...")

                # Download transcript
                if urls.get("transcript_url"):
                    transcript_path = conv_dir / f"transcript_{conversation_id}.txt"
                    if self.download_file(urls["transcript_url"], transcript_path):
                        successful_downloads += 1
                    total_downloads_attempted += 1

                # Download audio
                if urls.get("audio_url"):
                    audio_path = conv_dir / f"audio_{conversation_id}.mp3"
                    if self.download_file(urls["audio_url"], audio_path):
                        successful_downloads += 1
                    total_downloads_attempted += 1

                # Download PDF report
                if urls.get("report_url"):
                    pdf_path = conv_dir / f"report_{conversation_id}.pdf"
                    if self.download_file(urls["report_url"], pdf_path):
                        successful_downloads += 1
                    total_downloads_attempted += 1
            else:
                print(f"⚠️ No secure URLs found for {conversation_id}")

            # Small delay between conversation downloads
            time.sleep(1)

        print(f"\n📊 Download Summary: {successful_downloads}/{total_downloads_attempted} files downloaded successfully")

        return results

    def generate_summary_report(self, results: List[Dict[str, Any]]) -> None:
        """
        Generate a summary report of all processed conversations

        Args:
            results: List of processing results
        """
        summary_file = self.output_dir / "processing_summary.json"

        summary = {
            "processing_timestamp": datetime.now().isoformat(),
            "total_conversations": len(results),
            "successful": len([r for r in results if "error" not in r]),
            "failed": len([r for r in results if "error" in r]),
            "results": results
        }

        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        print(f"\n{'='*60}")
        print("PROCESSING SUMMARY")
        print(f"{'='*60}")
        print(f"Total conversations: {summary['total_conversations']}")
        print(f"Successful: {summary['successful']}")
        print(f"Failed: {summary['failed']}")
        print(f"Summary saved to: {summary_file}")
        print(f"{'='*60}")


def main():
    """Main execution function"""
    print("🎯 ElevenLabs Conversation Processor")
    print("====================================")

    # Create processor
    processor = ConversationProcessor()

    # Process all conversations with secure download URLs
    results = processor.process_all_conversations(CONVERSATION_IDS, account_id="test_account")

    # Generate summary
    processor.generate_summary_report(results)

    print("\n🎉 Processing complete!")
    print(f"📁 Artifacts saved to: {processor.output_dir.absolute()}")


if __name__ == "__main__":
    main()
