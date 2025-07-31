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

class KeyFactor(BaseModel):
    category: str
    points: List[str]

class RiskFactor(BaseModel):
    risk_type: str
    description: str
    severity: str

class ThirdPartyIntervention(BaseModel):
    speaker: str
    questions_answered: List[str]
    risk_level: str

class ThirdPartyInterventionSummary(BaseModel):
    detected: bool
    speakers: List[str]
    intervention_details: List[ThirdPartyIntervention]

class ConversationSummary(BaseModel):
    topic: str
    sentiment: str
    resolution: str
    keywords: Optional[List[str]] = None
    intent: Optional[str] = None
    summary: str
    key_factors: Optional[List[KeyFactor]] = None
    risk_factors: Optional[List[RiskFactor]] = None
    third_party_intervention: Optional[ThirdPartyInterventionSummary] = None
    recommendations: Optional[List[str]] = None
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
            Analyze the following conversation transcript and create a comprehensive business assessment summary.
            
            Account ID: {account_id}
            User Email: {email_id}
            
            Conversation Transcript:
            {formatted_transcript}
            
            Please provide a detailed analysis in the following JSON format:
            {{
                "topic": "Main topic of conversation (e.g., Business Loan Application Assessment)",
                "sentiment": "Overall sentiment (positive/negative/neutral)",
                "resolution": "How the conversation was resolved or current status",
                "keywords": ["key", "business", "terms", "extracted"],
                "intent": "Primary business intent or purpose",
                "summary": "Detailed summary of the conversation in English",
                "key_factors": [
                    {{
                        "category": "Business Profile",
                        "points": ["bullet point 1", "bullet point 2"]
                    }},
                    {{
                        "category": "Financial Information",
                        "points": ["bullet point 1", "bullet point 2"]
                    }},
                    {{
                        "category": "Operational Details",
                        "points": ["bullet point 1", "bullet point 2"]
                    }}
                ],
                "risk_factors": [
                    {{
                        "risk_type": "Financial Risk",
                        "description": "Description of the risk",
                        "severity": "High/Medium/Low"
                    }},
                    {{
                        "risk_type": "Operational Risk", 
                        "description": "Description of the risk",
                        "severity": "High/Medium/Low"
                    }}
                ],
                "third_party_intervention": {{
                    "detected": true/false,
                    "speakers": ["list of all speakers identified"],
                    "intervention_details": [
                        {{
                            "speaker": "name of third party",
                            "questions_answered": ["specific questions they answered"],
                            "risk_level": "High/Medium/Low"
                        }}
                    ]
                }},
                "recommendations": ["recommendation 1", "recommendation 2"],
                "action_items": ["action item 1", "action item 2"],
                "follow_up_required": true/false
            }}
            
            Focus on:
            1. Key business factors and information requested by the interviewer
            2. Financial details, operational structure, and business model
            3. Risk factors and potential concerns
            4. Any third-party intervention (someone other than the main interviewee answering questions)
            5. Specific recommendations and action items
            6. Overall assessment for business loan or credit purposes
            
            Note: If the conversation is in Hindi or other languages, provide the summary in English.
            Identify any third-party speakers and mark their interventions as potential risks.
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
            
            # Parse key factors
            key_factors = []
            if "key_factors" in analysis_data:
                for factor in analysis_data["key_factors"]:
                    key_factors.append(KeyFactor(
                        category=factor.get("category", ""),
                        points=factor.get("points", [])
                    ))
            
            # Parse risk factors
            risk_factors = []
            if "risk_factors" in analysis_data:
                for risk in analysis_data["risk_factors"]:
                    risk_factors.append(RiskFactor(
                        risk_type=risk.get("risk_type", ""),
                        description=risk.get("description", ""),
                        severity=risk.get("severity", "Medium")
                    ))
            
            # Parse third-party intervention
            third_party_intervention = None
            if "third_party_intervention" in analysis_data:
                intervention_data = analysis_data["third_party_intervention"]
                intervention_details = []
                if "intervention_details" in intervention_data:
                    for detail in intervention_data["intervention_details"]:
                        intervention_details.append(ThirdPartyIntervention(
                            speaker=detail.get("speaker", ""),
                            questions_answered=detail.get("questions_answered", []),
                            risk_level=detail.get("risk_level", "Medium")
                        ))
                
                third_party_intervention = ThirdPartyInterventionSummary(
                    detected=intervention_data.get("detected", False),
                    speakers=intervention_data.get("speakers", []),
                    intervention_details=intervention_details
                )
            
            return ConversationSummary(
                topic=analysis_data.get("topic", "Business Assessment"),
                sentiment=analysis_data.get("sentiment", "neutral"),
                resolution=analysis_data.get("resolution", "Assessment in progress"),
                keywords=analysis_data.get("keywords", []),
                intent=analysis_data.get("intent", "Business assessment"),
                summary=analysis_data.get("summary", "No summary available"),
                key_factors=key_factors,
                risk_factors=risk_factors,
                third_party_intervention=third_party_intervention,
                recommendations=analysis_data.get("recommendations", []),
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