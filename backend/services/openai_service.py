"""
OpenAI Service for conversation summarization
"""
import logging
import json
import openai
from typing import Dict, Any, Optional
from pydantic import ValidationError
from config import Settings
from models.openai_response_models import OpenAIStructuredResponse

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
            # Check if transcript is too long and truncate if necessary
            max_transcript_length = 100000  # Much higher limit for gpt-4o-mini (128K context)
            if len(transcript) > max_transcript_length:
                logger.warning(f"Transcript too long ({len(transcript)} chars), truncating to {max_transcript_length} chars")
                transcript = transcript[:max_transcript_length] + "\n\n[Transcript truncated due to length]"
            else:
                logger.info(f"Processing transcript of {len(transcript)} characters with {self.model}")
            
            # Format the prompt with the transcript
            formatted_prompt = prompt_template.replace("{transcript}", transcript)
            
            # Create the chat completion request with JSON response format
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional financial analyst creating comprehensive summary reports from business loan interview transcripts. Always respond with valid JSON format. IMPORTANT: If the transcript is in any language other than English, translate ALL content to English before analysis. Provide the entire response in English only."
                    },
                    {
                        "role": "user", 
                        "content": formatted_prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                response_format={"type": "json_object"}
            )
            
            # Extract and parse the JSON response
            raw_response = response.choices[0].message.content
            
            # Parse JSON response with Pydantic
            try:
                # First parse as JSON
                json_data = json.loads(raw_response)
                
                # Then validate with Pydantic model
                structured_response = OpenAIStructuredResponse(**json_data)
                
                summary = raw_response  # Keep raw JSON for backward compatibility
                parsed_summary = structured_response  # Use Pydantic model
                
                logger.info("Successfully parsed and validated OpenAI response with Pydantic")
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                
                # Try to repair the JSON
                logger.info("Attempting to repair truncated JSON response...")
                repaired_json = self._repair_json(raw_response)
                
                if repaired_json:
                    try:
                        json_data = json.loads(repaired_json)
                        structured_response = OpenAIStructuredResponse(**json_data)
                        summary = repaired_json
                        parsed_summary = structured_response
                        logger.info("Successfully repaired and parsed JSON response")
                    except (json.JSONDecodeError, ValidationError) as repair_error:
                        logger.error(f"Failed to parse repaired JSON: {repair_error}")
                        summary = raw_response
                        parsed_summary = None
                else:
                    # Fallback to raw response if JSON repair fails
                    summary = raw_response
                    parsed_summary = None
                
            except ValidationError as e:
                logger.error(f"Failed to validate response with Pydantic: {e}")
                # Try to parse as regular JSON for fallback
                try:
                    summary_json = json.loads(raw_response)
                    summary = raw_response
                    parsed_summary = summary_json  # Use dict as fallback
                except json.JSONDecodeError:
                    summary = raw_response
                    parsed_summary = None
            
            # Get usage information
            usage = response.usage
            
            return {
                "status": "success",
                "summary": summary,
                "parsed_summary": parsed_summary,
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

    def _repair_json(self, json_string: str) -> Optional[str]:
        """
        Attempt to repair truncated or malformed JSON responses
        
        Args:
            json_string: The potentially malformed JSON string
            
        Returns:
            Repaired JSON string or None if repair fails
        """
        try:
            # Clean up the string
            cleaned = json_string.strip()
            
            # Check if it's already valid JSON
            try:
                json.loads(cleaned)
                return cleaned  # Already valid
            except json.JSONDecodeError:
                pass
            
            # Common repair strategies
            
            # 1. Add missing closing braces/brackets
            open_braces = cleaned.count('{')
            close_braces = cleaned.count('}')
            open_brackets = cleaned.count('[')
            close_brackets = cleaned.count(']')
            
            if open_braces > close_braces:
                missing_braces = open_braces - close_braces
                cleaned += '}' * missing_braces
                logger.info(f"Added {missing_braces} missing closing braces")
            
            if open_brackets > close_brackets:
                missing_brackets = open_brackets - close_brackets
                cleaned += ']' * missing_brackets
                logger.info(f"Added {missing_brackets} missing closing brackets")
            
            # 2. Handle unterminated strings
            # Find the last quote and see if it's properly closed
            if cleaned.count('"') % 2 == 1:
                # Odd number of quotes means unterminated string
                cleaned += '"'
                logger.info("Added missing closing quote")
            
            # 3. Remove trailing commas before closing braces/brackets
            import re
            cleaned = re.sub(r',(\s*[}\]])', r'\1', cleaned)
            
            # 4. Handle incomplete JSON objects/arrays at the end
            # If the JSON ends abruptly in the middle of a string or object, try to close it gracefully
            if not cleaned.rstrip().endswith(('}', ']')):
                # Find the last complete JSON structure and truncate there
                last_complete_brace = cleaned.rfind('}')
                last_complete_bracket = cleaned.rfind(']')
                last_complete = max(last_complete_brace, last_complete_bracket)
                
                if last_complete > len(cleaned) * 0.8:  # If we're close to the end
                    cleaned = cleaned[:last_complete + 1]
                    logger.info("Truncated to last complete JSON structure")
            
            # 5. Try to parse the repaired JSON
            json.loads(cleaned)
            return cleaned
            
        except Exception as e:
            logger.error(f"JSON repair failed: {e}")
            return None
