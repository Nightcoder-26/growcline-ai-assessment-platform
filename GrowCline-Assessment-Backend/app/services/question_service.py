"""
Question Service Module
Handles all business logic, CRUD operations, random question generation,
filtering, search, pagination, and duplicate validation for:
- Aptitude Questions
- Technical Questions
- Coding Questions

Architecture: Controller -> Service -> Model -> MongoDB
"""

import logging
import re
from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime
from bson import ObjectId
from pymongo.errors import PyMongoError

try:
    from config.database import Database
except ImportError:
    from app.config.database import Database

try:
    from models.aptitude_question_model import AptitudeQuestion
    from models.technical_question_model import TechnicalQuestion
    from models.coding_question_model import CodingQuestion
except ImportError:
    from app.models.aptitude_question_model import AptitudeQuestion
    from app.models.technical_question_model import TechnicalQuestion
    from app.models.coding_question_model import CodingQuestion

# Configure logger for enterprise monitoring
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

# Constants
QUESTION_TYPE_APTITUDE = "aptitude"
QUESTION_TYPE_TECHNICAL = "technical"
QUESTION_TYPE_CODING = "coding"

VALID_QUESTION_TYPES = {
    QUESTION_TYPE_APTITUDE,
    QUESTION_TYPE_TECHNICAL,
    QUESTION_TYPE_CODING
}

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
DEFAULT_DIFFICULTY = "Medium"


class QuestionService:
    """
    Service class responsible for managing assessment questions across categories.
    Implements Object-Oriented principles, comprehensive validation, duplicate checking,
    and scalable MongoDB querying for thousands of concurrent assessments.
    """

    @classmethod
    def _get_db_collection_and_model(cls, question_type: str) -> Tuple[Any, Any, str]:
        """
        Resolves the appropriate MongoDB collection and model based on question type.

        Args:
            question_type (str): The type of question ('aptitude', 'technical', 'coding').

        Returns:
            Tuple[Any, Any, str]: (MongoDB Collection, Model Class, Text Field Name for uniqueness)
        
        Raises:
            ValueError: If the question type is invalid.
        """
        db = Database.get_db()
        q_type = question_type.lower().strip()

        if q_type == QUESTION_TYPE_APTITUDE:
            return db.aptitude_questions, AptitudeQuestion, "question"
        elif q_type == QUESTION_TYPE_TECHNICAL:
            return db.technical_questions, TechnicalQuestion, "question"
        elif q_type == QUESTION_TYPE_CODING:
            return db.coding_questions, CodingQuestion, "problemStatement"
        else:
            logger.error(f"Invalid question type requested: {question_type}")
            raise ValueError(
                f"Invalid question type '{question_type}'. Must be one of: {', '.join(VALID_QUESTION_TYPES)}"
            )

    @classmethod
    def _validate_duplicate(
        cls,
        collection: Any,
        text_field: str,
        text_value: str,
        exclude_id: Optional[str] = None
    ) -> bool:
        """
        Checks if an identical question already exists in the database.
        Uses case-insensitive and whitespace-trimmed matching to prevent near-duplicates.

        Args:
            collection (Any): MongoDB collection instance.
            text_field (str): Field name containing the question text or problem statement.
            text_value (str): The actual text content to validate.
            exclude_id (Optional[str]): Document ID to ignore (useful during updates).

        Returns:
            bool: True if a duplicate exists, False otherwise.
        """
        if not text_value or not isinstance(text_value, str):
            return False

        # Build case-insensitive exact match regex
        trimmed_text = re.escape(text_value.strip())
        query: Dict[str, Any] = {
            text_field: {"$regex": f"^{trimmed_text}$", "$options": "i"}
        }

        if exclude_id and ObjectId.is_valid(exclude_id):
            query["_id"] = {"$ne": ObjectId(exclude_id)}

        try:
            count = collection.count_documents(query, limit=1)
            return count > 0
        except PyMongoError as e:
            logger.error(f"Database error during duplicate check: {str(e)}")
            raise RuntimeError("Database connection error while validating uniqueness.")

    @classmethod
    def create_question(
        cls,
        question_type: str,
        data: Dict[str, Any],
        created_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Creates a new question after validating uniqueness and schema parameters.

        Args:
            question_type (str): Category ('aptitude', 'technical', 'coding').
            data (Dict[str, Any]): Payload containing question attributes.
            created_by (Optional[str]): User ID of the creator/admin.

        Returns:
            Dict[str, Any]: Standardized API response containing newly created question details.
        """
        try:
            collection, model_class, text_field = cls._get_db_collection_and_model(question_type)

            # Validate primary content field
            content = data.get(text_field) or data.get("question") or data.get("problemStatement")
            if not content:
                return {
                    "success": False,
                    "status_code": 400,
                    "message": f"Missing required field: '{text_field}' is mandatory for {question_type} questions.",
                    "error": "MISSING_REQUIRED_FIELD"
                }

            # Check for duplicates
            if cls._validate_duplicate(collection, text_field, content):
                logger.warning(f"Duplicate {question_type} question creation attempt blocked.")
                return {
                    "success": False,
                    "status_code": 409,
                    "message": f"An identical {question_type} question already exists in the system.",
                    "error": "DUPLICATE_QUESTION"
                }

            # Construct question document using appropriate model
            q_type = question_type.lower().strip()
            if q_type == QUESTION_TYPE_APTITUDE:
                doc = model_class.create_question(
                    category=data.get("category", "General Aptitude"),
                    question=content,
                    options=data.get("options", []),
                    correct_answer=data.get("correctAnswer", data.get("correct_answer")),
                    difficulty=data.get("difficulty", DEFAULT_DIFFICULTY),
                    marks=int(data.get("marks", 1)),
                    explanation=data.get("explanation", ""),
                    question_type=data.get("questionType", "MCQ"),
                    tags=data.get("tags", []),
                    created_by=created_by or data.get("createdBy", data.get("created_by"))
                )
            elif q_type == QUESTION_TYPE_TECHNICAL:
                doc = model_class.create_question(
                    technology=data.get("technology", "General"),
                    category=data.get("category", data.get("technology", "General")),
                    question=content,
                    options=data.get("options", []),
                    correct_answer=data.get("correctAnswer", data.get("correct_answer")),
                    difficulty=data.get("difficulty", DEFAULT_DIFFICULTY),
                    marks=int(data.get("marks", 1)),
                    explanation=data.get("explanation", ""),
                    question_type=data.get("questionType", "MCQ"),
                    tags=data.get("tags", []),
                    created_by=created_by or data.get("createdBy", data.get("created_by"))
                )
            else:  # coding
                doc = model_class.create_question(
                    title=data.get("title", "Untitled Coding Challenge"),
                    programming_language=data.get("programmingLanguage", "Python"),
                    category=data.get("category", "Algorithms"),
                    problem_statement=content,
                    difficulty=data.get("difficulty", DEFAULT_DIFFICULTY),
                    input_format=data.get("inputFormat", ""),
                    output_format=data.get("outputFormat", ""),
                    constraints=data.get("constraints", ""),
                    sample_test_cases=data.get("sampleTestCases", []),
                    hidden_test_cases=data.get("hiddenTestCases", []),
                    marks=int(data.get("marks", 10)),
                    time_limit=float(data.get("timeLimit", 2.0)),
                    memory_limit=int(data.get("memoryLimit", 256)),
                    explanation=data.get("explanation", ""),
                    tags=data.get("tags", []),
                    created_by=created_by or data.get("createdBy", data.get("created_by"))
                )

            result = collection.insert_one(doc)
            logger.info(f"Successfully created {question_type} question with ID: {result.inserted_id}")

            formatted_response = model_class.response(doc)
            return {
                "success": True,
                "status_code": 201,
                "message": f"{question_type.capitalize()} question created successfully.",
                "data": formatted_response
            }

        except ValueError as val_err:
            return {
                "success": False,
                "status_code": 400,
                "message": str(val_err),
                "error": "INVALID_ARGUMENT"
            }
        except PyMongoError as db_err:
            logger.error(f"MongoDB insert error in create_question: {str(db_err)}")
            return {
                "success": False,
                "status_code": 500,
                "message": "Database error occurred while saving question.",
                "error": "DATABASE_ERROR"
            }
        except Exception as err:
            logger.critical(f"Unexpected error in create_question: {str(err)}", exc_info=True)
            return {
                "success": False,
                "status_code": 500,
                "message": "Internal server error occurred.",
                "error": "INTERNAL_SERVER_ERROR"
            }

    @classmethod
    def get_question_by_id(cls, question_type: str, question_id: str) -> Dict[str, Any]:
        """
        Retrieves a single question by its MongoDB ObjectId.

        Args:
            question_type (str): Category ('aptitude', 'technical', 'coding').
            question_id (str): String representation of ObjectId.

        Returns:
            Dict[str, Any]: Standardized response containing question details or 404.
        """
        try:
            if not ObjectId.is_valid(question_id):
                return {
                    "success": False,
                    "status_code": 400,
                    "message": "Invalid question ID format.",
                    "error": "INVALID_OBJECT_ID"
                }

            collection, model_class, _ = cls._get_db_collection_and_model(question_type)
            doc = collection.find_one({"_id": ObjectId(question_id)})

            if not doc:
                return {
                    "success": False,
                    "status_code": 404,
                    "message": f"{question_type.capitalize()} question not found.",
                    "error": "QUESTION_NOT_FOUND"
                }

            return {
                "success": True,
                "status_code": 200,
                "message": "Question retrieved successfully.",
                "data": model_class.response(doc)
            }

        except ValueError as val_err:
            return {"success": False, "status_code": 400, "message": str(val_err), "error": "INVALID_ARGUMENT"}
        except PyMongoError as db_err:
            logger.error(f"MongoDB query error in get_question_by_id: {str(db_err)}")
            return {"success": False, "status_code": 500, "message": "Database error.", "error": "DATABASE_ERROR"}
        except Exception as err:
            logger.critical(f"Unexpected error in get_question_by_id: {str(err)}", exc_info=True)
            return {"success": False, "status_code": 500, "message": "Internal server error.", "error": "INTERNAL_SERVER_ERROR"}

    @classmethod
    def update_question(
        cls,
        question_type: str,
        question_id: str,
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Updates an existing question. Validates duplicate content if the text is modified.

        Args:
            question_type (str): Category ('aptitude', 'technical', 'coding').
            question_id (str): Target question ID.
            update_data (Dict[str, Any]): Fields to update.

        Returns:
            Dict[str, Any]: Standardized API response indicating success or failure.
        """
        try:
            if not ObjectId.is_valid(question_id):
                return {"success": False, "status_code": 400, "message": "Invalid question ID.", "error": "INVALID_OBJECT_ID"}

            if not update_data:
                return {"success": False, "status_code": 400, "message": "No update payload provided.", "error": "EMPTY_PAYLOAD"}

            collection, model_class, text_field = cls._get_db_collection_and_model(question_type)

            # Prevent updating immutable ID fields
            fields_to_update = dict(update_data)
            fields_to_update.pop("_id", None)
            fields_to_update.pop("id", None)
            fields_to_update.pop("createdAt", None)
            fields_to_update["updatedAt"] = datetime.utcnow()

            # Check duplicate if content text is being updated
            if text_field in fields_to_update:
                new_text = fields_to_update[text_field]
                if cls._validate_duplicate(collection, text_field, new_text, exclude_id=question_id):
                    return {
                        "success": False,
                        "status_code": 409,
                        "message": "Another question with this content already exists.",
                        "error": "DUPLICATE_QUESTION"
                    }

            result = collection.update_one(
                {"_id": ObjectId(question_id)},
                {"$set": fields_to_update}
            )

            if result.matched_count == 0:
                return {"success": False, "status_code": 404, "message": "Question not found.", "error": "QUESTION_NOT_FOUND"}

            logger.info(f"Updated {question_type} question ID: {question_id}")
            updated_doc = collection.find_one({"_id": ObjectId(question_id)})

            return {
                "success": True,
                "status_code": 200,
                "message": "Question updated successfully.",
                "data": model_class.response(updated_doc) if updated_doc else {}
            }

        except ValueError as val_err:
            return {"success": False, "status_code": 400, "message": str(val_err), "error": "INVALID_ARGUMENT"}
        except PyMongoError as db_err:
            logger.error(f"MongoDB update error: {str(db_err)}")
            return {"success": False, "status_code": 500, "message": "Database update failure.", "error": "DATABASE_ERROR"}
        except Exception as err:
            logger.critical(f"Unexpected error in update_question: {str(err)}", exc_info=True)
            return {"success": False, "status_code": 500, "message": "Internal server error.", "error": "INTERNAL_SERVER_ERROR"}

    @classmethod
    def delete_question(cls, question_type: str, question_id: str, soft_delete: bool = True) -> Dict[str, Any]:
        """
        Deletes a question. Supports both soft delete (setting isActive=False) and hard delete.

        Args:
            question_type (str): Category ('aptitude', 'technical', 'coding').
            question_id (str): Target question ID.
            soft_delete (bool): If True, marks isActive=False instead of removing document.

        Returns:
            Dict[str, Any]: Standardized API response.
        """
        try:
            if not ObjectId.is_valid(question_id):
                return {"success": False, "status_code": 400, "message": "Invalid question ID.", "error": "INVALID_OBJECT_ID"}

            collection, _, _ = cls._get_db_collection_and_model(question_type)

            if soft_delete:
                result = collection.update_one(
                    {"_id": ObjectId(question_id)},
                    {"$set": {"isActive": False, "updatedAt": datetime.utcnow()}}
                )
                modified = result.matched_count > 0
            else:
                result = collection.delete_one({"_id": ObjectId(question_id)})
                modified = result.deleted_count > 0

            if not modified:
                return {"success": False, "status_code": 404, "message": "Question not found.", "error": "QUESTION_NOT_FOUND"}

            logger.info(f"{'Soft' if soft_delete else 'Hard'} deleted {question_type} question ID: {question_id}")
            return {
                "success": True,
                "status_code": 200,
                "message": "Question deleted successfully."
            }

        except ValueError as val_err:
            return {"success": False, "status_code": 400, "message": str(val_err), "error": "INVALID_ARGUMENT"}
        except PyMongoError as db_err:
            logger.error(f"MongoDB delete error: {str(db_err)}")
            return {"success": False, "status_code": 500, "message": "Database deletion failure.", "error": "DATABASE_ERROR"}
        except Exception as err:
            logger.critical(f"Unexpected error in delete_question: {str(err)}", exc_info=True)
            return {"success": False, "status_code": 500, "message": "Internal server error.", "error": "INTERNAL_SERVER_ERROR"}

    @classmethod
    def list_questions(
        cls,
        question_type: str,
        page: int = 1,
        limit: int = DEFAULT_PAGE_SIZE,
        difficulty: Optional[str] = None,
        technology: Optional[str] = None,
        category: Optional[str] = None,
        search_query: Optional[str] = None,
        is_active: Optional[bool] = True
    ) -> Dict[str, Any]:
        """
        Retrieves a paginated list of questions with multi-field filtering and full-text/regex search.

        Args:
            question_type (str): Category ('aptitude', 'technical', 'coding').
            page (int): 1-indexed page number.
            limit (int): Number of items per page.
            difficulty (Optional[str]): Filter by difficulty level ('Easy', 'Medium', 'Hard').
            technology (Optional[str]): Filter by technology stack (for technical questions).
            category (Optional[str]): Filter by sub-category.
            search_query (Optional[str]): Regex search keyword against question text/title.
            is_active (Optional[bool]): Filter by active status (default True).

        Returns:
            Dict[str, Any]: Standardized response containing paginated data and pagination metadata.
        """
        try:
            collection, model_class, text_field = cls._get_db_collection_and_model(question_type)

            # Validate and cap pagination parameters
            page = max(1, int(page))
            limit = min(MAX_PAGE_SIZE, max(1, int(limit)))
            skip = (page - 1) * limit

            # Build query filters
            query: Dict[str, Any] = {}
            if is_active is not None:
                query["isActive"] = is_active

            if difficulty:
                query["difficulty"] = {"$regex": f"^{re.escape(difficulty)}$", "$options": "i"}

            if technology and question_type == QUESTION_TYPE_TECHNICAL:
                query["technology"] = {"$regex": f"^{re.escape(technology)}$", "$options": "i"}

            if category:
                query["category"] = {"$regex": f"^{re.escape(category)}$", "$options": "i"}

            # Search across primary text field and title
            if search_query and search_query.strip():
                regex_pattern = {"$regex": re.escape(search_query.strip()), "$options": "i"}
                if question_type == QUESTION_TYPE_CODING:
                    query["$or"] = [
                        {"title": regex_pattern},
                        {"problemStatement": regex_pattern},
                        {"category": regex_pattern}
                    ]
                else:
                    query["$or"] = [
                        {text_field: regex_pattern},
                        {"category": regex_pattern},
                        {"tags": regex_pattern}
                    ]

            # Execute query and count total
            total_count = collection.count_documents(query)
            cursor = collection.find(query).sort("createdAt", -1).skip(skip).limit(limit)

            formatted_data = []
            for doc in cursor:
                try:
                    formatted_data.append(model_class.response(doc))
                except Exception as e:
                    logger.warning(f"Failed to format document {doc.get('_id')}: {str(e)}")

            total_pages = (total_count + limit - 1) // limit if total_count > 0 else 0

            return {
                "success": True,
                "status_code": 200,
                "message": f"Retrieved {len(formatted_data)} {question_type} questions.",
                "data": formatted_data,
                "meta": {
                    "total_items": total_count,
                    "current_page": page,
                    "items_per_page": limit,
                    "total_pages": total_pages,
                    "has_next": page < total_pages,
                    "has_previous": page > 1
                }
            }

        except ValueError as val_err:
            return {"success": False, "status_code": 400, "message": str(val_err), "error": "INVALID_ARGUMENT"}
        except PyMongoError as db_err:
            logger.error(f"MongoDB pagination error: {str(db_err)}")
            return {"success": False, "status_code": 500, "message": "Database query failure.", "error": "DATABASE_ERROR"}
        except Exception as err:
            logger.critical(f"Unexpected error in list_questions: {str(err)}", exc_info=True)
            return {"success": False, "status_code": 500, "message": "Internal server error.", "error": "INTERNAL_SERVER_ERROR"}

    @classmethod
    def generate_random_questions(
        cls,
        question_type: str,
        size: int = 10,
        difficulty: Optional[str] = None,
        technology: Optional[str] = None,
        category: Optional[str] = None,
        exclude_ids: Optional[List[str]] = None,
        strip_answers: bool = False
    ) -> Dict[str, Any]:
        """
        Scalably generates a random sample of active questions using MongoDB aggregation pipeline ($sample).
        Ideal for automated assessment generation without loading large tables into memory.

        Args:
            question_type (str): Category ('aptitude', 'technical', 'coding').
            size (int): Number of random questions requested.
            difficulty (Optional[str]): Filter by difficulty level.
            technology (Optional[str]): Filter by technology stack.
            category (Optional[str]): Filter by sub-category.
            exclude_ids (Optional[List[str]]): Question IDs to exclude from sampling.
            strip_answers (bool): If True, removes correct answers and hidden test cases (for live exams).

        Returns:
            Dict[str, Any]: Standardized response with sampled question list.
        """
        try:
            collection, model_class, _ = cls._get_db_collection_and_model(question_type)
            size = max(1, min(int(size), MAX_PAGE_SIZE))

            match_stage: Dict[str, Any] = {"isActive": True}

            if difficulty:
                match_stage["difficulty"] = {"$regex": f"^{re.escape(difficulty)}$", "$options": "i"}
            if technology and question_type == QUESTION_TYPE_TECHNICAL:
                match_stage["technology"] = {"$regex": f"^{re.escape(technology)}$", "$options": "i"}
            if category:
                match_stage["category"] = {"$regex": f"^{re.escape(category)}$", "$options": "i"}

            if exclude_ids:
                valid_ids = [ObjectId(qid) for qid in exclude_ids if ObjectId.is_valid(qid)]
                if valid_ids:
                    match_stage["_id"] = {"$nin": valid_ids}

            pipeline = [
                {"$match": match_stage},
                {"$sample": {"size": size}}
            ]

            cursor = collection.aggregate(pipeline)
            sampled_questions = []

            for doc in cursor:
                formatted = model_class.response(doc)
                if strip_answers:
                    formatted.pop("correctAnswer", None)
                    formatted.pop("correct_answer", None)
                    formatted.pop("hiddenTestCases", None)
                sampled_questions.append(formatted)

            return {
                "success": True,
                "status_code": 200,
                "message": f"Generated {len(sampled_questions)} random {question_type} questions.",
                "total_count": len(sampled_questions),
                "data": sampled_questions
            }

        except ValueError as val_err:
            return {"success": False, "status_code": 400, "message": str(val_err), "error": "INVALID_ARGUMENT"}
        except PyMongoError as db_err:
            logger.error(f"MongoDB aggregation error in generate_random_questions: {str(db_err)}")
            return {"success": False, "status_code": 500, "message": "Database random sampling failure.", "error": "DATABASE_ERROR"}
        except Exception as err:
            logger.critical(f"Unexpected error in generate_random_questions: {str(err)}", exc_info=True)
            return {"success": False, "status_code": 500, "message": "Internal server error.", "error": "INTERNAL_SERVER_ERROR"}

    # Convenience wrappers for specific modules
    @classmethod
    def create_aptitude_question(cls, data: Dict[str, Any], created_by: Optional[str] = None) -> Dict[str, Any]:
        return cls.create_question(QUESTION_TYPE_APTITUDE, data, created_by)

    @classmethod
    def create_technical_question(cls, data: Dict[str, Any], created_by: Optional[str] = None) -> Dict[str, Any]:
        return cls.create_question(QUESTION_TYPE_TECHNICAL, data, created_by)

    @classmethod
    def create_coding_question(cls, data: Dict[str, Any], created_by: Optional[str] = None) -> Dict[str, Any]:
        return cls.create_question(QUESTION_TYPE_CODING, data, created_by)
