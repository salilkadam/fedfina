"""
Callback Service for External API Notifications

This module handles sending callback notifications to external systems
after conversation processing is completed.
"""

import os
import logging
import httpx
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class CallbackService:
    """Service for sending callback notifications to external systems"""
    
    def __init__(self, settings):
        """
        Initialize the callback service
        
        Args:
            settings: Application settings containing callback configuration
        """
        self.settings = settings
        self.callback_enabled = settings.callback_enabled
        self.callback_url = settings.callback_url
        self.timeout = settings.callback_timeout_seconds
        
        if self.callback_enabled:
            logger.info(f"✅ Callback service enabled. URL: {self.callback_url}")
        else:
            logger.info("⏸️ Callback service disabled")
    
    async def send_processing_callback(
        self,
        status: str,
        applicant_id: str,
        email_id: str,
        description: str,
        artifacts: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Send callback notification to external system
        
        Args:
            status: Processing status ("success" or "failed")
            applicant_id: The applicant/account ID
            email_id: The email address
            description: Description of the processing result
            artifacts: Dictionary containing file URLs (transcript_url, audio_url, pdf_url)
            
        Returns:
            Dictionary with callback result
        """
        # Check if callbacks are enabled
        if not self.callback_enabled:
            logger.info("⏸️ Callback disabled, skipping notification")
            return {
                "status": "skipped",
                "message": "Callback service is disabled",
                "error_type": "disabled"
            }
        
        try:
            logger.info(f"🔄 Sending callback to {self.callback_url}")
            logger.info(f"📋 Callback timeout: {self.timeout} seconds")
            
            # Prepare callback payload
            payload = {
                "status": status,
                "applicant_id": applicant_id,
                "email_id": email_id,
                "description": description,
                "artifacts": {
                    "transcript_url": artifacts.get("transcript_url", ""),
                    "audio_url": artifacts.get("audio_url", ""),
                    "pdf_url": artifacts.get("pdf_url", "")
                }
            }
            
            logger.info(f"📤 Callback payload: {payload}")
            
            # Send callback request
            logger.info(f"🌐 Making HTTP request to: {self.callback_url}")
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info("📡 Sending POST request...")
                response = await client.post(
                    self.callback_url,
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "User-Agent": "FedFina-PostProcess/1.0"
                    }
                )
                
                logger.info(f"📥 Received response: {response.status_code}")
                response.raise_for_status()
                
                logger.info(f"✅ Callback sent successfully. Status: {response.status_code}")
                
                return {
                    "status": "success",
                    "message": "Callback sent successfully",
                    "response_status": response.status_code,
                    "response_data": response.json() if response.content else None
                }
                
        except httpx.TimeoutException:
            error_msg = f"Callback request timed out after {self.timeout} seconds"
            logger.error(f"⏰ {error_msg}")
            return {
                "status": "error",
                "message": error_msg,
                "error_type": "timeout"
            }
            
        except httpx.HTTPStatusError as e:
            error_msg = f"Callback request failed with status {e.response.status_code}: {e.response.text}"
            logger.error(f"❌ {error_msg}")
            return {
                "status": "error",
                "message": error_msg,
                "error_type": "http_error",
                "response_status": e.response.status_code
            }
            
        except Exception as e:
            error_msg = f"Callback request failed: {str(e)}"
            logger.error(f"💥 {error_msg}")
            return {
                "status": "error",
                "message": error_msg,
                "error_type": "exception"
            }
    
    async def send_success_callback(
        self,
        applicant_id: str,
        email_id: str,
        artifacts: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Send success callback notification
        
        Args:
            applicant_id: The applicant/account ID
            email_id: The email address
            artifacts: Dictionary containing file URLs
            
        Returns:
            Dictionary with callback result
        """
        return await self.send_processing_callback(
            status="success",
            applicant_id=applicant_id,
            email_id=email_id,
            description="Process completed successfully",
            artifacts=artifacts
        )
    
    async def send_failure_callback(
        self,
        applicant_id: str,
        email_id: str,
        error_description: str,
        artifacts: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Send failure callback notification
        
        Args:
            applicant_id: The applicant/account ID
            email_id: The email address
            error_description: Description of the failure
            artifacts: Optional dictionary containing any available file URLs
            
        Returns:
            Dictionary with callback result
        """
        if artifacts is None:
            artifacts = {}
            
        return await self.send_processing_callback(
            status="failed",
            applicant_id=applicant_id,
            email_id=email_id,
            description=error_description,
            artifacts=artifacts
        )
