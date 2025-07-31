"""
OpenAI Service for processing conversation transcripts
"""
import os
import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class TranscriptMessage(BaseModel):
    timestamp: str
    speaker: str
    content: str
    messageId: str
    metadata: Optional[Dict[str, Any]] = None

class ConversationSummary(BaseModel):
    topic: str
    sentiment: str
    resolution: str
    keywords: Optional[List[str]] = None
    intent: Optional[str] = None
    summary: str
    action_items: Optional[List[str]] = None
    follow_up_required: bool = False

class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", "gpt-4")
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "2000"))
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    
    def format_transcript_for_analysis(self, transcript: List[TranscriptMessage]) -> str:
        """Format transcript messages for OpenAI analysis"""
        formatted_messages = []
        for msg in transcript:
            formatted_messages.append(f"{msg.speaker}: {msg.content}")
        return "\n".join(formatted_messages)
    
    async def analyze_conversation(self, transcript: List[TranscriptMessage], 
                                 account_id: str, email_id: str) -> ConversationSummary:
        """Analyze conversation transcript using OpenAI"""
        try:
            formatted_transcript = self.format_transcript_for_analysis(transcript)
            
            prompt = f"""
            Analyze the following conversation transcript and provide a comprehensive summary.
            
            Account ID: {account_id}
            User Email: {email_id}
            
            Conversation Transcript:
            {formatted_transcript}
            
            Please provide a detailed analysis in the following JSON format:
            {{
                "topic": "Main topic of conversation",
                "sentiment": "Overall sentiment (positive/negative/neutral)",
                "resolution": "How the conversation was resolved",
                "keywords": ["key", "words", "extracted"],
                "intent": "User's primary intent",
                "summary": "Detailed summary of the conversation",
                "action_items": ["action", "items", "if any"],
                "follow_up_required": true/false
            }}
            
            Focus on:
            1. Key points discussed
            2. User's main concerns or questions
            3. Solutions or responses provided
            4. Any follow-up actions needed
            5. Overall satisfaction indicators
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional conversation analyst. Provide accurate, detailed analysis in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                response_format={"type": "json_object"}
            )
            
            # Parse the JSON response
            import json
            analysis_data = json.loads(response.choices[0].message.content)
            
            return ConversationSummary(
                topic=analysis_data.get("topic", "General Discussion"),
                sentiment=analysis_data.get("sentiment", "neutral"),
                resolution=analysis_data.get("resolution", "No specific resolution"),
                keywords=analysis_data.get("keywords", []),
                intent=analysis_data.get("intent", "General inquiry"),
                summary=analysis_data.get("summary", "No summary available"),
                action_items=analysis_data.get("action_items", []),
                follow_up_required=analysis_data.get("follow_up_required", False)
            )
            
        except Exception as e:
            logger.error(f"Error analyzing conversation with OpenAI: {str(e)}")
            # Return a default summary if OpenAI fails
            return ConversationSummary(
                topic="Conversation Analysis",
                sentiment="neutral",
                resolution="Analysis pending",
                keywords=[],
                intent="General inquiry",
                summary="Conversation transcript received. Analysis will be completed shortly.",
                action_items=[],
                follow_up_required=False
            )
    
    async def generate_email_content(self, summary: ConversationSummary, 
                                   account_id: str, email_id: str) -> Dict[str, str]:
        """Generate email content based on conversation summary"""
        try:
            prompt = f"""
            Generate professional email content for a conversation report.
            
            Account ID: {account_id}
            User Email: {email_id}
            
            Conversation Summary:
            - Topic: {summary.topic}
            - Sentiment: {summary.sentiment}
            - Resolution: {summary.resolution}
            - Summary: {summary.summary}
            - Action Items: {', '.join(summary.action_items) if summary.action_items else 'None'}
            - Follow-up Required: {summary.follow_up_required}
            
            Generate:
            1. A professional email subject line
            2. A concise email body (HTML format)
            3. A plain text version of the email body
            
            Return in JSON format:
            {{
                "subject": "Email subject line",
                "html_body": "<html>...</html>",
                "text_body": "Plain text version"
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional email writer. Generate clear, professional email content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.5,
                response_format={"type": "json_object"}
            )
            
            import json
            email_data = json.loads(response.choices[0].message.content)
            
            return {
                "subject": email_data.get("subject", f"Report for Acct: {account_id}"),
                "html_body": email_data.get("html_body", ""),
                "text_body": email_data.get("text_body", "")
            }
            
        except Exception as e:
            logger.error(f"Error generating email content: {str(e)}")
            # Return default email content
            return {
                "subject": f"Report for Acct: {account_id}",
                "html_body": f"""
                <html>
                <body>
                <h2>Conversation Report</h2>
                <p><strong>Account ID:</strong> {account_id}</p>
                <p><strong>Summary:</strong> {summary.summary}</p>
                <p><strong>Topic:</strong> {summary.topic}</p>
                <p><strong>Sentiment:</strong> {summary.sentiment}</p>
                <p><strong>Resolution:</strong> {summary.resolution}</p>
                </body>
                </html>
                """,
                "text_body": f"""
                Conversation Report
                
                Account ID: {account_id}
                Summary: {summary.summary}
                Topic: {summary.topic}
                Sentiment: {summary.sentiment}
                Resolution: {summary.resolution}
                """
            } 