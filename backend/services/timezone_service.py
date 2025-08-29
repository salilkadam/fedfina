"""
Timezone Service for IST timezone support

This module provides centralized timezone conversion utilities for
Indian Standard Time (IST - UTC+5:30) support in the FedFina Postprocess API.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple
import pytz
from config import Settings

logger = logging.getLogger(__name__)


class TimezoneService:
    """Centralized timezone conversion utility for IST support"""
    
    def __init__(self, settings: Settings):
        """
        Initialize TimezoneService with configuration
        
        Args:
            settings: Application settings containing timezone configuration
        """
        self.settings = settings
        self.ist_timezone = pytz.timezone("Asia/Kolkata")
        self.utc_timezone = pytz.timezone("UTC")
        self.timezone_offset = timedelta(
            hours=settings.timezone_offset_hours, 
            minutes=settings.timezone_offset_minutes
        )
        self.business_start_hour = settings.business_start_hour
        self.business_end_hour = settings.business_end_hour
        
        logger.info(f"TimezoneService initialized with IST timezone (UTC+{settings.timezone_offset_hours}:{settings.timezone_offset_minutes:02d})")
    
    def utc_to_ist(self, utc_datetime: datetime) -> datetime:
        """
        Convert UTC datetime to IST
        
        Args:
            utc_datetime: UTC datetime object (with or without timezone info)
            
        Returns:
            IST datetime object with timezone info
            
        Raises:
            ValueError: If datetime conversion fails
        """
        try:
            if utc_datetime.tzinfo is None:
                utc_datetime = utc_datetime.replace(tzinfo=self.utc_timezone)
            return utc_datetime.astimezone(self.ist_timezone)
        except Exception as e:
            logger.error(f"Failed to convert UTC to IST: {e}")
            raise ValueError(f"Failed to convert UTC to IST: {e}")
    
    def ist_to_utc(self, ist_datetime: datetime) -> datetime:
        """
        Convert IST datetime to UTC
        
        Args:
            ist_datetime: IST datetime object (with or without timezone info)
            
        Returns:
            UTC datetime object with timezone info
            
        Raises:
            ValueError: If datetime conversion fails
        """
        try:
            if ist_datetime.tzinfo is None:
                ist_datetime = ist_datetime.replace(tzinfo=self.ist_timezone)
            return ist_datetime.astimezone(self.utc_timezone)
        except Exception as e:
            logger.error(f"Failed to convert IST to UTC: {e}")
            raise ValueError(f"Failed to convert IST to UTC: {e}")
    
    def get_ist_now(self) -> datetime:
        """
        Get current time in IST
        
        Returns:
            Current IST datetime object with timezone info
        """
        try:
            return datetime.now(self.ist_timezone)
        except Exception as e:
            logger.error(f"Failed to get IST now: {e}")
            # Fallback to UTC + offset
            utc_now = datetime.now(timezone.utc)
            return utc_now + self.timezone_offset
    
    def get_ist_date_range(self, date_str: str) -> Tuple[datetime, datetime]:
        """
        Get UTC date range for IST date to use in database queries
        
        Args:
            date_str: Date string in YYYY-MM-DD format (IST date)
            
        Returns:
            Tuple of (start_utc, end_utc) for database queries
            
        Example:
            get_ist_date_range("2025-08-29") returns UTC range for IST 2025-08-29
        """
        try:
            # Parse IST date
            ist_date = datetime.strptime(date_str, "%Y-%m-%d")
            ist_date = self.ist_timezone.localize(ist_date)
            
            # Get start and end of IST day
            start_of_day = ist_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = ist_date.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            # Convert to UTC for database queries
            start_utc = self.ist_to_utc(start_of_day)
            end_utc = self.ist_to_utc(end_of_day)
            
            logger.debug(f"IST date range for {date_str}: {start_utc} to {end_utc}")
            return start_utc, end_utc
        except Exception as e:
            logger.error(f"Failed to get IST date range for {date_str}: {e}")
            raise ValueError(f"Failed to get IST date range: {e}")
    
    def is_business_hours(self, ist_datetime: datetime) -> bool:
        """
        Check if given IST datetime is within business hours
        
        Args:
            ist_datetime: IST datetime object
            
        Returns:
            True if within business hours, False otherwise
        """
        try:
            if ist_datetime.tzinfo is None:
                ist_datetime = ist_datetime.replace(tzinfo=self.ist_timezone)
            
            hour = ist_datetime.hour
            return self.business_start_hour <= hour < self.business_end_hour
        except Exception as e:
            logger.warning(f"Failed to check business hours: {e}")
            return False
    
    def format_ist_timestamp(self, datetime_obj: datetime, include_timezone: bool = True) -> str:
        """
        Format datetime object as IST timestamp string
        
        Args:
            datetime_obj: Datetime object (UTC or IST)
            include_timezone: Whether to include timezone info
            
        Returns:
            Formatted IST timestamp string
        """
        try:
            # Convert to IST if needed
            if datetime_obj.tzinfo is None:
                datetime_obj = datetime_obj.replace(tzinfo=self.utc_timezone)
            
            ist_datetime = self.utc_to_ist(datetime_obj)
            
            if include_timezone:
                return ist_datetime.strftime("%Y-%m-%d %H:%M:%S IST")
            else:
                return ist_datetime.strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            logger.error(f"Failed to format IST timestamp: {e}")
            return str(datetime_obj)
    
    def get_timezone_info(self) -> dict:
        """
        Get timezone information for API responses
        
        Returns:
            Dictionary with timezone information
        """
        return {
            "timezone": "IST (UTC+5:30)",
            "offset_hours": self.settings.timezone_offset_hours,
            "offset_minutes": self.settings.timezone_offset_minutes,
            "business_start_hour": self.business_start_hour,
            "business_end_hour": self.business_end_hour,
            "enabled": self.settings.enable_ist_timezone
        }
    
    def validate_ist_date(self, date_str: str) -> bool:
        """
        Validate IST date string format
        
        Args:
            date_str: Date string to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
