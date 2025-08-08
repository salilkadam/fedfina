"""
Text Formatter Service for transcript processing and formatting
"""
import logging
import re
from typing import Dict, Any, List, Optional
from config import Settings

logger = logging.getLogger(__name__)


class TextFormatterService:
    """Service for text formatting and transcript processing"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
    
    def format_transcript(self, raw_transcript: str) -> str:
        """
        Format raw transcript into clean, readable text
        
        Args:
            raw_transcript: Raw transcript from ElevenLabs API
            
        Returns:
            Formatted transcript text
        """
        try:
            # Clean up the transcript
            formatted = self._clean_transcript(raw_transcript)
            
            # Ensure proper line breaks
            formatted = self._normalize_line_breaks(formatted)
            
            # Remove excessive whitespace
            formatted = self._remove_excess_whitespace(formatted)
            
            return formatted
            
        except Exception as e:
            logger.error(f"Error formatting transcript: {e}")
            return raw_transcript
    
    def _clean_transcript(self, transcript: str) -> str:
        """
        Clean up transcript text
        
        Args:
            transcript: Raw transcript text
            
        Returns:
            Cleaned transcript text
        """
        # Remove any HTML tags if present
        transcript = re.sub(r'<[^>]+>', '', transcript)
        
        # Remove any special characters that might cause issues
        transcript = re.sub(r'[^\w\s\.\,\!\?\:\;\-\(\)]', '', transcript)
        
        # Normalize quotes
        transcript = transcript.replace('"', '"').replace('"', '"')
        transcript = transcript.replace(''', "'").replace(''', "'")
        
        return transcript
    
    def _normalize_line_breaks(self, transcript: str) -> str:
        """
        Normalize line breaks in transcript
        
        Args:
            transcript: Transcript text
            
        Returns:
            Transcript with normalized line breaks
        """
        # Replace multiple line breaks with single ones
        transcript = re.sub(r'\n\s*\n', '\n', transcript)
        
        # Ensure proper spacing after speaker labels
        transcript = re.sub(r'(AI:|User:)\s*', r'\1 ', transcript)
        
        # Add line breaks between different speakers
        transcript = re.sub(r'(AI:.*?)(User:)', r'\1\n\2', transcript, flags=re.DOTALL)
        transcript = re.sub(r'(User:.*?)(AI:)', r'\1\n\2', transcript, flags=re.DOTALL)
        
        return transcript
    
    def _remove_excess_whitespace(self, transcript: str) -> str:
        """
        Remove excess whitespace from transcript
        
        Args:
            transcript: Transcript text
            
        Returns:
            Transcript with normalized whitespace
        """
        # Remove leading/trailing whitespace
        transcript = transcript.strip()
        
        # Normalize multiple spaces to single space
        transcript = re.sub(r' +', ' ', transcript)
        
        # Remove empty lines
        lines = transcript.split('\n')
        lines = [line.strip() for line in lines if line.strip()]
        
        return '\n'.join(lines)
    
    def extract_conversation_summary(self, transcript: str) -> Dict[str, Any]:
        """
        Extract basic conversation summary information
        
        Args:
            transcript: Formatted transcript text
            
        Returns:
            Dict containing summary information
        """
        try:
            lines = transcript.split('\n')
            
            # Count messages by speaker
            ai_messages = 0
            user_messages = 0
            total_words = 0
            
            for line in lines:
                if line.startswith('AI:'):
                    ai_messages += 1
                    total_words += len(line.replace('AI:', '').strip().split())
                elif line.startswith('User:'):
                    user_messages += 1
                    total_words += len(line.replace('User:', '').strip().split())
            
            # Calculate average message length
            total_messages = ai_messages + user_messages
            avg_message_length = total_words / total_messages if total_messages > 0 else 0
            
            return {
                "total_messages": total_messages,
                "ai_messages": ai_messages,
                "user_messages": user_messages,
                "total_words": total_words,
                "avg_message_length": round(avg_message_length, 1),
                "conversation_length": len(transcript)
            }
            
        except Exception as e:
            logger.error(f"Error extracting conversation summary: {e}")
            return {
                "total_messages": 0,
                "ai_messages": 0,
                "user_messages": 0,
                "total_words": 0,
                "avg_message_length": 0,
                "conversation_length": 0
            }
    
    def validate_transcript(self, transcript: str) -> Dict[str, Any]:
        """
        Validate transcript format and content
        
        Args:
            transcript: Transcript text to validate
            
        Returns:
            Dict containing validation result
        """
        try:
            errors = []
            warnings = []
            
            # Check if transcript is empty
            if not transcript.strip():
                errors.append("Transcript is empty")
                return {
                    "valid": False,
                    "errors": errors,
                    "warnings": warnings
                }
            
            # Check for speaker labels
            if not re.search(r'AI:|User:', transcript):
                errors.append("No speaker labels found (AI: or User:)")
            
            # Check for minimum content
            if len(transcript.strip()) < 10:
                warnings.append("Transcript seems very short")
            
            # Check for excessive line breaks
            if transcript.count('\n') > len(transcript.split()) * 0.5:
                warnings.append("Transcript has many line breaks")
            
            # Check for repeated content
            lines = transcript.split('\n')
            if len(lines) > 1:
                unique_lines = set(lines)
                if len(unique_lines) < len(lines) * 0.5:
                    warnings.append("Transcript has repeated content")
            
            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings
            }
            
        except Exception as e:
            logger.error(f"Error validating transcript: {e}")
            return {
                "valid": False,
                "errors": [f"Validation error: {str(e)}"],
                "warnings": []
            }
    
    def format_for_openai(self, transcript: str) -> str:
        """
        Format transcript specifically for OpenAI processing
        
        Args:
            transcript: Formatted transcript text
            
        Returns:
            Transcript formatted for OpenAI
        """
        try:
            # Ensure transcript is properly formatted
            formatted = self.format_transcript(transcript)
            
            # Add context for OpenAI
            formatted = f"Conversation Transcript:\n\n{formatted}\n\nPlease provide a comprehensive summary of this conversation."
            
            return formatted
            
        except Exception as e:
            logger.error(f"Error formatting transcript for OpenAI: {e}")
            return transcript
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check text formatter service health
        
        Returns:
            Health status dictionary
        """
        try:
            # Test basic formatting functionality
            test_transcript = "AI: Hello\nUser: Hi there\nAI: How are you?"
            formatted = self.format_transcript(test_transcript)
            
            if formatted and "AI:" in formatted and "User:" in formatted:
                return {
                    "status": "healthy",
                    "message": "Text formatter service working correctly"
                }
            else:
                return {
                    "status": "unhealthy",
                    "message": "Text formatter test failed"
                }
                
        except Exception as e:
            logger.error(f"Text formatter health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"Text formatter error: {str(e)}"
            }
