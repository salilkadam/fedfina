"""
Pydantic models for OpenAI structured responses
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class CustomerInfo(BaseModel):
    """Customer information extracted from the interview"""
    name: str = Field(..., description="Customer/applicant name")
    interview_date: str = Field(default="Not specified", description="Interview date/time")
    business_name: str = Field(default="Not specified", description="Business name")


class ExecutiveSummary(BaseModel):
    """Executive summary of the interview"""
    overview: str = Field(..., description="Comprehensive narrative overview without specific numbers")
    financial_assessment: Optional[str] = Field(default=None, description="Financial assessment summary")


class IncomeSummary(BaseModel):
    """Income information from the interview"""
    summary: str = Field(..., description="Brief overview of income sources")
    details: List[str] = Field(default_factory=list, description="Detailed income information with bullet points")
    total_monthly_income: str = Field(default="No specific information provided", description="Total monthly income")
    seasonal_variations: str = Field(default="No specific information provided", description="Seasonal income patterns")


class ExpenseSummary(BaseModel):
    """Expense information from the interview"""
    summary: str = Field(..., description="Brief overview of expense categories")
    business_expenses: List[str] = Field(default_factory=list, description="Business expenses with bullet points")
    personal_expenses: List[str] = Field(default_factory=list, description="Personal expenses with bullet points")
    total_monthly_expenses: str = Field(default="No specific information provided", description="Total monthly expenses")


class LoanDisbursementSummary(BaseModel):
    """Loan disbursement information from the interview"""
    summary: str = Field(..., description="Brief overview of loan requirements")
    requested_amount: str = Field(default="No specific information provided", description="Requested loan amount")
    purposes: List[str] = Field(default_factory=list, description="Loan purposes with bullet points")
    repayment_plan: str = Field(default="No specific information provided", description="EMI and repayment details")
    timeline: str = Field(default="No specific information provided", description="Expected timeline")


class Risks(BaseModel):
    """Risk assessment from the interview"""
    summary: str = Field(..., description="Brief overview of identified risks")
    multiple_speakers: str = Field(default="No", description="Multiple speakers detection")
    financial_risks: List[str] = Field(default_factory=list, description="Financial risks with bullet points")
    business_risks: List[str] = Field(default_factory=list, description="Business risks with bullet points")
    other_concerns: List[str] = Field(default_factory=list, description="Other concerns with bullet points")


class OpenAIStructuredResponse(BaseModel):
    """Complete structured response from OpenAI"""
    customer_info: Optional[CustomerInfo] = None
    executive_summary: Optional[ExecutiveSummary] = None
    income_summary: Optional[IncomeSummary] = None
    expense_summary: Optional[ExpenseSummary] = None
    loan_disbursement_summary: Optional[LoanDisbursementSummary] = None
    risks: Optional[Risks] = None
    
    class Config:
        """Pydantic configuration"""
        extra = "ignore"  # Ignore extra fields
        validate_assignment = True  # Validate on assignment
