# Money Monitor Python Backend - Setup Guide

## 📋 What This Python Code Does

This FastAPI backend serves as the **brain** of your Money Monitor app:

| Feature | Handles |
|---------|---------|
| **Expense API** | Add, retrieve, and total expenses from Firestore |
| **AI Merchant Query** | "From HDFC Bank, how much have I spent?" → Returns total + breakdown |
| **Category Analytics** | Spending per category with percentages |
| **Monthly Trends** | Shows spending patterns over time |
| **Merchant Memory** | Saves merchant → category mapping for auto-categorization |
| **Company Mgmt** | Create companies, invite employees (for Phase 2) |

---

## 🚀 Step-by-Step Setup

### Step 1: Create Project Folder

```bash
mkdir money-monitor-backend
cd money-monitor-backend
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Get Firebase Credentials

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Select your **Money Monitor** project
3. Go to **Project Settings** → **Service Accounts** tab
4. Click **Generate new private key**
5. Save as `firebase-credentials.json` in your project folder

### Step 5: Create `.env` File

Create `.env` in your project folder:

```
FIREBASE_CREDENTIALS_PATH=firebase-credentials.json
```

### Step 6: Verify Project Structure

```
money-monitor-backend/
├── main.py
├── requirements.txt
├── firebase-credentials.json
├── .env
└── venv/
```

### Step 7: Test the Server

```bash
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### Step 8: Open API Documentation

Visit: **http://127.0.0.1:8000/docs**

You'll see Swagger UI with all endpoints! 🎉

---

## 📡 API Endpoints Reference

### Health Check
```
GET /health
```
**Response:**
```json
{
  "status": "healthy",
  "service": "Money Monitor API",
  "version": "1.0.0"
}
```

---

### Add Expense
```
POST /expenses/add?userId=user123
Body:
{
  "item": "petrol",
  "amount": 100.00,
  "type": "personal",
  "category": "consumable",
  "note": "filled tank",
  "source": "manual"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Expense added successfully",
  "expenseId": "abc123def"
}
```

---

### Get All Expenses
```
GET /expenses/user123?type=personal
```

**Response:**
```json
{
  "success": true,
  "count": 5,
  "expenses": [
    {
      "id": "doc1",
      "item": "petrol",
      "amount": 100.00,
      "type": "personal",
      "category": "consumable",
      "date": "2025-12-03T20:30:00"
    }
  ]
}
```

---

### Get Expense Totals
```
GET /expenses/totals/user123
```

**Response:**
```json
{
  "success": true,
  "userId": "user123",
  "totals": {
    "total": 500.00,
    "personal": 300.00,
    "business": 200.00
  }
}
```

---

### AI: Merchant Spending Query ⭐
```
POST /ai/merchant-spend
Body:
{
  "merchant": "HDFC Bank",
  "userId": "user123",
  "startDate": "2025-01-01",
  "endDate": "2025-12-31"
}
```

**Response:**
```json
{
  "success": true,
  "merchant": "HDFC Bank",
  "totalSpent": 5000.00,
  "transactionCount": 15,
  "byCategory": {
    "banking": 3000.00,
    "fees": 2000.00
  },
  "expenses": [
    {
      "date": "2025-12-03",
      "amount": 500.00,
      "category": "banking",
      "note": "Transfer"
    }
  ]
}
```

---

### AI: Category Summary
```
POST /ai/category-summary?userId=user123&type=personal
```

**Response:**
```json
{
  "success": true,
  "userId": "user123",
  "type": "personal",
  "totalSpent": 1000.00,
  "categories": {
    "food": {
      "total": 400.00,
      "count": 10,
      "percentage": 40.0
    },
    "transport": {
      "total": 300.00,
      "count": 5,
      "percentage": 30.0
    }
  }
}
```

---

### AI: Monthly Trend
```
POST /ai/monthly-trend?userId=user123
```

**Response:**
```json
{
  "success": true,
  "userId": "user123",
  "type": "all",
  "trend": {
    "2025-01": {
      "total": 1500.00,
      "count": 20
    },
    "2025-02": {
      "total": 2000.00,
      "count": 25
    }
  }
}
```

---

### Merchant Memory: Save
```
POST /merchants/save?userId=user123&merchant=HDFC%20Bank&category=banking&type=business
```

**Response:**
```json
{
  "success": true,
  "message": "Merchant 'HDFC Bank' saved with category 'banking'"
}
```

---

### Merchant Memory: Lookup
```
GET /merchants/lookup/user123/HDFC%20Bank
```

**Response (if found):**
```json
{
  "success": true,
  "found": true,
  "merchant": "HDFC Bank",
  "category": "banking",
  "type": "business"
}
```

**Response (if not found):**
```json
{
  "success": true,
  "found": false,
  "merchant": "HDFC Bank"
}
```

---

## 🔌 How to Call from Flutter App

In your Flutter app, add this to `pubspec.yaml`:

```yaml
dependencies:
  http: ^1.1.0
```

Then in your Dart code:

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

const String API_URL = "http://localhost:8000";

// Get merchant spend
Future<void> queryMerchantSpend() async {
  final response = await http.post(
    Uri.parse('$API_URL/ai/merchant-spend'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({
      "merchant": "HDFC Bank",
      "userId": "abdulqadir@aqbco.org",
      "startDate": "2025-01-01",
      "endDate": "2025-12-31"
    }),
  );

  if (response.statusCode == 200) {
    final data = jsonDecode(response.body);
    print("Total spent: Rs. ${data['totalSpent']}");
    print("Transactions: ${data['transactionCount']}");
  }
}

// Get expense totals
Future<void> getExpenseTotals() async {
  final userId = "abdulqadir@aqbco.org";
  final response = await http.get(
    Uri.parse('$API_URL/expenses/totals/$userId'),
  );

  if (response.statusCode == 200) {
    final data = jsonDecode(response.body);
    print("Total: Rs. ${data['totals']['total']}");
    print("Personal: Rs. ${data['totals']['personal']}");
    print("Business: Rs. ${data['totals']['business']}");
  }
}
```

---

## 🧪 Testing with cURL

### Test Health
```bash
curl http://localhost:8000/health
```

### Test Merchant Query
```bash
curl -X POST http://localhost:8000/ai/merchant-spend \
  -H "Content-Type: application/json" \
  -d '{
    "merchant": "petrol",
    "userId": "abdulqadir@aqbco.org"
  }'
```

### Test Category Summary
```bash
curl -X POST "http://localhost:8000/ai/category-summary?userId=abdulqadir@aqbco.org&type=personal"
```

---

## 🚀 Deployment Options

### Option 1: Google Cloud Run (Recommended)
```bash
# Deploy to Cloud Run
gcloud run deploy money-monitor-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Option 2: Railway
1. Push code to GitHub
2. Connect GitHub to Railway
3. Deploy with one click

### Option 3: Heroku
```bash
heroku create money-monitor-api
git push heroku main
```

---

## 📝 Environment Variables for Production

When deploying, set these in your platform:

```
FIREBASE_CREDENTIALS_PATH=/path/to/firebase-credentials.json
```

---

## ✅ Verification Checklist

- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Firebase credentials downloaded and saved
- [ ] `.env` file created with correct path
- [ ] Server starts without errors (`python main.py`)
- [ ] Swagger docs accessible at http://127.0.0.1:8000/docs
- [ ] Health check returns 200 status
- [ ] Merchant query returns correct data

---

## 🔥 What's Next?

**Phase 2 Features to Add:**

1. **SMS Parsing** - Extract merchant + amount from SMS
2. **NLP for Questions** - Parse natural language queries
3. **Approval Workflow** - Manager approval for business expenses
4. **OCR for Receipts** - Extract data from receipt images
5. **Analytics Dashboard** - Charts and reports

---

**Need help?** Check the Swagger docs at `/docs` or test endpoints there! 🚀
