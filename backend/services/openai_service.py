"""
OpenAI Service for conversation summarization
"""
import logging
import openai
from typing import Dict, Any, Optional
from config import Settings

logger = logging.getLogger(__name__)


class OpenAIService:
    """Service for OpenAI API interactions"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.max_tokens = settings.openai_max_tokens
        self.temperature = settings.openai_temperature

    async def summarize_conversation(self, transcript: str, prompt_template: str) -> Dict[str, Any]:
        """
        Summarize conversation using OpenAI API
        
        Args:
            transcript: The conversation transcript to summarize
            prompt_template: The prompt template to use for summarization
            
        Returns:
            Dict containing summarization result
        """
        try:
            # Format the prompt with the transcript
            formatted_prompt = prompt_template.replace("{transcript}", transcript)
            
            # Create the chat completion request
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional financial analyst creating comprehensive summary reports from business loan interview transcripts."
                    },
                    {
                        "role": "user", 
                        "content": formatted_prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            # Extract the summary from the response
            summary = response.choices[0].message.content
            
            # Get usage information
            usage = response.usage
            
            return {
                "status": "success",
                "summary": summary,
                "usage": {
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens
                },
                "model": self.model
            }
            
        except openai.RateLimitError as e:
            logger.error(f"OpenAI rate limit exceeded: {e}")
            return {
                "status": "error",
                "error": f"Rate limit exceeded: {str(e)}",
                "retry_after": getattr(e, 'retry_after', None)
            }
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            return {
                "status": "error",
                "error": f"API error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error in OpenAI summarization: {e}")
            return {
                "status": "error",
                "error": f"Unexpected error: {str(e)}"
            }

    async def test_summarization(self, test_transcript: str) -> Dict[str, Any]:
        """
        Test summarization with a sample transcript
        
        Args:
            test_transcript: Sample transcript for testing
            
        Returns:
            Dict containing test result
        """
        try:
            # Create a simple test prompt
            test_prompt = f"""
            Please provide a brief summary of the following conversation:
            
            {test_transcript}
            
            Summary:
            """
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that summarizes conversations."
                    },
                    {
                        "role": "user",
                        "content": test_prompt
                    }
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            summary = response.choices[0].message.content
            usage = response.usage
            
            return {
                "status": "success",
                "summary": summary,
                "usage": {
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens
                },
                "model": self.model
            }
            
        except Exception as e:
            logger.error(f"OpenAI test failed: {e}")
            return {
                "status": "error",
                "error": f"Test failed: {str(e)}"
            }

    async def validate_prompt_template(self, prompt_template: str) -> Dict[str, Any]:
        """
        Validate that a prompt template is properly formatted
        
        Args:
            prompt_template: The prompt template to validate
            
        Returns:
            Dict containing validation result
        """
        try:
            # Check for required placeholders
            required_placeholders = ["{transcript}"]
            missing_placeholders = []
            
            for placeholder in required_placeholders:
                if placeholder not in prompt_template:
                    missing_placeholders.append(placeholder)
            
            if missing_placeholders:
                return {
                    "status": "error",
                    "error": f"Missing required placeholders: {missing_placeholders}",
                    "valid": False
                }
            
            # Test with a minimal transcript
            test_transcript = "AI: Hello\nUser: Hi\nAI: How are you?\nUser: Good, thank you."
            formatted_prompt = prompt_template.replace("{transcript}", test_transcript)
            
            # Check if the formatted prompt is reasonable length
            if len(formatted_prompt) < 50:
                return {
                    "status": "error",
                    "error": "Prompt template too short after formatting",
                    "valid": False
                }
            
            if len(formatted_prompt) > 10000:
                return {
                    "status": "warning",
                    "message": "Prompt template may be too long for efficient processing",
                    "valid": True
                }
            
            return {
                "status": "success",
                "message": "Prompt template is valid",
                "valid": True,
                "formatted_length": len(formatted_prompt)
            }
            
        except Exception as e:
            logger.error(f"Prompt validation failed: {e}")
            return {
                "status": "error",
                "error": f"Validation failed: {str(e)}",
                "valid": False
            }

    async def health_check(self) -> Dict[str, Any]:
        """
        Check OpenAI API health
        
        Returns:
            Health status dictionary
        """
        try:
            # Test with a simple completion
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": "Hello, this is a health check."
                    }
                ],
                max_tokens=10,
                temperature=0
            )
            
            if response.choices[0].message.content:
                return {
                    "status": "healthy",
                    "message": f"OpenAI API responding correctly (model: {self.model})"
                }
            else:
                return {
                    "status": "unhealthy",
                    "message": "OpenAI API returned empty response"
                }
                
        except Exception as e:
            logger.error(f"OpenAI health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"OpenAI API error: {str(e)}"
            }
