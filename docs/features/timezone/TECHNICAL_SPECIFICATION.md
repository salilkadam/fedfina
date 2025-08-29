# 🌍 IST Timezone Technical Specification

## 📋 **Overview**

This document provides the detailed technical specification for implementing Indian Standard Time (IST) timezone support in the FedFina Postprocess API. The implementation follows Option 1: Application-Level Timezone Handling.

## 🏗️ **Architecture Design**

### **High-Level Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Layer     │    │  Service Layer  │    │  Database Layer │
│                 │    │                 │    │                 │
│ • FastAPI       │───▶│ • TimezoneService│───▶│ • PostgreSQL    │
│ • Request/      │    │ • DatabaseService│    │ • UTC Storage   │
│   Response      │    │ • PDFService     │    │ • UTC Queries   │
│ • IST Display   │    │ • EmailService   │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Configuration │    │   Conversion    │    │   Storage       │
│                 │    │                 │    │                 │
│ • Environment   │    │ • UTC ↔ IST     │    │ • UTC Timestamps│
│ • Settings      │    │ • Date Ranges   │    │ • UTC Queries   │
│ • Timezone      │    │ • Business Hours│    │ • UTC Indexes   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **Data Flow**

1. **Input**: API requests with date parameters (IST assumed)
2. **Conversion**: TimezoneService converts IST dates to UTC for database queries
3. **Storage**: Database stores and queries data in UTC
4. **Conversion**: TimezoneService converts UTC results to IST for API responses
5. **Output**: API responses with IST timestamps and timezone information

## 🔧 **Core Components**

### **1. TimezoneService**

#### **Class Definition**
```python
from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple
import pytz
from config import Settings

class TimezoneService:
    """Centralized timezone conversion utility for IST support"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.ist_timezone = pytz.timezone("Asia/Kolkata")
        self.utc_timezone = pytz.timezone("UTC")
        self.timezone_offset = timedelta(hours=settings.timezone_offset_hours, 
                                       minutes=settings.timezone_offset_minutes)
        self.business_start_hour = settings.business_start_hour
        self.business_end_hour = settings.business_end_hour
```

#### **Core Methods**

**UTC to IST Conversion**
```python
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
        raise ValueError(f"Failed to convert UTC to IST: {e}")
```

**IST to UTC Conversion**
```python
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
        raise ValueError(f"Failed to convert IST to UTC: {e}")
```

**IST Date Range for Database Queries**
```python
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
        
        return start_utc, end_utc
    except Exception as e:
        raise ValueError(f"Failed to get IST date range: {e}")
```

**Business Hours Detection**
```python
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
```

**IST Timestamp Formatting**
```python
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
```

### **2. Configuration Updates**

#### **Settings Class Extension**
```python
# backend/config.py
class Settings(BaseSettings):
    # ... existing settings ...
    
    # Timezone Configuration
    default_timezone: str = Field(default="Asia/Kolkata", env="DEFAULT_TIMEZONE")
    timezone_offset_hours: int = Field(default=5, env="TIMEZONE_OFFSET_HOURS")
    timezone_offset_minutes: int = Field(default=30, env="TIMEZONE_OFFSET_MINUTES")
    
    # Business Hours (IST)
    business_start_hour: int = Field(default=9, env="BUSINESS_START_HOUR")
    business_end_hour: int = Field(default=18, env="BUSINESS_END_HOUR")
    
    # Timezone Feature Flags
    enable_ist_timezone: bool = Field(default=True, env="ENABLE_IST_TIMEZONE")
    show_timezone_info: bool = Field(default=True, env="SHOW_TIMEZONE_INFO")
    
    @validator('timezone_offset_hours')
    def validate_timezone_offset_hours(cls, v):
        if not -12 <= v <= 14:
            raise ValueError('timezone_offset_hours must be between -12 and 14')
        return v
    
    @validator('timezone_offset_minutes')
    def validate_timezone_offset_minutes(cls, v):
        if not 0 <= v <= 59:
            raise ValueError('timezone_offset_minutes must be between 0 and 59')
        return v
    
    @validator('business_start_hour')
    def validate_business_start_hour(cls, v):
        if not 0 <= v <= 23:
            raise ValueError('business_start_hour must be between 0 and 23')
        return v
    
    @validator('business_end_hour')
    def validate_business_end_hour(cls, v):
        if not 0 <= v <= 23:
            raise ValueError('business_end_hour must be between 0 and 23')
        return v
```

#### **Environment Variables**
```bash
# Timezone Configuration
DEFAULT_TIMEZONE=Asia/Kolkata
TIMEZONE_OFFSET_HOURS=5
TIMEZONE_OFFSET_MINUTES=30
BUSINESS_START_HOUR=9
BUSINESS_END_HOUR=18
ENABLE_IST_TIMEZONE=true
SHOW_TIMEZONE_INFO=true
```

### **3. Database Service Updates**

#### **Modified DatabaseService**
```python
# backend/services/database_service.py
class DatabaseService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.connection_string = settings.database_url
        self.timezone_service = TimezoneService(settings)
    
    async def get_conversations_by_date(self, target_date: datetime) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get conversations for IST date with timezone-aware filtering
        
        Args:
            target_date: IST date (datetime object)
            
        Returns:
            Dictionary with account_id as key and list of conversations as value
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Convert IST date to UTC range for database query
            if target_date.tzinfo is None:
                target_date = self.timezone_service.ist_timezone.localize(target_date)
            
            start_date, end_date = self.timezone_service.get_ist_date_range(
                target_date.strftime("%Y-%m-%d")
            )
            
            # Database query remains the same (uses UTC)
            cursor.execute("""
                WITH ranked_conversations AS (
                    SELECT 
                        id, account_id, email_id, conversation_id, created_at,
                        transcript_url, audio_url, report_url,
                        ROW_NUMBER() OVER (
                            PARTITION BY conversation_id 
                            ORDER BY created_at DESC
                        ) as rn
                    FROM conversation_runs 
                    WHERE created_at >= %s AND created_at <= %s
                )
                SELECT id, account_id, email_id, conversation_id, created_at,
                       transcript_url, audio_url, report_url
                FROM ranked_conversations 
                WHERE rn = 1
                ORDER BY account_id, created_at DESC
            """, (start_date, end_date))
            
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            
            # Convert UTC timestamps to IST for response
            conversations_by_account = {}
            for row in rows:
                account_id = row[1]
                ist_created_at = self.timezone_service.utc_to_ist(row[4])
                
                conversation = {
                    "id": row[0],
                    "account_id": row[1],
                    "email_id": row[2],
                    "conversation_id": row[3],
                    "created_at": ist_created_at,
                    "transcript_url": row[5],
                    "audio_url": row[6],
                    "report_url": row[7]
                }
                
                if account_id not in conversations_by_account:
                    conversations_by_account[account_id] = []
                
                conversations_by_account[account_id].append(conversation)
            
            return conversations_by_account
            
        except Exception as e:
            logger.error(f"Error getting conversations for date {target_date}: {e}")
            return {}
```

### **4. API Response Format**

#### **Updated API Response Structure**
```json
{
  "status": "success",
  "date": "2025-08-29",
  "timezone": "IST (UTC+5:30)",
  "total_conversations": 5,
  "total_accounts": 2,
  "accounts": {
    "account_id": {
      "count": 3,
      "conversations": [
        {
          "account_id": "account_id",
          "email_id": "user@example.com",
          "timestamp": "2025-08-29T22:39:45.309874+05:30",
          "timestamp_ist": "2025-08-29 22:39:45 IST",
          "timestamp_utc": "2025-08-29T17:09:45.309842+00:00",
          "conversation_id": "conv_1234567890abcdef",
          "transcript_url": "https://fedfina.bionicaisolutions.com/api/v1/download/secure/token123",
          "audio_url": "https://fedfina.bionicaisolutions.com/api/v1/download/secure/token456",
          "report_url": "https://fedfina.bionicaisolutions.com/api/v1/download/secure/token789"
        }
      ]
    }
  }
}
```

### **5. PDF Service Updates**

#### **Modified PDF Service**
```python
# backend/services/pdf_service.py
class PDFService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.timezone_service = TimezoneService(settings)
        # ... existing initialization ...
    
    def _create_header(self, conversation_id: str, metadata: Dict[str, Any]) -> List:
        # ... existing code ...
        
        # Report Generated Date (IST)
        ist_now = self.timezone_service.get_ist_now()
        timestamp = Paragraph(
            f"<b>Report Generated:</b> {self.timezone_service.format_ist_timestamp(ist_now)}",
            self.styles['CustomBody']
        )
        elements.append(timestamp)
        
        # Add timezone information
        timezone_info = Paragraph(
            f"<b>Timezone:</b> Indian Standard Time (IST - UTC+5:30)",
            self.styles['CustomBody']
        )
        elements.append(timezone_info)
        
        # ... rest of existing code ...
```

### **6. Email Service Updates**

#### **Modified Email Service**
```python
# backend/services/email_service.py
class EmailService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.timezone_service = TimezoneService(settings)
        # ... existing initialization ...
    
    def _create_email_body_with_links(self, conversation_id: str, account_id: str, 
                                     files: Dict[str, str], metadata: Dict[str, Any]) -> str:
        # ... existing code ...
        
        # Add IST timestamp
        ist_timestamp = self.timezone_service.format_ist_timestamp(datetime.now())
        body += f"<p><strong>Report Generated:</strong> {ist_timestamp}</p>"
        body += f"<p><strong>Timezone:</strong> Indian Standard Time (IST - UTC+5:30)</p>"
        
        # ... rest of existing code ...
```

## 🧪 **Testing Strategy**

### **Unit Tests**

#### **TimezoneService Tests**
```python
# tests/unit/test_timezone_service.py
import pytest
from datetime import datetime, timezone
from backend.services.timezone_service import TimezoneService
from backend.config import Settings

class TestTimezoneService:
    @pytest.fixture
    def settings(self):
        return Settings(
            timezone_offset_hours=5,
            timezone_offset_minutes=30,
            business_start_hour=9,
            business_end_hour=18
        )
    
    @pytest.fixture
    def timezone_service(self, settings):
        return TimezoneService(settings)
    
    def test_utc_to_ist_conversion(self, timezone_service):
        # Test UTC to IST conversion
        utc_time = datetime(2025, 8, 29, 17, 9, 45, tzinfo=timezone.utc)
        ist_time = timezone_service.utc_to_ist(utc_time)
        
        assert ist_time.hour == 22
        assert ist_time.minute == 39
        assert ist_time.tzinfo.zone == "Asia/Kolkata"
    
    def test_ist_to_utc_conversion(self, timezone_service):
        # Test IST to UTC conversion
        ist_time = datetime(2025, 8, 29, 22, 39, 45)
        ist_time = timezone_service.ist_timezone.localize(ist_time)
        utc_time = timezone_service.ist_to_utc(ist_time)
        
        assert utc_time.hour == 17
        assert utc_time.minute == 9
        assert utc_time.tzinfo.zone == "UTC"
    
    def test_ist_date_range(self, timezone_service):
        # Test IST date range calculation
        start_utc, end_utc = timezone_service.get_ist_date_range("2025-08-29")
        
        # Verify start of IST day (00:00 IST = 18:30 UTC previous day)
        assert start_utc.hour == 18
        assert start_utc.minute == 30
        
        # Verify end of IST day (23:59 IST = 18:29 UTC next day)
        assert end_utc.hour == 18
        assert end_utc.minute == 29
    
    def test_business_hours(self, timezone_service):
        # Test business hours detection
        business_time = datetime(2025, 8, 29, 14, 0, 0)  # 2 PM IST
        non_business_time = datetime(2025, 8, 29, 22, 0, 0)  # 10 PM IST
        
        assert timezone_service.is_business_hours(business_time) == True
        assert timezone_service.is_business_hours(non_business_time) == False
```

#### **Database Service Tests**
```python
# tests/unit/test_database_service_timezone.py
import pytest
from datetime import datetime
from backend.services.database_service import DatabaseService
from backend.config import Settings

class TestDatabaseServiceTimezone:
    @pytest.fixture
    def settings(self):
        return Settings(
            timezone_offset_hours=5,
            timezone_offset_minutes=30
        )
    
    @pytest.fixture
    def db_service(self, settings):
        return DatabaseService(settings)
    
    @pytest.mark.asyncio
    async def test_get_conversations_by_date_ist(self, db_service, mock_db_connection):
        # Test IST date filtering
        ist_date = datetime(2025, 8, 29, 10, 0, 0)  # 10 AM IST
        result = await db_service.get_conversations_by_date(ist_date)
        
        # Verify that database query uses correct UTC range
        # Verify that response timestamps are in IST
        assert all(conv['created_at'].tzinfo.zone == "Asia/Kolkata" 
                  for conv in result.get('account_id', []))
```

### **Integration Tests**

#### **API Endpoint Tests**
```python
# tests/integration/test_api_timezone.py
import pytest
from fastapi.testclient import TestClient
from backend.app import app

class TestAPITimezone:
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_conversations_by_date_ist(self, client):
        # Test API endpoint with IST date
        response = client.get("/api/v1/conversations-by-date?date=2025-08-29")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify timezone information
        assert data['timezone'] == "IST (UTC+5:30)"
        
        # Verify IST timestamps in response
        for account_data in data['accounts'].values():
            for conv in account_data['conversations']:
                assert 'timestamp_ist' in conv
                assert conv['timestamp_ist'].endswith('IST')
```

### **Performance Tests**

#### **Timezone Conversion Performance**
```python
# tests/performance/test_timezone_performance.py
import time
import pytest
from datetime import datetime, timezone
from backend.services.timezone_service import TimezoneService
from backend.config import Settings

class TestTimezonePerformance:
    @pytest.fixture
    def timezone_service(self):
        settings = Settings()
        return TimezoneService(settings)
    
    def test_conversion_performance(self, timezone_service):
        # Test timezone conversion performance
        utc_time = datetime(2025, 8, 29, 17, 9, 45, tzinfo=timezone.utc)
        
        start_time = time.time()
        for _ in range(1000):
            ist_time = timezone_service.utc_to_ist(utc_time)
        end_time = time.time()
        
        # Should complete 1000 conversions in less than 1 second
        assert (end_time - start_time) < 1.0
```

## 📊 **Performance Considerations**

### **Optimization Strategies**

1. **Caching**: Cache timezone conversion results for frequently used dates
2. **Batch Processing**: Process multiple timestamps in batches
3. **Lazy Loading**: Convert timestamps only when needed
4. **Database Indexing**: Ensure proper indexing on timestamp columns

### **Memory Usage**

- **Timezone Objects**: ~1KB per timezone object
- **Conversion Overhead**: ~100 bytes per conversion
- **Total Impact**: < 1MB for typical usage

### **CPU Usage**

- **Single Conversion**: ~0.1ms
- **Batch Conversion**: ~0.01ms per conversion
- **Database Query Impact**: < 5% increase

## 🔒 **Security Considerations**

### **Input Validation**

1. **Date Format Validation**: Strict validation of date input formats
2. **Timezone Validation**: Validate timezone parameters
3. **SQL Injection Prevention**: Use parameterized queries
4. **Error Handling**: Don't expose internal timezone errors

### **Data Integrity**

1. **UTC Storage**: Always store timestamps in UTC
2. **Conversion Accuracy**: Ensure accurate timezone conversions
3. **Audit Trail**: Log timezone conversion operations
4. **Backup Strategy**: Maintain UTC backups

## 📚 **Documentation Requirements**

### **API Documentation**

1. **Timezone Parameters**: Document timezone handling in API docs
2. **Response Format**: Document IST timestamp format
3. **Error Codes**: Document timezone-related error codes
4. **Examples**: Provide timezone conversion examples

### **User Documentation**

1. **Timezone Guide**: User guide for timezone handling
2. **Migration Guide**: Guide for existing users
3. **FAQ**: Common timezone questions
4. **Troubleshooting**: Timezone-related issues

### **Developer Documentation**

1. **TimezoneService API**: Complete API documentation
2. **Configuration Guide**: Timezone configuration options
3. **Testing Guide**: How to test timezone functionality
4. **Deployment Guide**: Timezone deployment considerations

---

*This technical specification will be updated as implementation progresses and new requirements are identified.*
