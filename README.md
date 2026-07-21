# 🚀 GrowCline AI Assessment & Interview Intelligence Platform

A full-stack AI-powered interview and assessment platform with real-time proctoring, cheating detection, and interview analytics.

---

## 📁 Repository Structure

```
intership_june_2026/
├── GrowCline-Assessment-Backend/   # FastAPI backend (Python)
├── GrowCline-Assessment-Frontend/  # Next.js frontend (TypeScript)
├── Anirudh/                        # Team member workspace
├── Subbu/                          # Team member workspace
└── sarang_todo/                    # Team member workspace
```

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| **FastAPI** | REST API framework |
| **Uvicorn** | ASGI server |
| **MongoDB** (PyMongo) | Primary database |
| **Google Gemini AI** | AI-generated interview questions & evaluation |
| **Groq AI** | Fast LLM inference fallback |
| **PyJWT** | JWT authentication |
| **Pydantic v2** | Schema validation |
| **boto3** | AWS S3 video storage |

### Frontend
| Technology | Purpose |
|---|---|
| **Next.js 16** | React framework (App Router) |
| **TypeScript** | Type-safe development |
| **Tailwind CSS v4** | Utility-first styling |
| **Framer Motion** | Animations & transitions |
| **Recharts** | Analytics data visualizations |
| **react-webcam** | Camera access & face detection |
| **react-media-recorder** | Video/audio recording |
| **Lucide React** | Icon library |

---

## ✨ Features

### 🎯 AI Interview System
- Dynamic question generation using Google Gemini AI
- Adaptive difficulty based on job role, interview type (Technical / HR / Aptitude), and difficulty level
- Real-time answer evaluation with AI scoring

### 🎥 Live Video Recording
- Webcam-based video interview recording
- AWS S3 integration for video storage
- Per-question video clips with timestamps

### 🛡️ Real-Time Proctoring
- **Face presence detection** — alerts when candidate leaves frame
- **Tab switch detection** — tracks context switches
- **Fullscreen exit detection** — monitors window focus
- **Microphone violation detection** — detects audio muting
- **Multiple face detection** — flags additional persons on screen
- Live event streaming to backend with batch processing

### 🔍 Cheating Detection Risk Engine
- Deterministic heuristic scoring with weighted event contributions
- Risk levels: `LOW` → `MEDIUM` → `HIGH` → `CRITICAL`
- Real-time risk widget during interview session
- Per-event caps to prevent score inflation from repeated minor events

### 📊 Interview Analytics & Integrity Report
- Overall performance score calculated from AI answer evaluations
- Full proctoring event breakdown with violation counts
- Risk assessment with recommendation (Clear / Review / Flag)
- Auto-polling real-time updates every 8 seconds
- Shareable analytics report per interview session

### 🔐 Authentication
- JWT-based authentication
- Role-based access control (candidate / admin)
- Guest mode for demo testing

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- MongoDB (local or Atlas)
- pnpm (recommended) or npm

---

### Backend Setup

```bash
cd GrowCline-Assessment-Backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env             # fill in your values (see below)

# Run the server
python app.py
```

The backend runs at **http://localhost:5001**

#### Environment Variables (`.env`)

```env
MONGO_URI=mongodb://localhost:27017/growcline
JWT_SECRET=your_jwt_secret_here
GEMINI_API_KEY=your_google_gemini_api_key
GROQ_API_KEY=your_groq_api_key
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_S3_BUCKET=your_s3_bucket_name
HOST=0.0.0.0
PORT=5001
```

---

### Frontend Setup

```bash
cd GrowCline-Assessment-Frontend

# Install dependencies
pnpm install
# or: npm install

# Run development server
pnpm dev
# or: npm run dev
```

The frontend runs at **http://localhost:3000**

---

## 📡 API Overview

| Module | Base Path | Description |
|---|---|---|
| Auth | `/api/auth/` | Login, register, JWT tokens |
| Users | `/api/users/` | User management |
| Interviews | `/api/interviews/` | Create & manage interview sessions |
| Questions | `/api/interviews/:id/question` | AI question generation |
| Proctoring | `/api/proctoring/` | Event logging & summaries |
| Cheating Detection | `/api/interview/cheating/` | Risk scoring |
| Interview Analytics | `/api/interview-analytics/` | Full analytics reports |
| Video Recording | `/api/recording/` | Video upload & retrieval |
| Assessments | `/api/assessments/` | Aptitude & coding assessments |
| Technical | `/api/technical/` | Technical question bank |

---

## 🖥️ Frontend Pages

| Route | Description |
|---|---|
| `/` | Landing / home page |
| `/video-recording` | Main interview session page |
| `/interview-analytics` | Post-interview analytics & integrity report |
| `/cheating-detection` | Cheating detection admin dashboard |
| `/live-proctoring` | Live proctoring monitoring dashboard |

---

## 🏗️ Backend Architecture

```
GrowCline-Assessment-Backend/
├── app.py                    # FastAPI app entrypoint & router registration
├── app/
│   ├── config/              # Database connection & settings
│   ├── models/              # MongoDB document models
│   ├── schemas/             # Pydantic request/response schemas
│   ├── controllers/         # Request handlers
│   ├── services/            # Business logic layer
│   │   ├── cheating_detection_service.py   # Risk scoring engine
│   │   ├── proctoring_service.py           # Event processing
│   │   ├── interview_session_service.py    # Session orchestration
│   │   ├── interview_service.py            # AI question generation
│   │   └── interview_analytics_service.py # Analytics generation
│   ├── routes/              # FastAPI router definitions
│   ├── middleware/          # Auth middleware
│   └── utils/              # Shared utilities
└── requirements.txt
```

---

## 🔄 Proctoring Event Flow

```
Frontend Event Detected
       ↓
Batch POST /api/proctoring/events/batch
       ↓
proctoring_model.py → maps event types to DB schema:
  NO_FACE           → FACE_MISSING
  MICROPHONE_DISABLED → BACKGROUND_VOICE
  FULLSCREEN_EXIT   → WINDOW_MINIMIZED
       ↓
Stored in MongoDB proctoring_logs collection
       ↓
cheating_detection_service.py aggregates event counts
  + normalizes FACE_MISSING → NO_FACE for scoring
       ↓
Risk score calculated (0–100) with weighted heuristics
       ↓
Real-time widget + Analytics report updated
```

---

## 👥 Team

| Member | Work Area |
|---|---|
| **Sarang** | Live Proctoring, Cheating Detection, Interview Analytics, Interview Session |
| **Anirudh** | (see `Anirudh/`) |
| **Subbu** | (see `Subbu/`) |

---

## 📝 License

This project is developed as part of the GrowCline internship programme (June 2026).
