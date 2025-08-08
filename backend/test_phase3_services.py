#!/usr/bin/env python3
"""
Test script for Phase 3 services (OpenAI and Prompt services)
"""
import asyncio
import logging
from config import settings
from services.openai_service import OpenAIService
from services.prompt_service import PromptService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_prompt_service():
    """Test the prompt service functionality"""
    
    print("🔧 Testing Prompt Service...")
    print("=" * 60)
    
    prompt_service = PromptService(settings)
    
    try:
        # Test 1: Health check
        print("🏥 Test 1: Prompt service health check...")
        health_result = await prompt_service.health_check()
        print(f"Health status: {health_result.get('status')}")
        print(f"Message: {health_result.get('message')}")
        
        print("\n" + "=" * 60)
        
        # Test 2: List available prompts
        print("📋 Test 2: List available prompts...")
        list_result = await prompt_service.list_available_prompts()
        if list_result.get('status') == 'success':
            prompts = list_result.get('prompts', [])
            print(f"Found {len(prompts)} prompt templates:")
            for prompt in prompts:
                print(f"  - {prompt.get('file_name')} ({prompt.get('file_size')} chars)")
                if prompt.get('has_transcript_placeholder'):
                    print(f"    ✅ Has transcript placeholder")
                else:
                    print(f"    ❌ Missing transcript placeholder")
        else:
            print(f"❌ Failed to list prompts: {list_result.get('error')}")
        
        print("\n" + "=" * 60)
        
        # Test 3: Load default prompt
        print("📄 Test 3: Load default prompt template...")
        load_result = await prompt_service.load_prompt_template()
        if load_result.get('status') == 'success':
            prompt_template = load_result.get('prompt_template', '')
            print(f"✅ Loaded prompt template: {load_result.get('file_name')}")
            print(f"Template size: {len(prompt_template)} characters")
            print(f"Has transcript placeholder: {'{transcript}' in prompt_template}")
            
            # Test 4: Validate prompt template
            print("\n🔍 Test 4: Validate prompt template...")
            validation_result = await prompt_service.validate_prompt_template(prompt_template)
            print(f"Validation status: {validation_result.get('status')}")
            print(f"Valid: {validation_result.get('valid')}")
            
            if validation_result.get('errors'):
                print("❌ Validation errors:")
                for error in validation_result.get('errors', []):
                    print(f"  - {error}")
            
            if validation_result.get('warnings'):
                print("⚠️ Validation warnings:")
                for warning in validation_result.get('warnings', []):
                    print(f"  - {warning}")
        else:
            print(f"❌ Failed to load prompt template: {load_result.get('error')}")
        
    except Exception as e:
        print(f"❌ Prompt service test failed: {e}")
        logger.error(f"Prompt service test failed: {e}")


async def test_openai_service():
    """Test the OpenAI service functionality"""
    
    print("\n🤖 Testing OpenAI Service...")
    print("=" * 60)
    
    openai_service = OpenAIService(settings)
    
    try:
        # Test 1: Health check
        print("🏥 Test 1: OpenAI service health check...")
        health_result = await openai_service.health_check()
        print(f"Health status: {health_result.get('status')}")
        print(f"Message: {health_result.get('message')}")
        
        print("\n" + "=" * 60)
        
        # Test 2: Test summarization with sample transcript
        print("📝 Test 2: Test summarization with sample transcript...")
        test_transcript = """
        AI: Hello, I'm Neha. I'd like to learn about you and understand your business.
        User: Hello Neha ji, I'm Shardul Kadam and my business is a hotel restaurant in Mumbai.
        AI: Hello Shardul ji, nice to meet you. Running a hotel restaurant in Mumbai is excellent work. How is your day going and how is your business doing?
        User: Well madam, the day is good and business is also good, meaning earning well.
        AI: That's great to hear that your business is doing well. Can you tell me more about your hotel restaurant? Like what you serve, how many years you've been running this business, and how many people work with you?
        """
        
        test_result = await openai_service.test_summarization(test_transcript)
        if test_result.get('status') == 'success':
            print("✅ Test summarization successful")
            print(f"Summary: {test_result.get('summary', '')[:200]}...")
            print(f"Usage: {test_result.get('usage', {})}")
        else:
            print(f"❌ Test summarization failed: {test_result.get('error')}")
        
        print("\n" + "=" * 60)
        
        # Test 3: Validate prompt template
        print("🔍 Test 3: Validate prompt template...")
        test_prompt = "Please summarize this conversation:\n\n{transcript}\n\nSummary:"
        validation_result = await openai_service.validate_prompt_template(test_prompt)
        print(f"Validation status: {validation_result.get('status')}")
        print(f"Valid: {validation_result.get('valid')}")
        
        if validation_result.get('status') == 'success':
            print("✅ Prompt template validation successful")
        else:
            print(f"❌ Prompt template validation failed: {validation_result.get('error')}")
        
    except Exception as e:
        print(f"❌ OpenAI service test failed: {e}")
        logger.error(f"OpenAI service test failed: {e}")


async def test_integration():
    """Test integration between OpenAI and Prompt services"""
    
    print("\n🔗 Testing Service Integration...")
    print("=" * 60)
    
    try:
        prompt_service = PromptService(settings)
        openai_service = OpenAIService(settings)
        
        # Load prompt template
        load_result = await prompt_service.load_prompt_template()
        if load_result.get('status') != 'success':
            print(f"❌ Failed to load prompt template: {load_result.get('error')}")
            return
        
        prompt_template = load_result.get('prompt_template', '')
        
        # Test with sample transcript
        test_transcript = """
        AI: नमस्ते, मैं नेहा हूँ। मैं आपको जानना चाहती हूँ और आपके व्यवसाय को समझना चाहती हूँ।
        User: नमस्ते नेहाजी मैं शारदुल कदम हूँ और मेरा व्योसाय मतलब मैं एक होटिल रेस्टारोंड चलाता हूँ, बंबै में
        AI: नमस्ते शारदुल जी, आपसे मिलकर खुशी हुई। मुंबई में होटल रेस्टोरेंट चलाना बहुत ही बढ़िया काम है। आपका दिन कैसा चल रहा है और आपका व्यवसाय कैसा चल रहा है?
        User: जी मैडम दिन तो बढिया है और व्योसाय भी बढिया ही है, मतलब अक्ह से कमा
        """
        
        print("📝 Testing integration with real transcript...")
        print(f"Transcript length: {len(test_transcript)} characters")
        
        # Test summarization with loaded prompt
        summary_result = await openai_service.summarize_conversation(test_transcript, prompt_template)
        if summary_result.get('status') == 'success':
            print("✅ Integration test successful!")
            print(f"Summary length: {len(summary_result.get('summary', ''))} characters")
            print(f"Usage: {summary_result.get('usage', {})}")
            
            # Show first 300 characters of summary
            summary = summary_result.get('summary', '')
            print(f"Summary preview: {summary[:300]}...")
        else:
            print(f"❌ Integration test failed: {summary_result.get('error')}")
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        logger.error(f"Integration test failed: {e}")


if __name__ == "__main__":
    print("🚀 Starting Phase 3 Services Test")
    print("=" * 60)
    
    # Run the tests
    asyncio.run(test_prompt_service())
    asyncio.run(test_openai_service())
    asyncio.run(test_integration())
    
    print("\n✅ Phase 3 Services Test completed!")
