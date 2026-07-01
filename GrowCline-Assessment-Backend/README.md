# GrowCline AI Assessment Platform - Backend

Backend service for the **GrowCline AI Assessment & Interview Intelligence Platform**.

This backend is responsible for managing user authentication, assessments, question banks, result calculation, analytics, and AI-powered recommendations.

> **Current Status:** Project setup completed. Development is in progress.

## 🚀 Tech Stack

- Python
- Flask
- MongoDB Atlas
- PyMongo
- JWT Authentication
- Flask-CORS
- Python Dotenv
- Google Gemini API (Planned)


GrowCline-Assessment-Backend/

├── app/
│   ├── __init__.py
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   └── settings.py
│   │
│   ├── controllers/
│   │   ├── __init__.py
│   │   ├── auth_controller.py
│   │   ├── aptitude_controller.py
│   │   ├── technical_controller.py
│   │   ├── coding_controller.py
│   │   ├── assessment_controller.py
│   │   ├── result_controller.py
│   │   └── analytics_controller.py
│   │
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── auth_middleware.py
│   │   ├── validation.py
│   │   └── error_handler.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user_model.py
│   │   ├── aptitude_question_model.py
│   │   ├── technical_question_model.py
│   │   ├── coding_question_model.py
│   │   ├── assessment_model.py
│   │   ├── assessment_result_model.py
│   │   └── analytics_model.py
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth_routes.py
│   │   ├── aptitude_routes.py
│   │   ├── technical_routes.py
│   │   ├── coding_routes.py
│   │   ├── assessment_routes.py
│   │   ├── result_routes.py
│   │   └── analytics_routes.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user_schema.py
│   │   ├── aptitude_schema.py
│   │   ├── technical_schema.py
│   │   ├── coding_schema.py
│   │   ├── assessment_schema.py
│   │   ├── result_schema.py
│   │   └── analytics_schema.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── assessment_service.py
│   │   ├── question_service.py
│   │   ├── scoring_service.py
│   │   ├── analytics_service.py
│   │   ├── recommendation_service.py
│   │   └── coding_service.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── constants.py
│       ├── helpers.py
│       ├── jwt_utils.py
│       ├── password_utils.py
│       └── validators.py
│
├── uploads/
│
└── tests/
    ├── test_auth.py
    ├── test_assessment.py
    ├── test_result.py
    └── test_analytics.py
    │
    ├── app.py
    ├── requirements.txt
    ├── .env
    ├── .gitignore
    ├── README.md
    │