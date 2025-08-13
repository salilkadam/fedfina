"""
ElevenLabs Service for conversation and audio file retrieval
"""
import httpx
import logging
from typing import Dict, Any, Optional
from config import Settings

logger = logging.getLogger(__name__)


class ElevenLabsService:
    """Service for interacting with ElevenLabs API"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.base_url = settings.elevenlabs_base_url
        self.api_key = settings.elevenlabs_api_key
        self.headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
    
    async def get_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """
        Retrieve conversation details from ElevenLabs API
        
        Args:
            conversation_id: The ElevenLabs conversation ID
            
        Returns:
            Dict containing conversation details including transcript and audio URL
        """
        try:
            async with httpx.AsyncClient() as client:
                # Get conversation details using the correct endpoint
                conversation_url = f"{self.base_url}/convai/conversations/{conversation_id}"
                response = await client.get(conversation_url, headers=self.headers)
                response.raise_for_status()
                
                conversation_data = response.json()
                
                # Extract transcript and audio information
                transcript = self._extract_transcript(conversation_data)
                audio_url = self._extract_audio_url(conversation_data)
                
                return {
                    "conversation_id": conversation_id,
                    "transcript": transcript,
                    "audio_url": audio_url,
                    "conversation_data": conversation_data,
                    "status": "success"
                }
                
        except httpx.HTTPStatusError as e:
            logger.error(f"ElevenLabs API error for conversation {conversation_id}: {e}")
            return {
                "conversation_id": conversation_id,
                "error": f"API error: {e.response.status_code}",
                "status": "error"
            }
        except Exception as e:
            logger.error(f"Unexpected error retrieving conversation {conversation_id}: {e}")
            return {
                "conversation_id": conversation_id,
                "error": f"Unexpected error: {str(e)}",
                "status": "error"
            }
    
    def _extract_transcript(self, conversation_data: Dict[str, Any]) -> str:
        """
        Extract plain text transcript from conversation data
        
        Args:
            conversation_data: Raw conversation data from ElevenLabs API
            
        Returns:
            Plain text transcript in format "AI: message\nUser: message"
        """
        try:
            # Extract transcript from the conversation data
            transcript_messages = conversation_data.get("transcript", [])
            
            transcript_lines = []
            for message in transcript_messages:
                role = message.get("role", "unknown")
                content = message.get("message", "")
                
                if role.lower() == "agent":
                    transcript_lines.append(f"AI: {content}")
                elif role.lower() == "user":
                    transcript_lines.append(f"User: {content}")
                else:
                    transcript_lines.append(f"{role.title()}: {content}")
            
            return "\n".join(transcript_lines)
            
        except Exception as e:
            logger.error(f"Error extracting transcript: {e}")
            return f"Error extracting transcript: {str(e)}"
    
    def _extract_audio_url(self, conversation_data: Dict[str, Any]) -> Optional[str]:
        """
        Extract audio file URL from conversation data
        
        Args:
            conversation_data: Raw conversation data from ElevenLabs API
            
        Returns:
            Audio file URL or None if not found
        """
        try:
            # Check if audio is available
            has_audio = conversation_data.get("has_audio", False)
            logger.info(f"Audio availability check: has_audio={has_audio}")
            
            if not has_audio:
                logger.info("No audio available for this conversation")
                return None
            
            # Construct the audio download URL
            conversation_id = conversation_data.get("conversation_id")
            if conversation_id:
                audio_url = f"{self.base_url}/convai/conversations/{conversation_id}/audio"
                logger.info(f"Generated audio URL: {audio_url}")
                return audio_url
            
            logger.warning("No conversation_id found in conversation data")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting audio URL: {e}")
            return None
    
    async def download_audio(self, audio_url: str) -> Optional[bytes]:
        """
        Download audio file from ElevenLabs
        
        Args:
            audio_url: URL of the audio file to download
            
        Returns:
            Audio file bytes or None if download failed
        """
        try:
            logger.info(f"Attempting to download audio from: {audio_url}")
            async with httpx.AsyncClient() as client:
                response = await client.get(audio_url, headers=self.headers)
                response.raise_for_status()
                logger.info(f"Successfully downloaded audio, size: {len(response.content)} bytes")
                return response.content
                
        except Exception as e:
            logger.error(f"Error downloading audio from {audio_url}: {e}")
            return None
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check ElevenLabs API health
        
        Returns:
            Health status dictionary
        """
        try:
            async with httpx.AsyncClient() as client:
                # Test with a simple API call
                response = await client.get(
                    f"{self.base_url}/voices",
                    headers=self.headers
                )
                response.raise_for_status()
                
                return {
                    "status": "healthy",
                    "message": "ElevenLabs API responding correctly"
                }
                
        except Exception as e:
            logger.error(f"ElevenLabs health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"ElevenLabs API error: {str(e)}"
            }
