"""
Database Service for FedFina Enhanced Reporting
Handles PostgreSQL database operations for client interviews
"""
import os
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Database Models
Base = declarative_base()

class ClientInterview(Base):
    """Client interview database model"""
    __tablename__ = "client_interviews"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String(255), unique=True, nullable=False, index=True)
    officer_name = Column(String(255), nullable=False)
    officer_email = Column(String(255), nullable=False, index=True)
    client_account_id = Column(String(255), nullable=False, index=True)
    minio_audio_url = Column(Text, nullable=True)
    minio_transcript_url = Column(Text, nullable=True)
    minio_report_url = Column(Text, nullable=True)
    interview_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="completed")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Pydantic Models for API
class ClientInterviewCreate(BaseModel):
    conversation_id: str
    officer_name: str
    officer_email: str
    client_account_id: str
    minio_audio_url: Optional[str] = None
    minio_transcript_url: Optional[str] = None
    minio_report_url: Optional[str] = None
    status: str = "completed"

class ClientInterviewResponse(BaseModel):
    id: int
    conversation_id: str
    officer_name: str
    officer_email: str
    client_account_id: str
    minio_audio_url: Optional[str] = None
    minio_transcript_url: Optional[str] = None
    minio_report_url: Optional[str] = None
    interview_date: datetime
    status: str
    created_at: datetime
    updated_at: datetime

class DatabaseService:
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database connection"""
        try:
            # Get database URL from environment
            database_url = os.getenv("DATABASE_URL", "postgresql://fedfina_app_user:fedfina_app_password_2025@localhost:5432/fedfina_enhanced_reporting")
            
            # Create engine
            self.engine = create_engine(database_url, echo=False)
            
            # Create session factory
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
            # Create tables
            Base.metadata.create_all(bind=self.engine)
            
            logger.info("Database service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            self.engine = None
            self.SessionLocal = None
    
    def get_db_session(self) -> Optional[Session]:
        """Get database session"""
        if self.SessionLocal is None:
            logger.error("Database not initialized")
            return None
        
        try:
            db = self.SessionLocal()
            return db
        except Exception as e:
            logger.error(f"Failed to create database session: {str(e)}")
            return None
    
    async def create_client_interview(self, interview_data: ClientInterviewCreate) -> Optional[ClientInterviewResponse]:
        """Create a new client interview record"""
        try:
            db = self.get_db_session()
            if db is None:
                return None
            
            # Create interview record
            db_interview = ClientInterview(
                conversation_id=interview_data.conversation_id,
                officer_name=interview_data.officer_name,
                officer_email=interview_data.officer_email,
                client_account_id=interview_data.client_account_id,
                minio_audio_url=interview_data.minio_audio_url,
                minio_transcript_url=interview_data.minio_transcript_url,
                minio_report_url=interview_data.minio_report_url,
                status=interview_data.status
            )
            
            db.add(db_interview)
            db.commit()
            db.refresh(db_interview)
            
            logger.info(f"Created client interview record: {interview_data.conversation_id}")
            
            return ClientInterviewResponse(
                id=db_interview.id,
                conversation_id=db_interview.conversation_id,
                officer_name=db_interview.officer_name,
                officer_email=db_interview.officer_email,
                client_account_id=db_interview.client_account_id,
                minio_audio_url=db_interview.minio_audio_url,
                minio_transcript_url=db_interview.minio_transcript_url,
                minio_report_url=db_interview.minio_report_url,
                interview_date=db_interview.interview_date,
                status=db_interview.status,
                created_at=db_interview.created_at,
                updated_at=db_interview.updated_at
            )
            
        except SQLAlchemyError as e:
            logger.error(f"Database error creating client interview: {str(e)}")
            if db:
                db.rollback()
            return None
        except Exception as e:
            logger.error(f"Error creating client interview: {str(e)}")
            if db:
                db.rollback()
            return None
        finally:
            if db:
                db.close()
    
    async def get_client_interview(self, conversation_id: str) -> Optional[ClientInterviewResponse]:
        """Get client interview by conversation ID"""
        try:
            db = self.get_db_session()
            if db is None:
                return None
            
            interview = db.query(ClientInterview).filter(
                ClientInterview.conversation_id == conversation_id
            ).first()
            
            if not interview:
                return None
            
            return ClientInterviewResponse(
                id=interview.id,
                conversation_id=interview.conversation_id,
                officer_name=interview.officer_name,
                officer_email=interview.officer_email,
                client_account_id=interview.client_account_id,
                minio_audio_url=interview.minio_audio_url,
                minio_transcript_url=interview.minio_transcript_url,
                minio_report_url=interview.minio_report_url,
                interview_date=interview.interview_date,
                status=interview.status,
                created_at=interview.created_at,
                updated_at=interview.updated_at
            )
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting client interview: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error getting client interview: {str(e)}")
            return None
        finally:
            if db:
                db.close()
    
    async def update_client_interview(self, conversation_id: str, update_data: Dict[str, Any]) -> Optional[ClientInterviewResponse]:
        """Update client interview record"""
        try:
            db = self.get_db_session()
            if db is None:
                return None
            
            interview = db.query(ClientInterview).filter(
                ClientInterview.conversation_id == conversation_id
            ).first()
            
            if not interview:
                return None
            
            # Update fields
            for field, value in update_data.items():
                if hasattr(interview, field):
                    setattr(interview, field, value)
            
            interview.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(interview)
            
            logger.info(f"Updated client interview record: {conversation_id}")
            
            return ClientInterviewResponse(
                id=interview.id,
                conversation_id=interview.conversation_id,
                officer_name=interview.officer_name,
                officer_email=interview.officer_email,
                client_account_id=interview.client_account_id,
                minio_audio_url=interview.minio_audio_url,
                minio_transcript_url=interview.minio_transcript_url,
                minio_report_url=interview.minio_report_url,
                interview_date=interview.interview_date,
                status=interview.status,
                created_at=interview.created_at,
                updated_at=interview.updated_at
            )
            
        except SQLAlchemyError as e:
            logger.error(f"Database error updating client interview: {str(e)}")
            if db:
                db.rollback()
            return None
        except Exception as e:
            logger.error(f"Error updating client interview: {str(e)}")
            if db:
                db.rollback()
            return None
        finally:
            if db:
                db.close()
    
    async def list_client_interviews(self, 
                                   officer_email: Optional[str] = None,
                                   client_account_id: Optional[str] = None,
                                   status: Optional[str] = None,
                                   limit: int = 100,
                                   offset: int = 0) -> List[ClientInterviewResponse]:
        """List client interviews with optional filters"""
        try:
            db = self.get_db_session()
            if db is None:
                return []
            
            query = db.query(ClientInterview)
            
            # Apply filters
            if officer_email:
                query = query.filter(ClientInterview.officer_email == officer_email)
            
            if client_account_id:
                query = query.filter(ClientInterview.client_account_id == client_account_id)
            
            if status:
                query = query.filter(ClientInterview.status == status)
            
            # Apply pagination
            interviews = query.offset(offset).limit(limit).all()
            
            return [
                ClientInterviewResponse(
                    id=interview.id,
                    conversation_id=interview.conversation_id,
                    officer_name=interview.officer_name,
                    officer_email=interview.officer_email,
                    client_account_id=interview.client_account_id,
                    minio_audio_url=interview.minio_audio_url,
                    minio_transcript_url=interview.minio_transcript_url,
                    minio_report_url=interview.minio_report_url,
                    interview_date=interview.interview_date,
                    status=interview.status,
                    created_at=interview.created_at,
                    updated_at=interview.updated_at
                )
                for interview in interviews
            ]
            
        except SQLAlchemyError as e:
            logger.error(f"Database error listing client interviews: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error listing client interviews: {str(e)}")
            return []
        finally:
            if db:
                db.close()
    
    async def get_interview_statistics(self, officer_email: Optional[str] = None) -> Dict[str, Any]:
        """Get interview statistics"""
        try:
            db = self.get_db_session()
            if db is None:
                return {}
            
            query = db.query(ClientInterview)
            
            if officer_email:
                query = query.filter(ClientInterview.officer_email == officer_email)
            
            total_interviews = query.count()
            completed_interviews = query.filter(ClientInterview.status == "completed").count()
            failed_interviews = query.filter(ClientInterview.status == "failed").count()
            
            # Get recent interviews (last 30 days)
            from datetime import timedelta
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_interviews = query.filter(ClientInterview.created_at >= thirty_days_ago).count()
            
            return {
                "total_interviews": total_interviews,
                "completed_interviews": completed_interviews,
                "failed_interviews": failed_interviews,
                "recent_interviews": recent_interviews,
                "success_rate": (completed_interviews / total_interviews * 100) if total_interviews > 0 else 0
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting statistics: {str(e)}")
            return {}
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            return {}
        finally:
            if db:
                db.close()
    
    def get_config_status(self) -> Dict[str, Any]:
        """Get database configuration status"""
        return {
            "database_url_configured": bool(os.getenv("DATABASE_URL")),
            "engine_available": self.engine is not None,
            "session_factory_available": self.SessionLocal is not None,
            "tables_created": self.engine is not None
        } 