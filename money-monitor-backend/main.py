"""
Money Monitor - FastAPI Backend
Handles all business logic, AI queries, and Firestore integration
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import firebase_admin
from firebase_admin import credentials, firestore, auth
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Money Monitor API",
    description="Expense tracking backend with AI support",
    version="1.0.0"
)

# Enable CORS for Flutter app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Firebase
firebase_config_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase-credentials.json")
if not firebase_admin._apps:

    cred = credentials.Certificate(firebase_config_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ============================================================================
# DATA MODELS
# ============================================================================

class Expense(BaseModel):
    item: str
    amount: float
    type: str  # "personal" or "business"
    category: str
    note: str = ""
    source: str = "manual"  # "manual" or "sms"

class Company(BaseModel):
    name: str
    subscriptionStatus: str = "free"  # free, trial, active

class CompanyUser(BaseModel):
    userId: str
    role: str  # "owner", "manager", "employee"

class MerchantQuery(BaseModel):
    merchant: str
    userId: Optional[str] = None
    companyId: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None

class NLQuestion(BaseModel):
    question: str
    userId: Optional[str] = None
    companyId: Optional[str] = None

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "service": "Money Monitor API",
        "version": "1.0.0"
    }

# ============================================================================
# EXPENSE ENDPOINTS
# ============================================================================

@app.post("/expenses/add")
async def add_expense(userId: str, expense: Expense):
    """
    Add a new expense to Firestore
    
    Example:
    {
        "item": "petrol",
        "amount": 100.00,
        "type": "personal",
        "category": "consumable",
        "note": "filled tank",
        "source": "manual"
    }
    """
    try:
        expense_data = {
            **expense.dict(),
            "date": datetime.now().isoformat(),
            "createdAt": firestore.SERVER_TIMESTAMP,
            "userId": userId
        }
        
        ref = db.collection('users').document(userId).collection('expenses')
        doc = ref.add(expense_data)
        
        return {
            "success": True,
            "message": "Expense added successfully",
            "expenseId": doc[1].id
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/expenses/{userId}")
async def get_expenses(userId: str, type: Optional[str] = None):
    """
    Get all expenses for a user
    
    Query params:
    - type: "personal" or "business" (optional)
    """
    try:
        ref = db.collection('users').document(userId).collection('expenses')
        query = ref.order_by('date', direction=firestore.Query.DESCENDING)
        
        if type:
            query = query.where('type', '==', type)
        
        docs = query.stream()
        expenses = []
        
        for doc in docs:
            expense_data = doc.to_dict()
            expense_data['id'] = doc.id
            expenses.append(expense_data)
        
        return {
            "success": True,
            "count": len(expenses),
            "expenses": expenses
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/expenses/totals/{userId}")
async def get_expense_totals(userId: str):
    """
    Get total expenses by type (personal vs business)
    """
    try:
        ref = db.collection('users').document(userId).collection('expenses')
        docs = ref.stream()
        
        totals = {
            "total": 0,
            "personal": 0,
            "business": 0
        }
        
        for doc in docs:
            expense = doc.to_dict()
            amount = expense.get('amount', 0)
            totals['total'] += amount
            
            if expense.get('type') == 'personal':
                totals['personal'] += amount
            elif expense.get('type') == 'business':
                totals['business'] += amount
        
        return {
            "success": True,
            "userId": userId,
            "totals": totals
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============================================================================
# AI QUERY ENDPOINTS
# ============================================================================

@app.post("/ai/merchant-spend")
async def merchant_spend(query: MerchantQuery):
    """
    Query: "From this merchant how much have I spent?"
    
    Returns: Total amount, count, and breakdown by category
    
    Example request:
    {
        "merchant": "HDFC Bank",
        "userId": "user123",
        "startDate": "2025-01-01",
        "endDate": "2025-12-31"
    }
    """
    try:
        userId = query.userId
        merchant = query.merchant.lower()
        
        # Build query
        ref = db.collection('users').document(userId).collection('expenses')
        docs = ref.where('item', '==', merchant).stream()
        
        total_amount = 0
        count = 0
        categories = {}
        expenses_list = []
        
        for doc in docs:
            expense = doc.to_dict()
            amount = expense.get('amount', 0)
            category = expense.get('category', 'uncategorized')
            
            # Filter by date if provided
            if query.startDate and query.endDate:
                expense_date = expense.get('date', '')
                if expense_date < query.startDate or expense_date > query.endDate:
                    continue
            
            total_amount += amount
            count += 1
            categories[category] = categories.get(category, 0) + amount
            
            expenses_list.append({
                'date': expense.get('date'),
                'amount': amount,
                'category': category,
                'note': expense.get('note', '')
            })
        
        return {
            "success": True,
            "merchant": query.merchant,
            "totalSpent": round(total_amount, 2),
            "transactionCount": count,
            "byCategory": categories,
            "expenses": expenses_list
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/ai/category-summary")
async def category_summary(userId: str, type: Optional[str] = None):
    """
    Get spending breakdown by category
    
    Returns: Total per category, count, percentage
    """
    try:
        ref = db.collection('users').document(userId).collection('expenses')
        docs = ref.stream()
        
        categories = {}
        total = 0
        
        for doc in docs:
            expense = doc.to_dict()
            
            # Filter by type if provided
            if type and expense.get('type') != type:
                continue
            
            category = expense.get('category', 'uncategorized')
            amount = expense.get('amount', 0)
            
            if category not in categories:
                categories[category] = {'total': 0, 'count': 0}
            
            categories[category]['total'] += amount
            categories[category]['count'] += 1
            total += amount
        
        # Calculate percentages
        for cat in categories:
            cat_total = categories[cat]['total']
            percentage = (cat_total / total * 100) if total > 0 else 0
            categories[cat]['percentage'] = round(percentage, 2)
        
        return {
            "success": True,
            "userId": userId,
            "type": type or "all",
            "totalSpent": round(total, 2),
            "categories": categories
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/ai/monthly-trend")
async def monthly_trend(userId: str, type: Optional[str] = None):
    """
    Get monthly spending trend
    
    Returns: Spending by month for last 12 months
    """
    try:
        ref = db.collection('users').document(userId).collection('expenses')
        docs = ref.stream()
        
        monthly_data = {}
        
        for doc in docs:
            expense = doc.to_dict()
            
            # Filter by type if provided
            if type and expense.get('type') != type:
                continue
            
            date_str = expense.get('date', '')
            if not date_str:
                continue
            
            # Extract year-month
            month_key = date_str[:7]  # "2025-01"
            amount = expense.get('amount', 0)
            
            if month_key not in monthly_data:
                monthly_data[month_key] = {'total': 0, 'count': 0}
            
            monthly_data[month_key]['total'] += amount
            monthly_data[month_key]['count'] += 1
        
        # Sort by month
        sorted_months = sorted(monthly_data.items())
        
        return {
            "success": True,
            "userId": userId,
            "type": type or "all",
            "trend": dict(sorted_months)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============================================================================
# MERCHANT MEMORY ENDPOINTS
# ============================================================================

@app.post("/merchants/save")
async def save_merchant(userId: str, merchant: str, category: str, type: str):
    """
    Save merchant categorization for auto-categorize on future SMS
    
    Example:
    {
        "merchant": "HDFC Bank",
        "category": "banking",
        "type": "business"
    }
    """
    try:
        merchant_data = {
            "normalizedName": merchant.lower(),
            "defaultCategory": category,
            "defaultType": type,
            "userId": userId,
            "createdAt": firestore.SERVER_TIMESTAMP,
            "lastUsed": firestore.SERVER_TIMESTAMP
        }
        
        db.collection('merchants').document(f"{userId}_{merchant.lower()}").set(merchant_data)
        
        return {
            "success": True,
            "message": f"Merchant '{merchant}' saved with category '{category}'"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/merchants/lookup/{userId}/{merchant}")
async def lookup_merchant(userId: str, merchant: str):
    """
    Look up saved merchant categorization
    
    Returns: Category and type if found, null otherwise
    """
    try:
        doc = db.collection('merchants').document(f"{userId}_{merchant.lower()}").get()
        
        if doc.exists:
            data = doc.to_dict()
            return {
                "success": True,
                "found": True,
                "merchant": merchant,
                "category": data.get('defaultCategory'),
                "type": data.get('defaultType')
            }
        else:
            return {
                "success": True,
                "found": False,
                "merchant": merchant
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============================================================================
# COMPANY ENDPOINTS (For Future Use)
# ============================================================================

@app.post("/companies/create")
async def create_company(userId: str, company: Company):
    """
    Create a new company (for business subscriptions)
    """
    try:
        company_data = {
            "name": company.name,
            "ownerUserId": userId,
            "subscriptionStatus": company.subscriptionStatus,
            "createdAt": firestore.SERVER_TIMESTAMP
        }
        
        ref = db.collection('companies').add(company_data)
        
        return {
            "success": True,
            "message": "Company created successfully",
            "companyId": ref[1].id
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/companies/{companyId}/invite-employee")
async def invite_employee(companyId: str, employeeEmail: str, role: str = "employee"):
    """
    Invite an employee to a company
    """
    try:
        # In production, send email invitation
        return {
            "success": True,
            "message": f"Invitation sent to {employeeEmail}",
            "role": role
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============================================================================
# APPROVAL ENDPOINTS (For Future Use)
# ============================================================================

@app.get("/approvals/{userId}")
async def get_pending_approvals(userId: str):
    """
    Get pending expense approvals for manager/owner
    """
    try:
        # Query expenses with status "pending" for this user's company
        return {
            "success": True,
            "userId": userId,
            "pendingCount": 0,
            "approvals": []
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/")
async def root():
    """
    Root endpoint with API documentation
    """
    return {
        "service": "Money Monitor API",
        "version": "1.0.0",
        "endpoints": {
            "health": "GET /health",
            "expenses": {
                "add": "POST /expenses/add",
                "list": "GET /expenses/{userId}",
                "totals": "GET /expenses/totals/{userId}"
            },
            "ai": {
                "merchantSpend": "POST /ai/merchant-spend",
                "categorySummary": "POST /ai/category-summary",
                "monthlyTrend": "POST /ai/monthly-trend"
            },
            "merchants": {
                "save": "POST /merchants/save",
                "lookup": "GET /merchants/lookup/{userId}/{merchant}"
            },
            "companies": {
                "create": "POST /companies/create",
                "inviteEmployee": "POST /companies/{companyId}/invite-employee"
            }
        }
    }

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
