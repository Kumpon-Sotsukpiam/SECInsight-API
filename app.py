# -*- coding: utf-8 -*-
from fastapi import FastAPI, HTTPException
from models.income_statement_request import IncomeStatementRequest
from models.income_statement_response import IncomeStatementResponse
from helper import build_income_statement

app = FastAPI(title="SEC Income Statement API", version="1.0.0")

# ---------- API Endpoints ----------
@app.get("/")
def root():
    """Root endpoint with API information."""
    return {
        "message": "SEC Income Statement API",
        "version": "1.0.0",
        "endpoints": {
            "/income-statement": "POST - Get income statement data",
            "/docs": "GET - API documentation"
        }
    }


@app.post("/income-statement", response_model=IncomeStatementResponse)
async def get_income_statement(request: IncomeStatementRequest):
    """
    Get income statement data from SEC filings.
    
    - **cik**: Company CIK number (e.g., "320193" for Apple)
    - **user_agent**: Your email for SEC compliance
    - **start_date**: Optional start date (YYYY-MM-DD)
    - **end_date**: Optional end date (YYYY-MM-DD)
    - **required_fields**: List of income statement line items to retrieve
    - **output_type**: "quarterly" or "ttm" (trailing twelve months)
    """
    try:
        result = build_income_statement(
            cik=request.cik,
            ua=request.user_agent,
            required_fields=request.required_fields,
            output_type=request.output_type,
            start_date=request.start_date,
            end_date=request.end_date
        )
        
        return IncomeStatementResponse(
            cik=request.cik,
            company_name=result["company_name"],
            output_type=request.output_type,
            data=result["data"],
            periods=result["periods"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)