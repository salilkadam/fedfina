#!/usr/bin/env python3
"""
Test script to verify OpenAI service functionality
"""
import os
import asyncio
from dotenv import load_dotenv
from services.openai_service import OpenAIService, TranscriptMessage

# Load environment variables
load_dotenv()

async def test_openai_service():
    """Test OpenAI service with a sample conversation"""
    try:
        # Initialize service
        service = OpenAIService()
        print("✅ OpenAI service initialized")
        
        # Create sample transcript
        transcript = [
            TranscriptMessage(
                timestamp="2025-07-31T22:40:00Z",
                speaker="interviewer",
                content="Hello, I am conducting a business loan assessment. Can you tell me about your business?",
                messageId="msg1"
            ),
            TranscriptMessage(
                timestamp="2025-07-31T22:40:05Z",
                speaker="applicant",
                content="Hello, I run a tourism company with 5 vehicles. We started with 1 vehicle and have grown over 20 years.",
                messageId="msg2"
            ),
            TranscriptMessage(
                timestamp="2025-07-31T22:40:10Z",
                speaker="interviewer",
                content="What are your monthly operating expenses?",
                messageId="msg3"
            ),
            TranscriptMessage(
                timestamp="2025-07-31T22:40:15Z",
                speaker="spouse",
                content="We pay 50,000 rupees for driver salaries and 20,000 for marketing staff.",
                messageId="msg4"
            )
        ]
        
        print("✅ Sample transcript created")
        
        # Test analysis
        print("🔄 Testing conversation analysis...")
        summary = await service.analyze_conversation(
            transcript=transcript,
            account_id="test_acc",
            email_id="test@example.com"
        )
        
        print("✅ Analysis completed successfully!")
        print(f"Topic: {summary.topic}")
        print(f"Sentiment: {summary.sentiment}")
        print(f"Intent: {summary.intent}")
        print(f"Summary: {summary.summary[:100]}...")
        
        if summary.key_factors:
            print(f"Key Factors: {len(summary.key_factors)} categories")
            for factor in summary.key_factors:
                print(f"  - {factor.category}: {len(factor.points)} points")
        
        if summary.risk_factors:
            print(f"Risk Factors: {len(summary.risk_factors)} identified")
            for risk in summary.risk_factors:
                print(f"  - {risk.risk_type} ({risk.severity}): {risk.description}")
        
        if summary.third_party_intervention and summary.third_party_intervention.detected:
            print(f"Third Party Intervention: {len(summary.third_party_intervention.speakers)} speakers detected")
        
        return True
        
    except Exception as e:
        print(f"❌ OpenAI service test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_openai_service())
    if success:
        print("\n🎉 OpenAI service is working correctly!")
    else:
        print("\n💥 OpenAI service test failed!") 