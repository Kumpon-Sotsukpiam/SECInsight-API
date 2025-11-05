# -*- coding: utf-8 -*-
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

class IncomeStatementRequest(BaseModel):
    cik: str = Field(..., description="Company CIK number")
    user_agent: str = Field(..., description="Your email for SEC compliance (e.g., 'yourname@domain.com MyApp/1.0')")
    start_date: Optional[str] = Field(None, description="Start date in YYYY-MM-DD format")
    end_date: Optional[str] = Field(None, description="End date in YYYY-MM-DD format")
    required_fields: List[str] = Field(
        default=[
            "Total Revenues",
            "Cost Of Revenues", 
            "Gross Profit",
            "R&D Expenses",
            "Selling General & Admin Expenses",
            "Other Operating Expenses, Total",
            "Operating Income",
            "Interest Expense, Total",
            "Interest And Investment Income",
            "Net Interest Expenses",
            "Other Non Operating Expenses, Total",
            "EBT, Excl. Unusual Items",
            "Income Tax Expense",
            "Net Income to Company",
            "Minority Interest",
            "Net Income",
            "Basic EPS - Continuing Operations",
            "Diluted EPS - Continuing Operations",
            "Basic Weighted Average Shares Outstanding",
            "Diluted Weighted Average Shares Outstanding",
            "Dividend Per Share",
            "EBITDA",
            "EBIT"
        ],
        description="List of required income statement line items"
    )
    output_type: str = Field("quarterly", description="Output type: 'quarterly' or 'ttm'")
    
    @validator('output_type')
    def validate_output_type(cls, v):
        if v not in ['quarterly', 'ttm', 'annual']:
            raise ValueError("output_type must be 'quarterly' or 'ttm' or 'annual'")
        return v
    
    @validator('start_date', 'end_date')
    def validate_date(cls, v):
        if v is not None:
            try:
                datetime.strptime(v, '%Y-%m-%d')
            except ValueError:
                raise ValueError("Date must be in YYYY-MM-DD format")
        return v

