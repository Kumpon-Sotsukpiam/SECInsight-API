# -*- coding: utf-8 -*-
from pydantic import BaseModel
from typing import List

class IncomeStatementResponse(BaseModel):
    cik: str
    company_name: str
    output_type: str
    data: dict
    periods: List[str]
    message: str = "Success"

