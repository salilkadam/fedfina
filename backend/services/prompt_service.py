"""
Prompt Service for managing prompt templates
"""
import logging
import os
from typing import Dict, Any, Optional, List
from pathlib import Path
from config import Settings

logger = logging.getLogger(__name__)


class PromptService:
    """Service for managing prompt templates"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.prompts_directory = Path("prompts")
        self.default_prompt_file = "summarization.txt"

    async def load_prompt_template(self, prompt_file: str = None) -> Dict[str, Any]:
        """
        Load a prompt template from file
        
        Args:
            prompt_file: Name of the prompt file (default: summarization.txt)
            
        Returns:
            Dict containing the loaded prompt template
        """
        try:
            if prompt_file is None:
                prompt_file = self.default_prompt_file
            
            # Construct the full path to the prompt file
            prompt_path = self.prompts_directory / prompt_file
            
            if not prompt_path.exists():
                return {
                    "status": "error",
                    "error": f"Prompt file not found: {prompt_file}"
                }
            
            # Read the prompt template
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompt_template = f.read()
            
            return {
                "status": "success",
                "prompt_template": prompt_template,
                "file_name": prompt_file,
                "file_size": len(prompt_template)
            }
            
        except Exception as e:
            logger.error(f"Error loading prompt template: {e}")
            return {
                "status": "error",
                "error": f"Failed to load prompt template: {str(e)}"
            }

    async def list_available_prompts(self) -> Dict[str, Any]:
        """
        List all available prompt templates
        
        Returns:
            Dict containing list of available prompts
        """
        try:
            if not self.prompts_directory.exists():
                return {
                    "status": "error",
                    "error": f"Prompts directory not found: {self.prompts_directory}"
                }
            
            prompt_files = []
            for file_path in self.prompts_directory.glob("*.txt"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    prompt_files.append({
                        "file_name": file_path.name,
                        "file_size": len(content),
                        "has_transcript_placeholder": "{transcript}" in content
                    })
                except Exception as e:
                    logger.warning(f"Could not read prompt file {file_path}: {e}")
                    prompt_files.append({
                        "file_name": file_path.name,
                        "file_size": 0,
                        "has_transcript_placeholder": False,
                        "error": str(e)
                    })
            
            return {
                "status": "success",
                "prompts": prompt_files,
                "total_prompts": len(prompt_files)
            }
            
        except Exception as e:
            logger.error(f"Error listing prompts: {e}")
            return {
                "status": "error",
                "error": f"Failed to list prompts: {str(e)}"
            }

    async def validate_prompt_template(self, prompt_template: str) -> Dict[str, Any]:
        """
        Validate a prompt template
        
        Args:
            prompt_template: The prompt template to validate
            
        Returns:
            Dict containing validation result
        """
        try:
            validation_errors = []
            validation_warnings = []
            
            # Check for required placeholders
            if "{transcript}" not in prompt_template:
                validation_errors.append("Missing required placeholder: {transcript}")
            
            # Check template length
            if len(prompt_template) < 100:
                validation_warnings.append("Prompt template seems very short")
            
            if len(prompt_template) > 5000:
                validation_warnings.append("Prompt template is quite long")
            
            # Check for common issues
            if "INSTRUCTIONS:" not in prompt_template and "FORMAT:" not in prompt_template:
                validation_warnings.append("No clear instructions or format specified")
            
            # Check for potential issues
            if prompt_template.count("{transcript}") > 1:
                validation_warnings.append("Multiple {transcript} placeholders found")
            
            return {
                "status": "success",
                "valid": len(validation_errors) == 0,
                "errors": validation_errors,
                "warnings": validation_warnings,
                "template_length": len(prompt_template)
            }
            
        except Exception as e:
            logger.error(f"Error validating prompt template: {e}")
            return {
                "status": "error",
                "error": f"Validation failed: {str(e)}",
                "valid": False
            }

    async def create_prompt_template(self, file_name: str, content: str) -> Dict[str, Any]:
        """
        Create a new prompt template file
        
        Args:
            file_name: Name of the prompt file
            content: Content of the prompt template
            
        Returns:
            Dict containing creation result
        """
        try:
            # Ensure the prompts directory exists
            self.prompts_directory.mkdir(exist_ok=True)
            
            # Validate the file name
            if not file_name.endswith('.txt'):
                file_name += '.txt'
            
            # Check if file already exists
            prompt_path = self.prompts_directory / file_name
            if prompt_path.exists():
                return {
                    "status": "error",
                    "error": f"Prompt file already exists: {file_name}"
                }
            
            # Validate the content
            validation_result = await self.validate_prompt_template(content)
            if not validation_result.get("valid", False):
                return {
                    "status": "error",
                    "error": "Invalid prompt template",
                    "validation_errors": validation_result.get("errors", [])
                }
            
            # Write the prompt template
            with open(prompt_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "status": "success",
                "message": f"Prompt template created: {file_name}",
                "file_name": file_name,
                "file_size": len(content)
            }
            
        except Exception as e:
            logger.error(f"Error creating prompt template: {e}")
            return {
                "status": "error",
                "error": f"Failed to create prompt template: {str(e)}"
            }

    async def health_check(self) -> Dict[str, Any]:
        """
        Check prompt service health
        
        Returns:
            Health status dictionary
        """
        try:
            # Check if prompts directory exists
            if not self.prompts_directory.exists():
                return {
                    "status": "unhealthy",
                    "message": f"Prompts directory not found: {self.prompts_directory}"
                }
            
            # Check if default prompt exists
            default_prompt_path = self.prompts_directory / self.default_prompt_file
            if not default_prompt_path.exists():
                return {
                    "status": "unhealthy",
                    "message": f"Default prompt file not found: {self.default_prompt_file}"
                }
            
            # Try to load the default prompt
            load_result = await self.load_prompt_template()
            if load_result.get("status") != "success":
                return {
                    "status": "unhealthy",
                    "message": f"Failed to load default prompt: {load_result.get('error')}"
                }
            
            # Validate the default prompt
            validation_result = await self.validate_prompt_template(load_result["prompt_template"])
            if not validation_result.get("valid", False):
                return {
                    "status": "warning",
                    "message": f"Default prompt has validation issues: {validation_result.get('errors')}"
                }
            
            return {
                "status": "healthy",
                "message": f"Prompt service working correctly ({self.default_prompt_file} loaded and validated)"
            }
            
        except Exception as e:
            logger.error(f"Prompt service health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"Prompt service error: {str(e)}"
            }
