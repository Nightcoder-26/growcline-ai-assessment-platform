"""
GrowCline AI Assessment & Interview Intelligence Platform
Services Layer Exports

Architecture: Controller -> Service -> Model -> MongoDB
Controllers call ONLY Services. Services handle ALL business logic.
"""

from .question_service import (
    QuestionService,
    QUESTION_TYPE_APTITUDE,
    QUESTION_TYPE_TECHNICAL,
    QUESTION_TYPE_CODING
)
from .coding_service import (
    CodingService,
    ICodeExecutionEngine,
    LocalPythonExecutionEngine,
    DockerExecutionEngine
)
from .scoring_service import ScoringService
from .analytics_service import AnalyticsService
from .recommendation_service import (
    RecommendationService,
    IAIRecommendationProvider,
    HeuristicRecommendationEngine,
    GroqLLMRecommendationEngine
)
from .assessment_service import AssessmentService

__all__ = [
    "QuestionService",
    "QUESTION_TYPE_APTITUDE",
    "QUESTION_TYPE_TECHNICAL",
    "QUESTION_TYPE_CODING",
    "CodingService",
    "ICodeExecutionEngine",
    "LocalPythonExecutionEngine",
    "DockerExecutionEngine",
    "ScoringService",
    "AnalyticsService",
    "RecommendationService",
    "IAIRecommendationProvider",
    "HeuristicRecommendationEngine",
    "GroqLLMRecommendationEngine",
    "AssessmentService"
]
