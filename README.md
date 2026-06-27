# NexAltis Lead & Query Management System

**Candidate:** Shubh Bhanushali  
**Role Track:** Backend Development & Client Success Associate  
**Organization:** NexAltis Technologies LLP

A lightweight backend API built with **FastAPI** and **SQLite** to manage customer inquiries, track leads, and monitor follow-ups.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Database Schema](#database-schema)
- [ER Diagram](#er-diagram)
- [API Documentation](#api-documentation)
- [Example Usage](#example-usage)
- [Bonus Features](#bonus-features)

---

## Features

| Feature | Description |
|---------|-------------|
| Lead Registration | Add new leads with contact and service details |
| Query Management | Store and track customer queries |
| Status Tracking | Update lead/query status through the pipeline |
| Lead Listing | `GET /leads` with lead info, service, and status |
| Search | Filter leads by name, company, or service |
| Meeting Scheduler | Schedule meetings with date and time (Bonus L1) |
| Email Notifications | Notify on status changes (Bonus L2) |
| Lead Analytics | Conversion metrics and breakdowns (Bonus L3) |
| Lead Scoring | Assign Hot/Warm/Cold priority based on lead and query signals |
| Query Categorization | Categorize queries using built-in NLP rules or optional LLM |
| AI Query Summary | Generate short summaries for customer queries |
| Response Suggestions | Suggest customer success follow-up responses |
| Intent Detection | Detect pricing, meeting, purchase, support, or information intent |
| LLM Integration | Optional Ollama, Gemini, or OpenAI integration through `.env` |

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend Framework | FastAPI |
| Database | SQLite |
| ORM | SQLAlchemy 2.x |
| Validation | Pydantic v2 |
| Server | Uvicorn |

---

## Project Structure

```
nexaltistech/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── database.py          # Database engine & session
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── routers/
│   │   ├── leads.py         # Lead CRUD & search endpoints
│   │   ├── queries.py       # Query management endpoints
│   │   ├── analytics.py     # Analytics endpoint
│   │   └── ai.py            # AI assistant endpoints
│   └── services/
│       ├── email_service.py # Email notification service
│       └── ai_service.py    # NLP, scoring, and optional LLM service
├── requirements.txt
├── .env.example
└── README.md
```

---

## Setup & Installation

### Prerequisites

- Python 3.10 or higher
- pip

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/bhanushalishubh17-alt/nexaltis-lead-query-management.git
cd nexaltis-lead-query-management

# 2. Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) Configure email notifications
copy .env.example .env   # Windows
# cp .env.example .env   # macOS/Linux
# Edit .env with your SMTP or optional AI provider credentials

# 5. Run the server
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at:

- **Base URL:** http://localhost:8000
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## Database Schema

### `leads` Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Auto-increment lead ID |
| name | VARCHAR(255) | NOT NULL | Customer name |
| email | VARCHAR(255) | NOT NULL | Customer email |
| phone | VARCHAR(50) | NOT NULL | Phone number |
| company_name | VARCHAR(255) | NOT NULL | Company name |
| interested_service | ENUM | NOT NULL | Service of interest |
| status | ENUM | NOT NULL, DEFAULT 'New' | Current pipeline status |
| lead_score | INTEGER | NOT NULL, DEFAULT 0 | AI/rule-based lead score from 0-100 |
| priority | VARCHAR(50) | NOT NULL, DEFAULT 'Cold' | Lead priority: Cold, Warm, or Hot |
| meeting_date | DATE | NULLABLE | Scheduled meeting date |
| meeting_time | TIME | NULLABLE | Scheduled meeting time |
| created_at | DATETIME | NOT NULL | Record creation timestamp |
| updated_at | DATETIME | NOT NULL | Last update timestamp |

### `queries` Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Query ID |
| lead_id | INTEGER | FK → leads.id, NULLABLE | Optional linked lead |
| customer_name | VARCHAR(255) | NOT NULL | Customer name |
| description | TEXT | NOT NULL | Query description |
| query_date | DATETIME | NOT NULL | Date of query |
| status | ENUM | NOT NULL, DEFAULT 'New' | Query status |
| category | VARCHAR(100) | NULLABLE | Detected query category/service area |
| intent | VARCHAR(100) | NULLABLE | Detected customer intent |
| summary | TEXT | NULLABLE | AI/rule-based query summary |
| suggested_response | TEXT | NULLABLE | Suggested follow-up response |
| ai_provider | VARCHAR(50) | NOT NULL, DEFAULT 'rule_based' | Analysis provider used |

### Enums

**Interested Service:** `AI Chatbot`, `Website Development`, `Mobile App Development`, `Data Analytics`

**Status:** `New`, `Contacted`, `Meeting Scheduled`, `Proposal Sent`, `Converted`, `Closed`

---

## ER Diagram

```
┌─────────────────────────────────────────────────────────┐
│                         LEAD                            │
├─────────────────────────────────────────────────────────┤
│ PK  id                                                  │
│     name                                                │
│     email                                               │
│     phone                                               │
│     company_name                                        │
│     interested_service                                  │
│     status  ──────────────────────────────┐             │
│     lead_score                            │             │
│     priority                              │             │
│     meeting_date                          │             │
│     meeting_time                          │             │
│     created_at                            │             │
│     updated_at                            │             │
└──────────────────────┬──────────────────┘             │
                       │ 1                                │
                       │                                  │
                       │ N                                │
┌──────────────────────▼──────────────────┐             │
│                  QUERY                   │             │
├─────────────────────────────────────────┤             │
│ PK  id                                   │             │
│ FK  lead_id  ────────────────────────────┘             │
│     customer_name                                        │
│     description                                          │
│     query_date                                           │
│     status  ─────────────────────────────────────────────┘
│     category                                             │
│     intent                                               │
│     summary                                              │
│     suggested_response                                   │
│     ai_provider                                          │
└─────────────────────────────────────────────────────────┘

Relationship: One Lead → Many Queries (optional link)
Status: Shared enum applied to both Lead and Query records
```

---

## API Documentation

### Health

#### `GET /`
Returns API info and documentation links.

**Response:**
```json
{
  "message": "NexAltis Lead & Query Management System",
  "docs": "/docs",
  "version": "1.0.0"
}
```

#### `GET /health`
Health check endpoint.

---

### Leads

#### `POST /leads` — Register a New Lead

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+91-9876543210",
  "company_name": "Acme Corp",
  "interested_service": "AI Chatbot"
}
```

**Response (201):**
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+91-9876543210",
  "company_name": "Acme Corp",
  "interested_service": "AI Chatbot",
  "status": "New",
  "lead_score": 40,
  "priority": "Cold",
  "meeting_date": null,
  "meeting_time": null,
  "created_at": "2026-06-24T10:00:00",
  "updated_at": "2026-06-24T10:00:00"
}
```

#### `GET /leads` — List Leads (with Search)

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| name | string | Partial match on lead name |
| company | string | Partial match on company name |
| service | enum | Exact match on interested service |

**Example:** `GET /leads?name=John&service=AI%20Chatbot`

**Response:**
```json
{
  "total": 1,
  "leads": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "+91-9876543210",
      "company_name": "Acme Corp",
      "interested_service": "AI Chatbot",
      "status": "New",
      "lead_score": 40,
      "priority": "Cold",
      "meeting_date": null,
      "meeting_time": null,
      "created_at": "2026-06-24T10:00:00",
      "updated_at": "2026-06-24T10:00:00"
    }
  ]
}
```

#### `GET /leads/{lead_id}` — Get Lead by ID

#### `PATCH /leads/{lead_id}/status` — Update Lead Status

**Request Body:**
```json
{
  "status": "Contacted"
}
```

Valid statuses: `New`, `Contacted`, `Meeting Scheduled`, `Proposal Sent`, `Converted`, `Closed`

#### `PATCH /leads/{lead_id}/meeting` — Schedule Meeting (Bonus L1)

**Request Body:**
```json
{
  "meeting_date": "2026-07-01",
  "meeting_time": "14:30:00"
}
```

Automatically sets lead status to `Meeting Scheduled`.

---

### Queries

#### `POST /queries` — Create a Query

**Request Body:**
```json
{
  "customer_name": "John Doe",
  "description": "We need an AI chatbot for our business.",
  "lead_id": 1
}
```

`lead_id` is optional. If provided, the query is linked to an existing lead.

**Response (201):**
```json
{
  "id": 1,
  "lead_id": 1,
  "customer_name": "John Doe",
  "description": "We need an AI chatbot for our business.",
  "query_date": "2026-06-24T10:05:00",
  "status": "New",
  "category": "AI Chatbot",
  "intent": "Purchase Intent",
  "summary": "We need an AI chatbot for our business.",
  "suggested_response": "Hi John Doe, thanks for sharing your requirement. NexAltis can help with AI Chatbot. Could you share your goals, timeline, and any existing systems we should integrate with?",
  "ai_provider": "rule_based"
}
```

#### `GET /queries` — List Queries

**Query Parameters:** `customer_name`, `status`

#### `GET /queries/{query_id}` — Get Query by ID

#### `PATCH /queries/{query_id}/status` — Update Query Status

**Request Body:**
```json
{
  "status": "Proposal Sent"
}
```

If the query is linked to a lead, the lead status is synced and an email notification is sent.

---

### Analytics (Bonus L3)

#### `GET /analytics` — Lead Analytics

**Response:**
```json
{
  "total_leads": 10,
  "converted_leads": 3,
  "conversion_rate": 30.0,
  "leads_by_status": {
    "New": 2,
    "Contacted": 3,
    "Meeting Scheduled": 1,
    "Proposal Sent": 1,
    "Converted": 3,
    "Closed": 0
  },
  "leads_by_service": {
    "AI Chatbot": 4,
    "Website Development": 3,
    "Mobile App Development": 2,
    "Data Analytics": 1
  }
}
```

---

### AI Assistant Features

These features work without an API key by default using local rule-based NLP. Optional providers can be enabled through `.env`:

```env
AI_PROVIDER=rule_based

# Free local LLM option if Ollama is installed and running
AI_PROVIDER=ollama
OLLAMA_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=llama3.2

# Optional hosted providers; add your own key only if needed
GEMINI_API_KEY=
OPENAI_API_KEY=
```

#### `POST /ai/analyze-query` — Analyze Raw Query Text

**Request Body:**
```json
{
  "customer_name": "John Doe",
  "description": "We urgently need pricing for an AI chatbot for our business.",
  "service": "AI Chatbot"
}
```

**Response:**
```json
{
  "category": "AI Chatbot",
  "intent": "Pricing Inquiry",
  "summary": "We urgently need pricing for an AI chatbot for our business.",
  "suggested_response": "Hi John Doe, thanks for your interest in AI Chatbot. We can share a tailored proposal after understanding your requirements, expected timeline, and budget range.",
  "lead_score": 90,
  "priority": "Hot",
  "ai_provider": "rule_based"
}
```

#### `POST /ai/queries/{query_id}/analyze` — Re-analyze Stored Query

Re-runs categorization, intent detection, summarization, and response suggestion for a saved query.

#### `POST /ai/leads/{lead_id}/score` — Recalculate Lead Score

Recalculates lead score and priority from lead status, meeting data, service interest, and linked query descriptions.

AI-generated fields also appear in normal `GET /queries` and `GET /leads` responses.

---

## Example Usage

```bash
# Create a lead
curl -X POST http://localhost:8000/leads \
  -H "Content-Type: application/json" \
  -d '{"name":"Jane Smith","email":"jane@tech.com","phone":"9876543210","company_name":"Tech Solutions","interested_service":"Website Development"}'

# List all leads
curl http://localhost:8000/leads

# Search leads by company
curl "http://localhost:8000/leads?company=Tech"

# Update lead status
curl -X PATCH http://localhost:8000/leads/1/status \
  -H "Content-Type: application/json" \
  -d '{"status":"Contacted"}'

# Schedule a meeting
curl -X PATCH http://localhost:8000/leads/1/meeting \
  -H "Content-Type: application/json" \
  -d '{"meeting_date":"2026-07-05","meeting_time":"10:00:00"}'

# Create a query
curl -X POST http://localhost:8000/queries \
  -H "Content-Type: application/json" \
  -d '{"customer_name":"Jane Smith","description":"We need a modern website redesign.","lead_id":1}'

# Get analytics
curl http://localhost:8000/analytics
```

---

## Bonus Features

### Level 1 — Meeting Scheduler
Use `PATCH /leads/{id}/meeting` to set `meeting_date` and `meeting_time`. Status is automatically updated to `Meeting Scheduled`.

### Level 2 — Email Notification
When a lead or linked query status changes, an email is sent to the lead's email address. Configure SMTP settings in `.env`:

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
NOTIFICATION_FROM=your-email@gmail.com
```

If SMTP is not configured, notifications are logged to the console.

### Level 3 — Lead Analytics
Use `GET /analytics` for total leads, converted count, conversion rate, and breakdowns by status and service.

### Additional AI Features
The system includes lead prioritization/scoring, query categorization, query summarization, automated response suggestions, customer intent detection, and basic LLM integration.

Default mode is `rule_based`, so it is free and needs no API key. For free local LLM usage, install Ollama, run a local model, and set `AI_PROVIDER=ollama`. Gemini/OpenAI are optional and only run when you add your own API key in `.env`.

---

## Author

**Shubh Bhanushali**  
Backend Development & Client Success Associate — NexAltis Technologies LLP Technical Assessment
