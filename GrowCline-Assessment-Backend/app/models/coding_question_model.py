"""
Coding Question Model
"""

from app.config.database import Database


class CodingQuestionModel:
    """Coding Question Collection"""

    @staticmethod
    def collection():
        """Return coding_questions collection"""
        db = Database.get_db()
        return db["coding_questions"]