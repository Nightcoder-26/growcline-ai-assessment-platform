"""
Recommendation Service Module
Responsible for:
- Generating personalized learning recommendations based on candidate weak areas
- Providing recommended topics, structured learning paths, difficulty levels, and improvement tips
- Implementing reusable, extensible recommendation engine architecture
- Providing an extensible AI provider interface (ready for Groq LLM integration)

Architecture: Controller -> Service -> Model -> MongoDB
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from bson import ObjectId
from pymongo.errors import PyMongoError

try:
    from config.database import Database
except ImportError:
    from app.config.database import Database

logger = logging.getLogger(__name__)

# Constants for Difficulty Levels
DIFF_BEGINNER = "Beginner"
DIFF_INTERMEDIATE = "Intermediate"
DIFF_ADVANCED = "Advanced"


class IAIRecommendationProvider(ABC):
    """
    Abstract Base Class / Extensible Interface for AI Recommendation Providers.
    Allows seamless transition between heuristic rule engines and LLM providers
    (such as Groq Llama 3 or OpenAI) without refactoring caller services.
    """

    @abstractmethod
    def generate(
        self,
        weak_skills: List[str],
        user_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generates structured learning recommendations.

        Args:
            weak_skills (List[str]): Candidate's identified weak competencies.
            user_profile (Optional[Dict[str, Any]]): Historical performance breakdown.

        Returns:
            Dict[str, Any]: {
                "recommendedTopics": List[str],
                "learningPath": List[Dict[str, str]],
                "difficultyLevel": str,
                "improvementTips": List[str]
            }
        """
        pass


class HeuristicRecommendationEngine(IAIRecommendationProvider):
    """
    Production-grade rule-based recommendation engine.
    Maps technical and aptitude skill areas to curated learning trajectories,
    topic breakdowns, and practical improvement strategies.
    """

    # Knowledge base for topic mapping
    SKILL_KNOWLEDGE_BASE: Dict[str, Dict[str, Any]] = {
        "python": {
            "topics": ["Memory Management & Garbage Collection", "Generators & Iterators", "Concurrency (asyncio/multiprocessing)", "Decorators & Metaclasses", "Data Structures Optimization"],
            "tips": ["Write unit tests using pytest for all core logic.", "Practice LeetCode medium problems using Python dicts and sets.", "Analyze time complexity using Big-O notation."],
            "path": [
                {"step": "Step 1: Core Syntax & Idioms", "duration": "1 Week", "action": "Master Pythonic constructs, list comprehensions, and built-in functions."},
                {"step": "Step 2: Advanced Data Structures", "duration": "2 Weeks", "action": "Implement custom collections and explore collections/itertools modules."},
                {"step": "Step 3: Concurrency & Performance", "duration": "1 Week", "action": "Build asynchronous I/O pipelines and profile memory usage."}
            ]
        },
        "algorithms": {
            "topics": ["Dynamic Programming & Memoization", "Graph Traversals (BFS/DFS/Dijkstra)", "Sliding Window & Two Pointers", "Divide and Conquer", "Greedy Algorithms"],
            "tips": ["Draw recursion trees before coding dynamic programming solutions.", "Identify problem invariants early.", "Practice coding without an IDE to simulate whiteboard interviews."],
            "path": [
                {"step": "Step 1: Pattern Recognition", "duration": "2 Weeks", "action": "Categorize algorithmic problems by underlying patterns (e.g., Two Pointers)."},
                {"step": "Step 2: Graph & Tree Algorithms", "duration": "2 Weeks", "action": "Implement graph representations and shortest path algorithms from scratch."},
                {"step": "Step 3: Dynamic Programming Mastery", "duration": "2 Weeks", "action": "Solve classic 1D and 2D DP problems using bottom-up tabulation."}
            ]
        },
        "system design": {
            "topics": ["Horizontal vs Vertical Scaling", "Load Balancing & Caching Strategies", "Database Sharding & Replication", "Microservices & Event-Driven Architecture", "CAP Theorem & Eventual Consistency"],
            "tips": ["Always start system design interviews by clarifying functional and non-functional requirements.", "Calculate back-of-the-envelope estimations for QPS and storage.", "Understand the trade-offs between SQL and NoSQL databases."],
            "path": [
                {"step": "Step 1: Foundational Building Blocks", "duration": "1 Week", "action": "Study DNS, Load Balancers, Proxies, and Caching layers."},
                {"step": "Step 2: Database Architecture", "duration": "2 Weeks", "action": "Explore ACID transactions, distributed consensus, and replication."},
                {"step": "Step 3: End-to-End Case Studies", "duration": "2 Weeks", "action": "Design architectures for large-scale platforms (e.g., URL shortener, Chat app)."}
            ]
        },
        "sql": {
            "topics": ["Complex Joins & Subqueries", "Window Functions (ROW_NUMBER, RANK)", "Query Optimization & Indexing", "ACID Transactions & Isolation Levels", "Stored Procedures & Triggers"],
            "tips": ["Use EXPLAIN ANALYZE to inspect query execution plans.", "Avoid SELECT * in production queries; request only necessary columns.", "Index foreign keys and frequently filtered columns."],
            "path": [
                {"step": "Step 1: Advanced Relational Queries", "duration": "1 Week", "action": "Master multi-table JOINs, GROUP BY aggregations, and HAVING clauses."},
                {"step": "Step 2: Analytical Window Functions", "duration": "1 Week", "action": "Practice ranking, running totals, and moving averages."},
                {"step": "Step 3: Performance Tuning", "duration": "1 Week", "action": "Analyze B-Tree indexes, composite indexing, and deadlock avoidance."}
            ]
        },
        "general aptitude": {
            "topics": ["Quantitative Aptitude (Time, Speed, Work)", "Logical Reasoning & Deductive Logic", "Data Interpretation & Chart Analysis", "Verbal Reasoning & Comprehension", "Probability & Permutations"],
            "tips": ["Practice mental math and percentage fractions to increase calculation speed.", "Use elimination techniques in multiple-choice reasoning questions.", "Read data charts carefully before jumping into calculations."],
            "path": [
                {"step": "Step 1: Quantitative Speed Math", "duration": "1 Week", "action": "Review foundational arithmetic, percentages, and ratios."},
                {"step": "Step 2: Analytical Reasoning", "duration": "1 Week", "action": "Solve seating arrangement, syllogism, and blood relation puzzles."},
                {"step": "Step 3: Timed Mock Drills", "duration": "1 Week", "action": "Take full-length timed aptitude tests under simulated exam pressure."}
            ]
        }
    }

    def generate(
        self,
        weak_skills: List[str],
        user_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Synthesizes structured recommendations from candidate's weakest competencies.
        """
        if not weak_skills:
            return {
                "recommendedTopics": ["Advanced System Architecture", "High-Performance Computing", "Leadership & Communication"],
                "learningPath": [
                    {"step": "Milestone 1: Continuous Practice", "duration": "Ongoing", "action": "Maintain high competency through weekly coding challenges."},
                    {"step": "Milestone 2: Open Source Contributions", "duration": "Ongoing", "action": "Contribute to large-scale production codebases."}
                ],
                "difficultyLevel": DIFF_ADVANCED,
                "improvementTips": [
                    "You demonstrated excellent mastery across assessed areas!",
                    "Focus on time optimization and mentoring junior peers.",
                    "Explore architectural design patterns and distributed system reliability."
                ]
            }

        topics_set = set()
        tips_list = []
        path_list = []

        # Determine difficulty level based on profile score if available
        diff_level = DIFF_INTERMEDIATE
        if user_profile and isinstance(user_profile, dict):
            avg_pct = float(user_profile.get("percentage") or user_profile.get("average_score", 50.0))
            if avg_pct < 35.0:
                diff_level = DIFF_BEGINNER
            elif avg_pct >= 70.0:
                diff_level = DIFF_ADVANCED

        for skill in weak_skills:
            clean_skill = skill.lower().strip()
            # Match against knowledge base (exact or substring)
            matched = False
            for kb_key, kb_data in self.SKILL_KNOWLEDGE_BASE.items():
                if kb_key in clean_skill or clean_skill in kb_key:
                    matched = True
                    for topic in kb_data["topics"]:
                        topics_set.add(topic)
                    for tip in kb_data["tips"]:
                        if tip not in tips_list:
                            tips_list.append(tip)
                    for step_item in kb_data["path"]:
                        if step_item not in path_list:
                            path_list.append(step_item)
                    break

            if not matched and clean_skill and clean_skill != "none":
                # Fallback for dynamic/unlisted technical skills
                formatted_name = skill.capitalize()
                topics_set.add(f"Core Fundamentals of {formatted_name}")
                topics_set.add(f"Advanced Problem Solving in {formatted_name}")
                topics_set.add(f"Best Practices & Design Patterns for {formatted_name}")
                tips_list.append(f"Review official documentation and standard style guides for {formatted_name}.")
                tips_list.append(f"Build a miniature project focusing specifically on {formatted_name} architecture.")
                path_list.append({
                    "step": f"Step 1: {formatted_name} Foundations",
                    "duration": "1 Week",
                    "action": f"Study core syntax, data types, and standard libraries of {formatted_name}."
                })
                path_list.append({
                    "step": f"Step 2: {formatted_name} Applied Practice",
                    "duration": "2 Weeks",
                    "action": f"Solve real-world debugging and implementation exercises in {formatted_name}."
                })

        return {
            "recommendedTopics": sorted(list(topics_set))[:8],
            "learningPath": path_list[:5],
            "difficultyLevel": diff_level,
            "improvementTips": tips_list[:6]
        }


class GroqLLMRecommendationEngine(IAIRecommendationProvider):
    """
    Extensible Interface / Adapter for Groq AI (Llama 3 / Mixtral) recommendation generation.
    NOTE: As per project requirements ('Do NOT call Groq yet. Only implement reusable recommendation engine'),
    this class formats the LLM prompt and structure without executing live API network calls,
    falling back seamlessly to the heuristic engine while maintaining full readiness for future activation.
    """

    def generate(
        self,
        weak_skills: List[str],
        user_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Prepares LLM prompt payload and delegates to heuristic fallback until Groq API key is enabled.
        When activating Groq: replace fallback call below with groq_client.chat.completions.create(...).
        """
        logger.info("GroqLLMRecommendationEngine invoked. Constructing prompt schema for LLM.")
        prompt_payload = {
            "model": "llama3-70b-8192",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert AI technical career coach. Generate JSON recommendation plans."
                },
                {
                    "role": "user",
                    "content": f"Candidate weak areas: {', '.join(weak_skills)}. Provide Recommended Topics, Learning Path, Difficulty Level, and Improvement Tips."
                }
            ],
            "temperature": 0.4
        }
        logger.debug(f"Prepared Groq LLM payload structure: {prompt_payload['model']}")

        # Fallback to Heuristic Engine until Groq live calls are activated
        return HeuristicRecommendationEngine().generate(weak_skills, user_profile)


class RecommendationService:
    """
    Service class responsible for generating AI recommendations, learning paths,
    and actionable feedback based on candidate evaluation telemetry.
    """

    @staticmethod
    def get_provider(provider_type: str = "heuristic") -> IAIRecommendationProvider:
        """
        Factory method to obtain configured recommendation provider.

        Args:
            provider_type (str): Provider ID ('heuristic', 'groq').

        Returns:
            IAIRecommendationProvider: Configured engine instance.
        """
        if provider_type.lower() == "groq":
            return GroqLLMRecommendationEngine()
        return HeuristicRecommendationEngine()

    @classmethod
    def generate_recommendations(
        cls,
        weak_skills: List[str],
        user_profile: Optional[Dict[str, Any]] = None,
        provider_type: str = "heuristic"
    ) -> Dict[str, Any]:
        """
        Generates structured recommendations for a given set of weak competencies.

        Args:
            weak_skills (List[str]): List of skill/category names.
            user_profile (Optional[Dict[str, Any]]): Candidate analytical context.
            provider_type (str): Engine selector ('heuristic' or 'groq').

        Returns:
            Dict[str, Any]: Standardized API response containing recommendations.
        """
        try:
            clean_skills = [str(s).strip() for s in weak_skills if s and str(s).strip() != "" and str(s).strip() != "None"]
            provider = cls.get_provider(provider_type)
            rec_result = provider.generate(clean_skills, user_profile)

            return {
                "success": True,
                "status_code": 200,
                "message": "AI recommendations generated successfully.",
                "data": rec_result
            }

        except Exception as err:
            logger.critical(f"Error generating recommendations: {str(err)}", exc_info=True)
            return {
                "success": False,
                "status_code": 500,
                "message": "Internal server error generating recommendations.",
                "error": "INTERNAL_SERVER_ERROR"
            }

    @classmethod
    def generate_recommendations_for_user(
        cls,
        user_id: str,
        weak_skills: Optional[List[str]] = None,
        provider_type: str = "heuristic"
    ) -> Dict[str, Any]:
        """
        Retrieves user's historical performance from MongoDB and generates customized learning paths.

        Args:
            user_id (str): User ObjectId string.
            weak_skills (Optional[List[str]]): Optional override for weak skills list.
            provider_type (str): Engine selector.

        Returns:
            Dict[str, Any]: Standardized API response with tailored study plan.
        """
        try:
            if not ObjectId.is_valid(user_id):
                return {"success": False, "status_code": 400, "message": "Invalid user ID.", "error": "INVALID_OBJECT_ID"}

            target_skills = list(weak_skills) if weak_skills is not None else []
            user_profile: Dict[str, Any] = {"userId": user_id}

            if not target_skills:
                try:
                    db = Database.get_db()
                    # Check latest analytics record
                    latest_analytics = db.analytics.find_one(
                        {"userId": ObjectId(user_id)},
                        sort=[("createdAt", -1)]
                    )

                    if latest_analytics:
                        weak_val = str(latest_analytics.get("weakestSkill", "")).strip()
                        if weak_val and weak_val != "None" and weak_val != "General":
                            target_skills.append(weak_val)
                        user_profile["percentage"] = latest_analytics.get("percentage", 50.0)
                    else:
                        # Fallback check in assessment_results
                        latest_res = db.assessment_results.find_one(
                            {"userId": ObjectId(user_id)},
                            sort=[("createdAt", -1)]
                        )
                        if latest_res:
                            weak_val = str(latest_res.get("weakestSkill", "")).strip()
                            if weak_val and weak_val != "None" and weak_val != "General":
                                target_skills.append(weak_val)
                            user_profile["percentage"] = latest_res.get("percentage", 50.0)
                except PyMongoError as db_err:
                    logger.warning(f"Could not fetch historical profile for user {user_id}: {str(db_err)}")

            return cls.generate_recommendations(target_skills, user_profile, provider_type=provider_type)

        except Exception as err:
            logger.critical(f"Error in generate_recommendations_for_user: {str(err)}", exc_info=True)
            return {"success": False, "status_code": 500, "message": "Internal server error.", "error": "INTERNAL_SERVER_ERROR"}
