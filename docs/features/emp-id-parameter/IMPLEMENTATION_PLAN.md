# Implementation Plan: Add emp_id Parameter

## Overview
This feature adds a new `emp_id` parameter alongside the existing `account_id` and `email_id` parameters throughout the system. The `emp_id` will be used to identify specific employees within an account, providing better granularity for conversation tracking and reporting.

## Current State Analysis
- **Backend**: Currently supports `account_id` and `email_id` in all API endpoints
- **Frontend**: Landing page displays and uses `account_id` and `email_id` from URL parameters
- **Database**: `conversation_runs` table stores `account_id` and `email_id`
- **Webhook**: ElevenLabs webhook processes `account_id` and `email_id` from dynamic variables
- **API Endpoints**: 
  - `/api/v1/conversations-by-date` returns conversations grouped by account
  - `/api/v1/webhook/elevenlabs` processes webhooks with account and email IDs

## Implementation Phases

### Phase 1: Database Schema Updates
**Duration**: 1-2 hours
**Objective**: Add `emp_id` column to relevant database tables

**Tasks**:
- [ ] Create migration script to add `emp_id` column to `conversation_runs` table
- [ ] Update `conversation_processing` table to include `emp_id`
- [ ] Add appropriate indexes for `emp_id` column
- [ ] Test migration on test database

**Files to Modify**:
- `backend/migrations/002_add_emp_id_column.sql` (new)
- `backend/services/database_service.py`

**Validation**:
- [ ] Migration runs successfully
- [ ] New columns are accessible
- [ ] Indexes are created properly

### Phase 2: Backend Model Updates
**Duration**: 1-2 hours
**Objective**: Update Pydantic models and validation logic

**Tasks**:
- [ ] Update `PostprocessRequest` model to include `emp_id` field
- [ ] Add validation for `emp_id` format and requirements
- [ ] Update related response models if needed
- [ ] Update database service methods to handle `emp_id`

**Files to Modify**:
- `backend/models/postprocess_models.py`
- `backend/services/database_service.py`

**Validation**:
- [ ] Models validate correctly with new field
- [ ] Database operations work with new parameter
- [ ] All existing functionality remains intact

### Phase 3: API Endpoint Updates
**Duration**: 2-3 hours
**Objective**: Update API endpoints to handle and return `emp_id`

**Tasks**:
- [ ] Update `/api/v1/conversations-by-date` endpoint to include `emp_id` in response
- [ ] Update webhook endpoint to extract and process `emp_id`
- [ ] Ensure `emp_id` is passed through the entire processing pipeline
- [ ] Update error handling for missing `emp_id`

**Files to Modify**:
- `backend/app.py`

**Validation**:
- [ ] API endpoints accept and return `emp_id`
- [ ] Webhook processing includes `emp_id`
- [ ] Error handling works correctly
- [ ] All existing functionality preserved

### Phase 4: Frontend Updates
**Duration**: 2-3 hours
**Objective**: Update frontend to display and use `emp_id` parameter

**Tasks**:
- [ ] Update URL parameter extraction to include `emp_id`
- [ ] Modify landing page display to show all three parameters
- [ ] Update widget configuration to pass `emp_id` as dynamic variable
- [ ] Ensure consistent look and feel with three parameters
- [ ] Update test section to include `emp_id`

**Files to Modify**:
- `frontend/src/App.tsx`

**Validation**:
- [ ] Frontend displays all three parameters correctly
- [ ] Widget receives `emp_id` parameter
- [ ] UI layout accommodates three parameters gracefully
- [ ] All existing functionality works

### Phase 5: Testing and Validation
**Duration**: 2-3 hours
**Objective**: Comprehensive testing of all changes

**Tasks**:
- [ ] Update existing unit tests to include `emp_id`
- [ ] Create new test cases for `emp_id` functionality
- [ ] Test API endpoints with new parameter
- [ ] Test webhook processing with `emp_id`
- [ ] Test frontend with three parameters
- [ ] Integration testing with live services

**Files to Modify**:
- `tests/unit/` (update existing tests)
- `tests/integration/` (update existing tests)

**Validation**:
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] API endpoints work correctly
- [ ] Frontend functions properly
- [ ] Webhook processing includes `emp_id`

### Phase 6: Documentation and Deployment
**Duration**: 1-2 hours
**Objective**: Update documentation and prepare for deployment

**Tasks**:
- [ ] Update API documentation
- [ ] Update deployment scripts if needed
- [ ] Create rollback plan
- [ ] Document breaking changes (if any)
- [ ] Prepare deployment checklist

**Files to Modify**:
- API documentation
- Deployment scripts (if needed)

**Validation**:
- [ ] Documentation is accurate and complete
- [ ] Deployment plan is ready
- [ ] Rollback procedures documented

## Technical Specifications

### Database Changes
```sql
-- Add emp_id column to conversation_runs table
ALTER TABLE conversation_runs ADD COLUMN emp_id TEXT;

-- Add index for emp_id
CREATE INDEX idx_conversation_runs_emp_id ON conversation_runs(emp_id);

-- Add emp_id column to conversation_processing table
ALTER TABLE conversation_processing ADD COLUMN emp_id TEXT;

-- Add index for emp_id
CREATE INDEX idx_conversation_processing_emp_id ON conversation_processing(emp_id);
```

### API Changes
- **Request Models**: Add `emp_id: str` field to `PostprocessRequest`
- **Response Models**: Include `emp_id` in conversation data responses
- **Validation**: Ensure `emp_id` is provided and valid
- **Webhook**: Extract `emp_id` from dynamic variables

### Frontend Changes
- **URL Parameters**: Support `?email_id=...&account_id=...&emp_id=...`
- **Display**: Show all three parameters in consistent format
- **Widget**: Pass `emp_id` as dynamic variable to ElevenLabs widget

## Risk Assessment

### Low Risk
- Adding new optional field to existing models
- Frontend display updates
- Database schema additions

### Medium Risk
- API endpoint modifications
- Webhook processing changes
- Database migration execution

### Mitigation Strategies
- Comprehensive testing at each phase
- Backward compatibility maintenance
- Rollback procedures for database changes
- Gradual deployment with monitoring

## Success Criteria
- [ ] All three parameters (`account_id`, `email_id`, `emp_id`) are consistently handled
- [ ] API endpoints accept and return `emp_id` correctly
- [ ] Webhook processing includes `emp_id` parameter
- [ ] Frontend displays three parameters consistently
- [ ] All existing functionality remains intact
- [ ] All tests pass
- [ ] No breaking changes to existing APIs

## Dependencies
- Database access for migration execution
- Test environment availability
- ElevenLabs widget compatibility verification
- Frontend build and deployment pipeline

## Timeline
**Total Estimated Duration**: 9-15 hours
**Recommended Approach**: Implement in phases with testing at each stage
**Critical Path**: Database → Backend → Frontend → Testing → Deployment
