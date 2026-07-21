# GrowCline Assessment Backend

FastAPI backend powering the GrowCline AI Interview & Assessment Platform.

## Quick Start

```bash
# 1. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate       # macOS/Linux
# .venv\Scripts\activate        # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment variables
cp .env.example .env    # Edit .env with your credentials

# 4. Run the server
python app.py
```

Server starts at **http://localhost:5001**

## Environment Variables

```env
MONGO_URI=mongodb://localhost:27017/growcline
JWT_SECRET=your_jwt_secret
GEMINI_API_KEY=your_google_gemini_key
GROQ_API_KEY=your_groq_key
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_S3_BUCKET=your_bucket_name
HOST=0.0.0.0
PORT=5001
```

## Key Modules

| Module | Route Prefix | Description |
|---|---|---|
| Proctoring | `/api/proctoring/` | Real-time event logging & summaries |
| Cheating Detection | `/api/interview/cheating/` | Risk score calculation |
| Interview Analytics | `/api/interview-analytics/` | Full analytics & integrity report |
| Interview Session | `/api/interview/` | Unified session lifecycle |
| Interviews | `/api/interviews/` | AI question generation & evaluation |
| Recording | `/api/recording/` | Video upload to S3 |
| Auth | `/api/auth/` | JWT login & registration |

## Architecture

```
app/
├── config/          # DB connection, settings
├── models/          # MongoDB document models
├── schemas/         # Pydantic v2 schemas
├── controllers/     # Route handlers
├── services/        # Business logic
├── routes/          # FastAPI routers
├── middleware/       # Auth middleware
└── utils/           # Shared helpers
```

## API Documentation

Interactive Swagger docs available at: **http://localhost:5001/docs**
