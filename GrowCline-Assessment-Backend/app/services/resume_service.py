"""
Resume Service Module
Responsible for:
- Extracting text from PDF and DOCX resume files
- Analyzing resume content via Groq LLM (with robust heuristic fallback)
- Generating exactly 25 aptitude, 25 technical, and 15 coding questions personalized
  to the candidate's skill profile
- Persisting generated questions into existing question collections
- Persisting a personalized assessment record so the same question set is served
  on every page refresh (no regeneration)
- Managing candidate resume/profile documents in MongoDB

Architecture: Route → Controller → Service → MongoDB
"""

import io
import json
import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from bson import ObjectId
from pymongo.errors import PyMongoError

try:
    from config.database import Database
    from config.settings import Config
    from models.assessment_model import Assessment
    from models.aptitude_question_model import AptitudeQuestion
    from models.technical_question_model import TechnicalQuestion
    from models.coding_question_model import CodingQuestion
except ImportError:
    from app.config.database import Database
    from app.config.settings import Config
    from app.models.assessment_model import Assessment
    from app.models.aptitude_question_model import AptitudeQuestion
    from app.models.technical_question_model import TechnicalQuestion
    from app.models.coding_question_model import CodingQuestion

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

APTITUDE_COUNT  = 25
TECHNICAL_COUNT = 25
CODING_COUNT    = 15

GROQ_MODEL        = "llama3-70b-8192"
PROFILE_MAX_TOKENS = 2000
APTITUDE_MAX_TOKENS  = 8000
TECHNICAL_MAX_TOKENS = 8000
CODING_MAX_TOKENS    = 8000

# Tech dictionary for heuristic fallback parsing
KNOWN_LANGUAGES = {
    "python": "Python", "javascript": "JavaScript", "typescript": "TypeScript",
    "java": "Java", "c++": "C++", "cpp": "C++", "c#": "C#", "c": "C", "go": "Go",
    "golang": "Go", "rust": "Rust", "ruby": "Ruby", "php": "PHP", "kotlin": "Kotlin",
    "swift": "Swift", "sql": "SQL", "html": "HTML", "css": "CSS", "r": "R", "bash": "Bash"
}

KNOWN_FRAMEWORKS = {
    "react": "React", "react.js": "React", "reactjs": "React", "next.js": "Next.js", "nextjs": "Next.js",
    "angular": "Angular", "vue": "Vue.js", "vue.js": "Vue.js", "fastapi": "FastAPI",
    "flask": "Flask", "django": "Django", "express": "Express.js", "express.js": "Express.js",
    "node": "Node.js", "node.js": "Node.js", "nodejs": "Node.js", "spring boot": "Spring Boot",
    "springboot": "Spring Boot", "spring": "Spring Boot", "nest.js": "NestJS", "nestjs": "NestJS",
    "laravel": "Laravel", "flutter": "Flutter", "react native": "React Native"
}

KNOWN_DATABASES = {
    "mongodb": "MongoDB", "mongo": "MongoDB", "postgresql": "PostgreSQL", "postgres": "PostgreSQL",
    "mysql": "MySQL", "sqlite": "SQLite", "redis": "Redis", "oracle": "Oracle", "dynamodb": "DynamoDB"
}

KNOWN_TOOLS = {
    "docker": "Docker", "kubernetes": "Kubernetes", "k8s": "Kubernetes", "git": "Git",
    "github": "GitHub", "aws": "AWS", "azure": "Azure", "gcp": "GCP", "linux": "Linux",
    "tensorflow": "TensorFlow", "pytorch": "PyTorch", "scikit-learn": "Scikit-Learn",
    "pandas": "Pandas", "numpy": "NumPy", "postman": "Postman", "jira": "Jira"
}

# ---------------------------------------------------------------------------
# Groq Client — lazy init
# ---------------------------------------------------------------------------

_groq_client = None


def _get_groq_client():
    global _groq_client
    if _groq_client is not None:
        return _groq_client
    try:
        from groq import Groq  # type: ignore
    except ImportError:
        raise RuntimeError("groq package is not installed. Run: pip install groq")
    api_key = Config.GROQ_API_KEY
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not configured in .env.")
    _groq_client = Groq(api_key=api_key)
    return _groq_client


def _call_groq(system_prompt: str, user_prompt: str, max_tokens: int) -> str:
    client = _get_groq_client()
    resp = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        max_tokens=max_tokens,
        temperature=0.7,
    )
    return resp.choices[0].message.content.strip()


def _parse_json_from_response(raw: str) -> Any:
    """Strip markdown fences if present and parse JSON."""
    cleaned = re.sub(r"```(?:json)?", "", raw).replace("```", "").strip()
    return json.loads(cleaned)


# ---------------------------------------------------------------------------
# Text Extraction
# ---------------------------------------------------------------------------

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract plain text from a PDF file using PyMuPDF."""
    try:
        import pymupdf as fitz
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        pages = [page.get_text() for page in doc]
        doc.close()
        return "\n".join(pages).strip()
    except Exception as exc:
        logger.error(f"PDF extraction failed: {exc}")
        raise ValueError(f"Unable to extract text from PDF: {exc}")


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract plain text from a DOCX file using python-docx."""
    try:
        from docx import Document
        doc = Document(io.BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs).strip()
    except Exception as exc:
        logger.error(f"DOCX extraction failed: {exc}")
        raise ValueError(f"Unable to extract text from DOCX: {exc}")


def extract_resume_text(file_bytes: bytes, filename: str) -> str:
    """Route to the correct extractor based on file extension."""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext == "pdf":
        return extract_text_from_pdf(file_bytes)
    elif ext in ("doc", "docx"):
        return extract_text_from_docx(file_bytes)
    else:
        raise ValueError(f"Unsupported file format: .{ext}. Please upload PDF or DOCX.")


# ---------------------------------------------------------------------------
# Heuristic Resume Parser Fallback
# ---------------------------------------------------------------------------

def analyze_resume_heuristic(resume_text: str) -> Dict[str, Any]:
    """Extremely reliable NLP keyword extraction fallback when AI API is unavailable."""
    text_lower = resume_text.lower()

    found_langs = []
    for k, v in KNOWN_LANGUAGES.items():
        if re.search(r"\b" + re.escape(k) + r"\b", text_lower) and v not in found_langs:
            found_langs.append(v)

    found_fw = []
    for k, v in KNOWN_FRAMEWORKS.items():
        if re.search(r"\b" + re.escape(k) + r"\b", text_lower) and v not in found_fw:
            found_fw.append(v)

    found_db = []
    for k, v in KNOWN_DATABASES.items():
        if re.search(r"\b" + re.escape(k) + r"\b", text_lower) and v not in found_db:
            found_db.append(v)

    found_tools = []
    for k, v in KNOWN_TOOLS.items():
        if re.search(r"\b" + re.escape(k) + r"\b", text_lower) and v not in found_tools:
            found_tools.append(v)

    exp_level = "Junior"
    if re.search(r"\b(senior|lead|architect|principal|5\+ years|6\+ years|7\+ years|8\+ years)\b", text_lower):
        exp_level = "Senior"
    elif re.search(r"\b(mid|experienced|3\+ years|4\+ years|2-4 years|3-5 years)\b", text_lower):
        exp_level = "Mid"
    elif re.search(r"\b(fresher|intern|internship|graduate|student)\b", text_lower):
        exp_level = "Fresher"

    all_skills = list(set(found_langs + found_fw + found_db + found_tools))

    # Extract basic name/email if present
    email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", resume_text)
    email = email_match.group(0) if email_match else ""

    lines = [l.strip() for l in resume_text.split("\n") if l.strip()]
    name = lines[0] if lines and len(lines[0]) < 40 and not "@" in lines[0] else ""

    return {
        "name": name,
        "email": email,
        "experience_level": exp_level,
        "education": "Bachelor's Degree",
        "skills": all_skills,
        "programming_languages": found_langs,
        "frameworks": found_fw,
        "libraries": [t for t in found_tools if t in ("Pandas", "NumPy", "TensorFlow", "PyTorch", "Scikit-Learn")],
        "databases": found_db,
        "cloud_technologies": [t for t in found_tools if t in ("AWS", "Azure", "GCP")],
        "tools": found_tools,
        "domains": ["Software Engineering"],
        "projects": [],
        "certifications": [],
        "years_of_experience": 0 if exp_level == "Fresher" else (1 if exp_level == "Junior" else 3),
    }


# ---------------------------------------------------------------------------
# Resume Analysis (Groq AI → Structured Skill Profile with Fallback)
# ---------------------------------------------------------------------------

PROFILE_SYSTEM_PROMPT = (
    "You are an expert resume analyst. "
    "Extract a structured candidate skill profile from the given resume text. "
    "Return ONLY a raw JSON object — no markdown, no code fences, no commentary. "
    "Do NOT hallucinate skills. Only include what is actually mentioned in the resume."
)

PROFILE_USER_TEMPLATE = """
Analyze this resume and extract a structured skill profile.

Resume Text:
{resume_text}

Return ONLY this JSON structure (include only fields where data is present):
{{
  "name": "<full name if found>",
  "email": "<email if found>",
  "experience_level": "<Fresher|Junior|Mid|Senior based on years of experience>",
  "education": "<highest degree>",
  "skills": ["<skill1>", "<skill2>"],
  "programming_languages": ["<lang1>", "<lang2>"],
  "frameworks": ["<framework1>"],
  "libraries": ["<lib1>"],
  "databases": ["<db1>"],
  "cloud_technologies": ["<cloud1>"],
  "tools": ["<tool1>"],
  "domains": ["<domain1>"],
  "projects": [
    {{"name": "<project name>", "technologies": ["<tech1>"]}}
  ],
  "certifications": ["<cert1>"],
  "years_of_experience": <number or 0 if fresher>
}}
""".strip()


def analyze_resume_with_groq(resume_text: str) -> Dict[str, Any]:
    """Call Groq LLM with automatic heuristic fallback on API error."""
    if not resume_text or len(resume_text) < 30:
        raise ValueError("Resume text is too short or empty to analyze.")

    truncated_text = resume_text[:6000]
    user_prompt = PROFILE_USER_TEMPLATE.format(resume_text=truncated_text)

    try:
        raw = _call_groq(PROFILE_SYSTEM_PROMPT, user_prompt, PROFILE_MAX_TOKENS)
        profile = _parse_json_from_response(raw)

        if not isinstance(profile, dict):
            raise ValueError("Invalid JSON structure")

        for list_field in ["skills", "programming_languages", "frameworks", "libraries",
                           "databases", "cloud_technologies", "tools", "domains",
                           "certifications", "projects"]:
            if not isinstance(profile.get(list_field), list):
                profile[list_field] = []

        profile.setdefault("experience_level", "Junior")
        profile.setdefault("years_of_experience", 0)
        return profile
    except Exception as exc:
        logger.warning(f"Groq AI resume parsing notice ({exc}). Using heuristic NLP parser.")
        return analyze_resume_heuristic(resume_text)


# ---------------------------------------------------------------------------
# Heuristic Question Generators (25 Aptitude, 25 Technical, 15 Coding)
# ---------------------------------------------------------------------------

def generate_aptitude_questions_heuristic(profile: Dict[str, Any]) -> List[Dict]:
    """Generate 25 high-quality aptitude questions covering Quantitative, Logical, Analytical, Verbal."""
    exp = profile.get("experience_level", "Junior")
    questions = []

    # 1-8: Quantitative Aptitude
    quant_pool = [
        {"question": "A train running at a speed of 60 km/hr crosses a pole in 9 seconds. What is the length of the train?", "options": ["120 metres", "150 metres", "180 metres", "324 metres"], "correctAnswer": "150 metres", "category": "Quantitative", "difficulty": "Medium", "explanation": "Speed = 60 * 5/18 = 50/3 m/s. Length = Speed * Time = 50/3 * 9 = 150m."},
        {"question": "A person crosses a 600 m long street in 5 minutes. What is his speed in km per hour?", "options": ["3.6 km/hr", "7.2 km/hr", "8.4 km/hr", "10 km/hr"], "correctAnswer": "7.2 km/hr", "category": "Quantitative", "difficulty": "Easy", "explanation": "Speed = 600m / 300s = 2 m/s = 2 * 18/5 = 7.2 km/hr."},
        {"question": "If 12 men or 18 women can do a piece of work in 14 days, in how many days can 8 men and 16 women do it?", "options": ["8 days", "9 days", "10 days", "12 days"], "correctAnswer": "9 days", "category": "Quantitative", "difficulty": "Medium", "explanation": "12M = 18W => 1M = 1.5W. 8M + 16W = 28W. Time = (18 * 14) / 28 = 9 days."},
        {"question": "A vendor bought toffees at 6 for a rupee. How many for a rupee must he sell to gain 20%?", "options": ["3", "4", "5", "6"], "correctAnswer": "5", "category": "Quantitative", "difficulty": "Medium", "explanation": "CP of 6 = 1 Re. SP of 6 = 1.2 Re. To sell for 1 Re, count = 6 / 1.2 = 5."},
        {"question": "What is the probability of getting a sum 9 from two throws of a dice?", "options": ["1/6", "1/8", "1/9", "1/12"], "correctAnswer": "1/9", "category": "Quantitative", "difficulty": "Medium", "explanation": "Favorable pairs: (3,6), (4,5), (5,4), (6,3) = 4 pairs out of 36. 4/36 = 1/9."},
        {"question": "The average of 5 consecutive numbers is 20. What is the largest of these numbers?", "options": ["20", "21", "22", "23"], "correctAnswer": "22", "category": "Quantitative", "difficulty": "Easy", "explanation": "Middle number is 20. Numbers are 18, 19, 20, 21, 22. Largest is 22."},
        {"question": "A sum of money at simple interest doubles in 10 years. In how many years will it triple?", "options": ["15 years", "18 years", "20 years", "25 years"], "correctAnswer": "20 years", "category": "Quantitative", "difficulty": "Medium", "explanation": "Interest = P in 10 yrs. For triple, interest = 2P, which takes 20 years."},
        {"question": "In a competitive exam, 60% candidates passed in English, 70% in Math, and 20% failed in both. If 250 passed in both, total candidates were:", "options": ["400", "500", "600", "700"], "correctAnswer": "500", "category": "Quantitative", "difficulty": "Hard", "explanation": "% passing at least one subject = 100 - 20 = 80%. % passing both = 60 + 70 - 80 = 50%. 50% = 250 => Total = 500."},
    ]

    # 9-17: Logical Reasoning
    logical_pool = [
        {"question": "Find the missing term in the sequence: 2, 6, 12, 20, 30, ?", "options": ["36", "40", "42", "44"], "correctAnswer": "42", "category": "Logical", "difficulty": "Easy", "explanation": "Differences are +4, +6, +8, +10, +12. 30 + 12 = 42."},
        {"question": "Look at this series: 7, 10, 8, 11, 9, 12, ... What number should come next?", "options": ["7", "10", "12", "13"], "correctAnswer": "10", "category": "Logical", "difficulty": "Easy", "explanation": "Alternating pattern: +3, -2, +3, -2, +3, -2. 12 - 2 = 10."},
        {"question": "If CAT is coded as 3120, how is DOG coded?", "options": ["4157", "41515", "4157", "41514"], "correctAnswer": "4157", "category": "Logical", "difficulty": "Easy", "explanation": "C=3, A=1, T=20. D=4, O=15, G=7 -> 4157."},
        {"question": "Pointing to a photograph, a man said, 'I have no brother or sister but that man's father is my father's son.' Whose photograph was it?", "options": ["His own", "His son's", "His father's", "His nephew's"], "correctAnswer": "His son's", "category": "Logical", "difficulty": "Medium", "explanation": "My father's son = Me. 'That man's father is Me' -> That man is my son."},
        {"question": "Syllogism: All Mangoes are Golden. All Golden things are Choice. Conclusion I: All Mangoes are Choice. Conclusion II: Some Golden things are Mangoes.", "options": ["Only I follows", "Only II follows", "Both I and II follow", "Neither follows"], "correctAnswer": "Both I and II follow", "category": "Logical", "difficulty": "Medium", "explanation": "All Mangoes -> Golden -> Choice. Both conclusions logically hold true."},
        {"question": "Five friends A, B, C, D, E are sitting in a row facing North. A is to the immediate right of B. E is to the left of C but right of D. B is right of E. Who is in the middle?", "options": ["A", "B", "C", "E"], "correctAnswer": "B", "category": "Logical", "difficulty": "Hard", "explanation": "Order from left to right: D, E, B, A, C. B is in the middle position."},
        {"question": "If South-East becomes North, North-East becomes West and so on. What will West become?", "options": ["North-East", "South-East", "South-West", "North-West"], "correctAnswer": "South-East", "category": "Logical", "difficulty": "Hard", "explanation": "Directions rotate 135 degrees counter-clockwise. West turns to South-East."},
        {"question": "Which word does NOT belong with the others?", "options": ["Leopard", "Cougar", "Elephant", "Lion"], "correctAnswer": "Elephant", "category": "Logical", "difficulty": "Easy", "explanation": "Leopard, Cougar, and Lion belong to the feline family. Elephant does not."},
        {"question": "Statement: Should physical education be compulsory in schools? Argument I: Yes, it improves overall health. Argument II: No, academic performance suffers.", "options": ["Only I is strong", "Only II is strong", "Both are strong", "Neither is strong"], "correctAnswer": "Only I is strong", "category": "Logical", "difficulty": "Medium", "explanation": "Physical health directly enhances focus and learning. Argument I is strong."},
    ]

    # 18-22: Analytical Reasoning
    analytical_pool = [
        {"question": "In a group of 100 people, 65 can speak English and 40 can speak Hindi. How many can speak BOTH languages assuming everyone speaks at least one?", "options": ["5", "10", "15", "25"], "correctAnswer": "5", "category": "Analytical", "difficulty": "Medium", "explanation": "65 + 40 - 100 = 5 people speak both."},
        {"question": "A clock shows 3:30. If the minute hand points East, in which direction does the hour hand point?", "options": ["North-East", "South-East", "North-West", "South-West"], "correctAnswer": "North-East", "category": "Analytical", "difficulty": "Medium", "explanation": "At 3:30, minute hand is at 6 (South). If 6 is East, 3:15 (Hour hand at 3.5) points North-East."},
        {"question": "Four people P, Q, R, S need to cross a bridge at night with one flashlight. P takes 1 min, Q takes 2 min, R takes 5 min, S takes 10 min. At most 2 people cross at a time. What is the minimum time needed?", "options": ["17 mins", "19 mins", "21 mins", "15 mins"], "correctAnswer": "17 mins", "category": "Analytical", "difficulty": "Hard", "explanation": "P+Q cross (2m), P returns (1m), R+S cross (10m), Q returns (2m), P+Q cross (2m) = 17 mins."},
        {"question": "A cube of side 4 cm is painted red on all sides and cut into smaller 1 cm cubes. How many small cubes have NO red paint on any face?", "options": ["4", "8", "16", "27"], "correctAnswer": "8", "category": "Analytical", "difficulty": "Medium", "explanation": "Unpainted cubes = (n-2)^3 = (4-2)^3 = 2^3 = 8."},
        {"question": "A team of 3 must be selected from 3 men (M1, M2, M3) and 3 women (W1, W2, W3). M1 refuses to work with W2. W1 must be included. How many valid teams can be formed?", "options": ["6", "7", "8", "10"], "correctAnswer": "8", "category": "Analytical", "difficulty": "Hard", "explanation": "Choosing W1 and 2 others from 5 candidates, excluding the forbidden pair (M1, W2) gives 8 valid combinations."},
    ]

    # 23-25: Verbal Reasoning
    verbal_pool = [
        {"question": "Choose the word most nearly OPPOSITE in meaning to MITIGATE:", "options": ["Alleviate", "Aggravate", "Diminish", "Relieve"], "correctAnswer": "Aggravate", "category": "Verbal", "difficulty": "Easy", "explanation": "Mitigate means to lessen in severity. Aggravate means to make worse."},
        {"question": "Complete the analogy: Architect : Building :: Sculptor : ?", "options": ["Museum", "Statue", "Chisel", "Stone"], "correctAnswer": "Statue", "category": "Verbal", "difficulty": "Easy", "explanation": "An architect creates a building; a sculptor creates a statue."},
        {"question": "Select the correct spelling:", "options": ["Accomodate", "Accommodate", "Acommodate", "Accommodat"], "correctAnswer": "Accommodate", "category": "Verbal", "difficulty": "Easy", "explanation": "Accommodate has double 'c' and double 'm'."},
    ]

    return quant_pool + logical_pool + analytical_pool + verbal_pool


def generate_technical_questions_heuristic(profile: Dict[str, Any]) -> List[Dict]:
    """Generate 25 scenario-based technical questions matching the candidate's exact stack."""
    langs = [l.lower() for l in profile.get("programming_languages", [])]
    fws = [f.lower() for f in profile.get("frameworks", [])]
    dbs = [d.lower() for d in profile.get("databases", [])]
    tools = [t.lower() for t in profile.get("tools", [])]

    all_tech = set(langs + fws + dbs + tools)
    questions = []

    # Category pools
    python_qs = [
        {"question": "You are building a FastAPI service that performs CPU-bound image processing. Which approach prevents blocking the asyncio event loop?", "options": ["Execute the CPU-bound task in run_in_executor() or a Celery worker", "Declare the route with async def and run inline loops", "Use global thread locks inside the endpoint", "Increase the uvicorn worker timeout"], "correctAnswer": "Execute the CPU-bound task in run_in_executor() or a Celery worker", "technology": "Python", "category": "Backend", "difficulty": "Hard", "explanation": "CPU-bound blocking calls inside an async event loop stall all concurrent requests. Offloading to worker threads or Celery keeps the loop responsive."},
        {"question": "In Python, how does memory management handle cyclical object references when reference counting drops to zero for outside handles?", "options": ["The cyclic garbage collector runs generational checks to break reference cycles", "Reference counting automatically handles cycles", "Memory leaks permanently until process terminates", "Cyclic objects are freed immediately upon scope exit"], "correctAnswer": "The cyclic garbage collector runs generational checks to break reference cycles", "technology": "Python", "category": "Core", "difficulty": "Medium", "explanation": "Python uses reference counting as primary GC, but relies on a generational cyclic GC to detect and clean unreachable circular references."},
        {"question": "What is the key advantage of using a Python Generator (yield) over returning a full list when processing large datasets?", "options": ["Generators evaluate lazily, consuming O(1) memory per iteration", "Generators run faster by compiling to C extensions", "Generators automatically parallelize loop execution across CPU cores", "Generators persist data on disk automatically"], "correctAnswer": "Generators evaluate lazily, consuming O(1) memory per iteration", "technology": "Python", "category": "Data Structures", "difficulty": "Medium", "explanation": "Generators yield elements on demand rather than loading the entire dataset into RAM."},
    ]

    react_qs = [
        {"question": "A React component renders a large list and suffers from input lag on every keystroke. What is the most effective optimization?", "options": ["Virtualize the list rendering with react-window and wrap item components in React.memo", "Store the entire list state in a global Redux store without memoization", "Replace useState with useRef for all controlled input fields", "Call forceUpdate() inside the onChange handler"], "correctAnswer": "Virtualize the list rendering with react-window and wrap item components in React.memo", "technology": "React", "category": "Frontend", "difficulty": "Hard", "explanation": "List virtualization renders only DOM nodes in the visible viewport, drastically reducing DOM overhead during re-renders."},
        {"question": "Why must clean-up functions be returned inside useEffect when subscribing to WebSocket connections in React?", "options": ["To close stale socket connections and prevent memory leaks on component unmount", "To trigger automatic component re-render when WebSocket disconnects", "To prevent React from rendering in strict mode", "To convert WebSocket payloads into JSON format"], "correctAnswer": "To close stale socket connections and prevent memory leaks on component unmount", "technology": "React", "category": "Frontend", "difficulty": "Medium", "explanation": "Without cleanup functions, navigating away or re-running effects leaves open connections and event listeners in memory."},
        {"question": "In React 18, how does Automatic Batching improve state update performance?", "options": ["Groups multiple state updates inside promises, timeouts, and native handlers into a single re-render", "Disables all re-renders until the user stops interacting", "Compiles React components directly into WebAssembly", "Automatically memoizes all custom hooks"], "correctAnswer": "Groups multiple state updates inside promises, timeouts, and native handlers into a single re-render", "technology": "React", "category": "Frontend", "difficulty": "Medium", "explanation": "React 18 batches state updates across async boundaries (setTimeout, fetch callbacks) into one single render pass."},
    ]

    node_qs = [
        {"question": "In Node.js, what happens when a synchronous blocking operation (e.g. fs.readFileSync) is called inside an HTTP request handler?", "options": ["It blocks the single event loop thread, preventing all incoming HTTP requests from being processed", "Node.js automatically delegates file reading to a background worker thread", "It throws a non-catchable ThreadBlockedException", "It runs asynchronously without affecting event loop throughput"], "correctAnswer": "It blocks the single event loop thread, preventing all incoming HTTP requests from being processed", "technology": "Node.js", "category": "Backend", "difficulty": "Hard", "explanation": "Node.js uses a single event loop for JavaScript execution; synchronous I/O blocks the entire thread."},
        {"question": "How does libuv manage asynchronous file I/O operations in Node.js?", "options": ["Offloads file system calls to an internal thread pool (default 4 threads)", "Uses epoll directly for all disk I/O operations without threads", "Spawns a separate OS process per file read", "Executes file I/O on the main V8 execution thread"], "correctAnswer": "Offloads file system calls to an internal thread pool (default 4 threads)", "technology": "Node.js", "category": "Architecture", "difficulty": "Medium", "explanation": "Because disk I/O cannot always be non-blocking on OS level, libuv uses its thread pool to perform asynchronous disk operations."},
    ]

    mongo_qs = [
        {"question": "You have a MongoDB query on `{ status: 1, createdAt: -1 }` that is running slowly. How should the compound index be created?", "options": ["db.collection.createIndex({ status: 1, createdAt: -1 }) following the Equality, Sort, Range rule", "db.collection.createIndex({ createdAt: -1 }) only", "db.collection.createIndex({ status: 1 }) and separate index on createdAt", "db.collection.createIndex({ $text: { search: 'status' } })"], "correctAnswer": "db.collection.createIndex({ status: 1, createdAt: -1 }) following the Equality, Sort, Range rule", "technology": "MongoDB", "category": "Database", "difficulty": "Hard", "explanation": "The ESR (Equality, Sort, Range) rule ensures compound indexes satisfy filter equality first and sort order second without in-memory sorting."},
        {"question": "What is the primary trade-off of using embedded documents over normalized references in MongoDB?", "options": ["Faster read queries with single fetches, but risk of document size exceeding 16MB limit and duplicate data updates", "Automatic ACID transactions across all collections", "Slower read operations due to joins", "Inability to index nested fields"], "correctAnswer": "Faster read queries with single fetches, but risk of document size exceeding 16MB limit and duplicate data updates", "technology": "MongoDB", "category": "Database", "difficulty": "Medium", "explanation": "Embedding avoids joins and speeds up reads, but can hit the 16MB document limit and requires multi-document updates for shared data."},
    ]

    docker_aws_qs = [
        {"question": "How can you minimize Docker image size when containerizing a Python FastAPI backend?", "options": ["Use multi-stage builds with python:3.11-slim and copy only necessary virtual environment packages", "Use full ubuntu:latest base image and install build-essential tools in final stage", "Include source git history inside the Docker image", "Disable Docker layer caching entirely"], "correctAnswer": "Use multi-stage builds with python:3.11-slim and copy only necessary virtual environment packages", "technology": "Docker", "category": "DevOps", "difficulty": "Medium", "explanation": "Multi-stage builds separate compilation dependencies from the lean runtime image, shrinking production container size."},
        {"question": "Which AWS service is best suited for hosting stateless microservices with automatic container scaling and serverless pricing?", "options": ["AWS Fargate (ECS/EKS)", "AWS EC2 Reserved Instances", "AWS S3 Static Hosting", "AWS EBS Volume Manager"], "correctAnswer": "AWS Fargate (ECS/EKS)", "technology": "AWS", "category": "Cloud", "difficulty": "Medium", "explanation": "Fargate provides serverless compute engine for containers without provisioning EC2 instances."},
    ]

    general_cs_qs = [
        {"question": "What is the main difference between REST and GraphQL API architectures?", "options": ["GraphQL allows clients to request exact fields needed in a single query, avoiding over-fetching", "REST requires WebSocket connections for all requests", "GraphQL only works with SQL databases", "REST does not support HTTP caching headers"], "correctAnswer": "GraphQL allows clients to request exact fields needed in a single query, avoiding over-fetching", "technology": "Web Architecture", "category": "APIs", "difficulty": "Medium", "explanation": "GraphQL enables client-specified queries for exact schema attributes."},
        {"question": "Which data structure provides O(1) average time complexity for key lookup, insertion, and deletion?", "options": ["Hash Table / Hash Map", "Binary Search Tree", "Array", "Linked List"], "correctAnswer": "Hash Table / Hash Map", "technology": "Data Structures", "category": "Algorithms", "difficulty": "Easy", "explanation": "Hash tables use hash functions for constant time average operations."},
        {"question": "In Object-Oriented Programming, what does the SOLID 'Open/Closed Principle' state?", "options": ["Software entities should be open for extension, but closed for modification", "Classes should be open for editing by all developers", "All methods must be closed with private access modifiers", "Interfaces should be open to multiple inheritance"], "correctAnswer": "Software entities should be open for extension, but closed for modification", "technology": "Software Design", "category": "Architecture", "difficulty": "Medium", "explanation": "New functionality should be added by extending code (e.g. polymorphism) rather than altering existing tested logic."},
        {"question": "What is the primary function of an API Gateway in microservice architectures?", "options": ["Acts as a single entry point for routing, authentication, rate limiting, and request aggregation", "Replaces microservice databases with a central store", "Compiles microservices into a monolithic binary", "Manages git branch deployments automatically"], "correctAnswer": "Acts as a single entry point for routing, authentication, rate limiting, and request aggregation", "technology": "System Design", "category": "Microservices", "difficulty": "Medium", "explanation": "API Gateways handle cross-cutting concerns like security, rate limiting, and routing across services."},
        {"question": "What does ACID stand for in relational database management systems?", "options": ["Atomicity, Consistency, Isolation, Durability", "Availability, Consistency, Integration, Distribution", "Authentication, Control, Identity, Data", "Automated, Concurrent, Indexed, Distributed"], "correctAnswer": "Atomicity, Consistency, Isolation, Durability", "technology": "Databases", "category": "SQL", "difficulty": "Easy", "explanation": "ACID properties guarantee reliable transaction processing in database systems."},
        {"question": "What is the time complexity of building a heap from an unsorted array of N elements using Floyd's build-heap algorithm?", "options": ["O(N)", "O(N log N)", "O(N^2)", "O(log N)"], "correctAnswer": "O(N)", "technology": "Algorithms", "category": "Data Structures", "difficulty": "Hard", "explanation": "Bottom-up heap construction runs in linear O(N) time mathematically."},
        {"question": "In web security, what vulnerability is mitigated by implementing SameSite cookies and CSRF tokens?", "options": ["Cross-Site Request Forgery (CSRF)", "Cross-Site Scripting (XSS)", "SQL Injection", "Man-in-the-Middle (MitM) Attacks"], "correctAnswer": "Cross-Site Request Forgery (CSRF)", "technology": "Security", "category": "Web Security", "difficulty": "Medium", "explanation": "CSRF tokens verify that request originates from authorized user interface."},
        {"question": "Which HTTP status code should a server return when a request payload fails schema validation?", "options": ["422 Unprocessable Entity (or 400 Bad Request)", "500 Internal Server Error", "403 Forbidden", "404 Not Found"], "correctAnswer": "422 Unprocessable Entity (or 400 Bad Request)", "technology": "HTTP Protocol", "category": "APIs", "difficulty": "Easy", "explanation": "422 or 400 indicates client error due to invalid payload formatting."},
        {"question": "What is the purpose of a Reverse Proxy (such as Nginx)?", "options": ["Sits in front of backend servers to handle SSL termination, load balancing, and static caching", "Directs outbound client DNS lookups to root servers", "Encrypts client-side browser storage", "Executes background cron jobs on database servers"], "correctAnswer": "Sits in front of backend servers to handle SSL termination, load balancing, and static caching", "technology": "DevOps", "category": "Infrastructure", "difficulty": "Medium", "explanation": "Nginx reverse proxies intercept client traffic and distribute load to application servers."},
        {"question": "What is the difference between Process and Thread in operating systems?", "options": ["Processes have independent memory spaces, while threads share memory space within the same process", "Threads run in kernel space, processes run in user space", "Processes cannot execute concurrently", "Threads have higher context-switching overhead than processes"], "correctAnswer": "Processes have independent memory spaces, while threads share memory space within the same process", "technology": "Operating Systems", "category": "Core CS", "difficulty": "Medium", "explanation": "Threads share heap and code segments of parent process; processes isolate memory."},
        {"question": "What is the primary purpose of indexing a database column?", "options": ["To speed up data retrieval queries at the cost of slower write/insert operations", "To encrypt column values for security compliance", "To automatically remove duplicate rows", "To prevent foreign key constraints"], "correctAnswer": "To speed up data retrieval queries at the cost of slower write/insert operations", "technology": "Databases", "category": "Performance", "difficulty": "Easy", "explanation": "Indexes maintain lookup trees (B-Trees) to accelerate SELECT queries, but add overhead to INSERT/UPDATE."},
        {"question": "In git, what does `git rebase` do compared to `git merge`?", "options": ["Re-applies commits from one branch onto the tip of another branch, creating a linear history", "Deletes all local uncommitted changes", "Merges branches with a distinct merge commit node", "Clones a remote repository to local machine"], "correctAnswer": "Re-applies commits from one branch onto the tip of another branch, creating a linear history", "technology": "Git", "category": "Tools", "difficulty": "Medium", "explanation": "Rebase rewrites commit history onto the target branch tip for a clean linear log."},
        {"question": "What is the CAP Theorem statement regarding distributed database systems?", "options": ["A distributed system can guarantee at most 2 out of 3: Consistency, Availability, Partition Tolerance", "Computers Always Process data in linear time", "Caching Accelerates Performance in all scenarios", "Cluster Architecture Prevents downtime completely"], "correctAnswer": "A distributed system can guarantee at most 2 out of 3: Consistency, Availability, Partition Tolerance", "technology": "System Design", "category": "Distributed Systems", "difficulty": "Hard", "explanation": "In presence of network partitions (P), a system must trade off between Consistency (C) or Availability (A)."},
        {"question": "What is the main function of Docker volumes?", "options": ["To persist container data outside the ephemeral container filesystem lifespan", "To speed up CPU execution inside containers", "To limit container RAM usage", "To compile source code into binaries"], "correctAnswer": "To persist container data outside the ephemeral container filesystem lifespan", "technology": "Docker", "category": "DevOps", "difficulty": "Easy", "explanation": "Volumes mount directories from host machine to preserve data when containers stop or restart."},
        {"question": "Which design pattern is best used when creating families of related objects without specifying concrete classes?", "options": ["Abstract Factory Pattern", "Singleton Pattern", "Observer Pattern", "Strategy Pattern"], "correctAnswer": "Abstract Factory Pattern", "technology": "Design Patterns", "category": "Architecture", "difficulty": "Hard", "explanation": "Abstract Factory provides an interface for creating families of dependent objects."},
    ]

    # Combine prioritized matched tech questions + general CS questions
    matched = []
    if "python" in all_tech: matched.extend(python_qs)
    if "react" in all_tech or "next.js" in all_tech: matched.extend(react_qs)
    if "node.js" in all_tech or "express.js" in all_tech: matched.extend(node_qs)
    if "mongodb" in all_tech: matched.extend(mongo_qs)
    if "docker" in all_tech or "aws" in all_tech: matched.extend(docker_aws_qs)

    pool = matched + general_cs_qs

    # Guarantee exactly 25 questions without duplicate content
    seen = set()
    final_questions = []
    for q in pool:
        if q["question"] not in seen:
            seen.add(q["question"])
            final_questions.append(q)
        if len(final_questions) == TECHNICAL_COUNT:
            break

    # If pool is smaller than 25, pad from general_cs_qs
    while len(final_questions) < TECHNICAL_COUNT:
        for q in general_cs_qs:
            if q["question"] not in seen:
                seen.add(q["question"])
                final_questions.append(q)
            if len(final_questions) == TECHNICAL_COUNT:
                break

    return final_questions[:TECHNICAL_COUNT]


def generate_coding_questions_heuristic(profile: Dict[str, Any]) -> List[Dict]:
    """Generate 15 LeetCode-style coding problems adapted to candidate's primary language.
    Uses a shuffled random sample from a large pool to prevent repetition."""
    import random
    langs = profile.get("programming_languages", [])
    primary_lang = langs[0] if langs else "Python"

    # Full pool of 42 unique problems across all DSA categories
    full_pool = [
        # ── Arrays & Hashing ──────────────────────────────────────────────────
        {"title": "Two Sum Target", "problemStatement": "Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`. Each input has exactly one solution, and you may not use the same element twice.", "inputFormat": "First line: space-separated integers for nums. Second line: target integer.", "outputFormat": "Two space-separated indices.", "constraints": "2 <= nums.length <= 10^4\n-10^9 <= nums[i] <= 10^9", "sampleInput": "2 7 11 15\n9", "sampleOutput": "0 1", "difficulty": "Easy", "category": "Arrays & Hashing"},
        {"title": "Contains Duplicate Check", "problemStatement": "Given an integer array `nums`, return `true` if any value appears at least twice in the array, and return `false` if every element is distinct.", "inputFormat": "Space-separated array of integers.", "outputFormat": "true or false", "constraints": "1 <= nums.length <= 10^5", "sampleInput": "1 2 3 1", "sampleOutput": "true", "difficulty": "Easy", "category": "Arrays & Hashing"},
        {"title": "Group Anagrams Together", "problemStatement": "Given an array of strings `strs`, group the anagrams together. You can return the answer in any order.", "inputFormat": "Comma-separated list of strings.", "outputFormat": "Groups of anagrams, each group on one line.", "constraints": "1 <= strs.length <= 10^4", "sampleInput": "eat,tea,tan,ate,nat,bat", "sampleOutput": "eat tea ate\ntan nat\nbat", "difficulty": "Medium", "category": "Arrays & Hashing"},
        {"title": "Top K Frequent Elements", "problemStatement": "Given an integer array `nums` and an integer `k`, return the `k` most frequent elements. You may return the answer in any order.", "inputFormat": "Line 1: space-separated nums. Line 2: k.", "outputFormat": "k most frequent elements.", "constraints": "1 <= nums.length <= 10^5\nk is guaranteed to be valid", "sampleInput": "1 1 1 2 2 3\n2", "sampleOutput": "1 2", "difficulty": "Medium", "category": "Arrays & Hashing"},
        {"title": "Product of Array Except Self", "problemStatement": "Given an integer array `nums`, return an array `answer` such that `answer[i]` is equal to the product of all elements of `nums` except `nums[i]`. Solve in O(n) without using the division operation.", "inputFormat": "Space-separated array nums.", "outputFormat": "Product array.", "constraints": "2 <= nums.length <= 10^5", "sampleInput": "1 2 3 4", "sampleOutput": "24 12 8 6", "difficulty": "Medium", "category": "Arrays & Hashing"},

        # ── Strings ───────────────────────────────────────────────────────────
        {"title": "Valid Anagram Check", "problemStatement": "Given two strings `s` and `t`, return `true` if `t` is an anagram of `s`, and `false` otherwise. An Anagram is a word formed by rearranging the letters of a different word using all original letters exactly once.", "inputFormat": "Two lines containing strings s and t.", "outputFormat": "true or false", "constraints": "1 <= s.length, t.length <= 5 * 10^4", "sampleInput": "anagram\nnagaram", "sampleOutput": "true", "difficulty": "Easy", "category": "Strings"},
        {"title": "Reverse Words in String", "problemStatement": "Given an input string `s`, reverse the order of the words. A word is defined as a sequence of non-space characters. The words in `s` will be separated by at least one space.", "inputFormat": "A single string s.", "outputFormat": "String with words in reverse order.", "constraints": "1 <= s.length <= 10^4", "sampleInput": "the sky is blue", "sampleOutput": "blue is sky the", "difficulty": "Medium", "category": "Strings"},
        {"title": "Palindrome Substring Longest", "problemStatement": "Given a string `s`, return the longest palindromic substring in `s`.", "inputFormat": "Single line string s.", "outputFormat": "Longest palindromic substring.", "constraints": "1 <= s.length <= 1000", "sampleInput": "babad", "sampleOutput": "bab", "difficulty": "Medium", "category": "Strings"},

        # ── Sliding Window ────────────────────────────────────────────────────
        {"title": "Longest Substring Without Repeating", "problemStatement": "Given a string `s`, find the length of the longest substring without repeating characters.", "inputFormat": "Single line string s.", "outputFormat": "Integer representing longest substring length.", "constraints": "0 <= s.length <= 5 * 10^4", "sampleInput": "abcabcbb", "sampleOutput": "3", "difficulty": "Medium", "category": "Sliding Window"},
        {"title": "Minimum Window Substring", "problemStatement": "Given two strings `s` and `t`, return the minimum window substring of `s` such that every character in `t` (including duplicates) is included in the window. If no such window exists, return empty string.", "inputFormat": "Line 1: string s. Line 2: string t.", "outputFormat": "Minimum window substring or empty string.", "constraints": "1 <= s.length, t.length <= 10^5", "sampleInput": "ADOBECODEBANC\nABC", "sampleOutput": "BANC", "difficulty": "Hard", "category": "Sliding Window"},

        # ── Two Pointers ──────────────────────────────────────────────────────
        {"title": "Container With Most Water", "problemStatement": "Given an integer array `height` of length `n`, find two lines that form a container with the x-axis storing the most water. Return the maximum amount of water the container can store.", "inputFormat": "Space-separated array of heights.", "outputFormat": "Single integer representing max area.", "constraints": "n == height.length\n2 <= n <= 10^5", "sampleInput": "1 8 6 2 5 4 8 3 7", "sampleOutput": "49", "difficulty": "Medium", "category": "Two Pointers"},
        {"title": "3Sum Zero Triplets", "problemStatement": "Given an integer array `nums`, return all unique triplets `[nums[i], nums[j], nums[k]]` such that `i != j != k` and `nums[i] + nums[j] + nums[k] == 0`.", "inputFormat": "Space-separated array nums.", "outputFormat": "Triplets list.", "constraints": "3 <= nums.length <= 3000", "sampleInput": "-1 0 1 2 -1 -4", "sampleOutput": "-1 -1 2\n-1 0 1", "difficulty": "Medium", "category": "Two Pointers"},
        {"title": "Trapping Rain Water", "problemStatement": "Given `n` non-negative integers representing an elevation map where the width of each bar is 1, compute how much water it can trap after raining.", "inputFormat": "Space-separated array of heights.", "outputFormat": "Total water trapped.", "constraints": "n == height.length\n1 <= n <= 2 * 10^4", "sampleInput": "0 1 0 2 1 0 1 3 2 1 2 1", "sampleOutput": "6", "difficulty": "Hard", "category": "Two Pointers"},

        # ── Binary Search ─────────────────────────────────────────────────────
        {"title": "Binary Search in Rotated Array", "problemStatement": "Given the array `nums` after possible rotation and an integer `target`, return the index of `target` if it is in `nums`, or `-1` if it is not. Write an algorithm with O(log n) runtime.", "inputFormat": "Line 1: space-separated nums. Line 2: target.", "outputFormat": "Target index or -1.", "constraints": "1 <= nums.length <= 5000", "sampleInput": "4 5 6 7 0 1 2\n0", "sampleOutput": "4", "difficulty": "Medium", "category": "Binary Search"},
        {"title": "Find Minimum in Rotated Array", "problemStatement": "Suppose an array of length `n` sorted in ascending order is rotated between 1 and n times. Given the rotated array, return the minimum element. Write an O(log n) solution.", "inputFormat": "Space-separated rotated sorted array.", "outputFormat": "Minimum element.", "constraints": "n == nums.length\n1 <= n <= 5000", "sampleInput": "3 4 5 1 2", "sampleOutput": "1", "difficulty": "Medium", "category": "Binary Search"},
        {"title": "Median of Two Sorted Arrays", "problemStatement": "Given two sorted arrays `nums1` and `nums2` of size `m` and `n`, return the median of the two sorted arrays. The overall runtime complexity should be O(log(m+n)).", "inputFormat": "Line 1: nums1. Line 2: nums2.", "outputFormat": "Median value.", "constraints": "0 <= m, n <= 1000", "sampleInput": "1 3\n2", "sampleOutput": "2.0", "difficulty": "Hard", "category": "Binary Search"},

        # ── Stacks ────────────────────────────────────────────────────────────
        {"title": "Valid Parentheses String", "problemStatement": "Given a string `s` containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid. A string is valid if brackets close in the correct order.", "inputFormat": "Single line string s.", "outputFormat": "true or false", "constraints": "1 <= s.length <= 10^4", "sampleInput": "()[]{}", "sampleOutput": "true", "difficulty": "Easy", "category": "Stacks"},
        {"title": "Daily Temperatures Next Warmer", "problemStatement": "Given an array of integers `temperatures` representing daily temperatures, return an array `answer` such that `answer[i]` is the number of days you have to wait until a warmer temperature. If no future warm day exists, keep `answer[i] == 0`.", "inputFormat": "Space-separated daily temperatures.", "outputFormat": "Answer array.", "constraints": "1 <= temperatures.length <= 10^5\n30 <= temperatures[i] <= 100", "sampleInput": "73 74 75 71 69 72 76 73", "sampleOutput": "1 1 4 2 1 1 0 0", "difficulty": "Medium", "category": "Stacks"},
        {"title": "Largest Rectangle in Histogram", "problemStatement": "Given an array of integers `heights` representing the histogram's bar heights where the width of each bar is 1, return the area of the largest rectangle in the histogram.", "inputFormat": "Space-separated heights.", "outputFormat": "Maximum rectangle area.", "constraints": "1 <= heights.length <= 10^5\n0 <= heights[i] <= 10^4", "sampleInput": "2 1 5 6 2 3", "sampleOutput": "10", "difficulty": "Hard", "category": "Stacks"},

        # ── Linked Lists ──────────────────────────────────────────────────────
        {"title": "Merge Two Sorted Linked Lists", "problemStatement": "You are given the heads of two sorted linked lists `list1` and `list2`. Merge the two lists into one sorted list and return its head.", "inputFormat": "Line 1: list1 elements. Line 2: list2 elements.", "outputFormat": "Merged sorted list.", "constraints": "0 <= list length <= 50\n-100 <= Node.val <= 100", "sampleInput": "1 2 4\n1 3 4", "sampleOutput": "1 1 2 3 4 4", "difficulty": "Easy", "category": "Linked Lists"},
        {"title": "Reverse Linked List", "problemStatement": "Given the head of a singly linked list, reverse the list, and return the reversed list.", "inputFormat": "Space-separated node values (head first).", "outputFormat": "Reversed linked list values.", "constraints": "0 <= nodes <= 5000\n-5000 <= Node.val <= 5000", "sampleInput": "1 2 3 4 5", "sampleOutput": "5 4 3 2 1", "difficulty": "Easy", "category": "Linked Lists"},
        {"title": "Detect Cycle in Linked List", "problemStatement": "Given the head of a linked list, determine if the linked list has a cycle in it. Return `true` if there is a cycle, otherwise `false`.", "inputFormat": "Space-separated values with optional cycle indication.", "outputFormat": "true or false", "constraints": "0 <= nodes <= 10^4", "sampleInput": "3 2 0 -4 (tail connects to index 1)", "sampleOutput": "true", "difficulty": "Easy", "category": "Linked Lists"},
        {"title": "Find Middle of Linked List", "problemStatement": "Given the head of a singly linked list, return the middle node of the linked list. If there are two middle nodes, return the second middle node.", "inputFormat": "Space-separated node values (head first).", "outputFormat": "Middle node value and remaining list.", "constraints": "1 <= nodes <= 100", "sampleInput": "1 2 3 4 5", "sampleOutput": "3 4 5", "difficulty": "Easy", "category": "Linked Lists"},

        # ── Trees ─────────────────────────────────────────────────────────────
        {"title": "Invert Binary Tree", "problemStatement": "Given the root of a binary tree, invert the tree (mirror image) and return its root.", "inputFormat": "Level-order traversal array of tree nodes.", "outputFormat": "Level-order traversal of inverted tree.", "constraints": "0 <= nodes <= 100\n-100 <= Node.val <= 100", "sampleInput": "4 2 7 1 3 6 9", "sampleOutput": "4 7 2 9 6 3 1", "difficulty": "Easy", "category": "Trees"},
        {"title": "Maximum Depth of Binary Tree", "problemStatement": "Given the root of a binary tree, return its maximum depth. The maximum depth is the number of nodes along the longest path from the root node down to the farthest leaf node.", "inputFormat": "Level-order traversal array.", "outputFormat": "Maximum depth integer.", "constraints": "0 <= nodes <= 10^4", "sampleInput": "3 9 20 null null 15 7", "sampleOutput": "3", "difficulty": "Easy", "category": "Trees"},
        {"title": "Validate Binary Search Tree", "problemStatement": "Given the root of a binary tree, determine if it is a valid binary search tree (BST).", "inputFormat": "Level-order traversal array.", "outputFormat": "true or false", "constraints": "1 <= nodes <= 10^4\n-2^31 <= Node.val <= 2^31 - 1", "sampleInput": "2 1 3", "sampleOutput": "true", "difficulty": "Medium", "category": "Trees"},
        {"title": "Lowest Common Ancestor BST", "problemStatement": "Given a binary search tree (BST), find the lowest common ancestor (LCA) node of two given nodes in the BST.", "inputFormat": "Line 1: Tree in level-order. Line 2: Node p, Node q.", "outputFormat": "LCA node value.", "constraints": "2 <= nodes <= 10^5", "sampleInput": "6 2 8 0 4 7 9\n2 8", "sampleOutput": "6", "difficulty": "Medium", "category": "Trees"},
        {"title": "Binary Tree Level Order Traversal", "problemStatement": "Given the root of a binary tree, return the level order traversal of its nodes' values (i.e., from left to right, level by level).", "inputFormat": "Level-order traversal array.", "outputFormat": "Level-by-level node values.", "constraints": "0 <= nodes <= 2000", "sampleInput": "3 9 20 null null 15 7", "sampleOutput": "[3]\n[9,20]\n[15,7]", "difficulty": "Medium", "category": "Trees"},

        # ── Graphs & BFS/DFS ──────────────────────────────────────────────────
        {"title": "Number of Islands Grid", "problemStatement": "Given an `m x n` 2D binary grid representing a map of '1's (land) and '0's (water), return the number of islands.", "inputFormat": "m and n followed by matrix rows of 1s and 0s.", "outputFormat": "Single integer count of islands.", "constraints": "1 <= m, n <= 300", "sampleInput": "1 1 0 0\n1 1 0 0\n0 0 1 0\n0 0 0 1", "sampleOutput": "3", "difficulty": "Medium", "category": "Graphs & BFS/DFS"},
        {"title": "Clone Graph Deep Copy", "problemStatement": "Given a reference of a node in a connected undirected graph, return a deep copy (clone) of the graph.", "inputFormat": "Adjacency list representation.", "outputFormat": "Adjacency list of cloned graph.", "constraints": "1 <= nodes <= 100\n1 <= Node.val <= 100", "sampleInput": "[[2,4],[1,3],[2,4],[1,3]]", "sampleOutput": "[[2,4],[1,3],[2,4],[1,3]]", "difficulty": "Medium", "category": "Graphs & BFS/DFS"},
        {"title": "Course Schedule Cycle Detection", "problemStatement": "There are `numCourses` courses and a list of `prerequisites`. Return `true` if you can finish all courses, `false` if there is a cycle.", "inputFormat": "Line 1: numCourses. Line 2: prerequisites as pairs.", "outputFormat": "true or false", "constraints": "1 <= numCourses <= 2000", "sampleInput": "2\n[[1,0]]", "sampleOutput": "true", "difficulty": "Medium", "category": "Graphs & BFS/DFS"},

        # ── Dynamic Programming ───────────────────────────────────────────────
        {"title": "Climbing Stairs Count Ways", "problemStatement": "You are climbing a staircase that takes `n` steps to reach the top. Each time you can climb 1 or 2 steps. In how many distinct ways can you climb to the top?", "inputFormat": "Single integer n.", "outputFormat": "Number of ways.", "constraints": "1 <= n <= 45", "sampleInput": "3", "sampleOutput": "3", "difficulty": "Easy", "category": "Dynamic Programming"},
        {"title": "House Robber Maximum Loot", "problemStatement": "You are a robber planning to rob houses along a street. Each house has a certain amount of money stashed; the only constraint is that adjacent houses have security systems connected. Return the maximum amount you can rob tonight.", "inputFormat": "Space-separated house values.", "outputFormat": "Maximum loot amount.", "constraints": "1 <= nums.length <= 100\n0 <= nums[i] <= 400", "sampleInput": "2 7 9 3 1", "sampleOutput": "12", "difficulty": "Medium", "category": "Dynamic Programming"},
        {"title": "Coin Change Minimum Coins", "problemStatement": "Given integer array `coins` of different denominations and integer `amount`, return the fewest coins needed to make up that amount. If it cannot be done, return `-1`.", "inputFormat": "Line 1: space-separated coins. Line 2: amount.", "outputFormat": "Minimum coins count or -1.", "constraints": "1 <= coins.length <= 12\n1 <= amount <= 10^4", "sampleInput": "1 2 5\n11", "sampleOutput": "3", "difficulty": "Medium", "category": "Dynamic Programming"},
        {"title": "Longest Increasing Subsequence", "problemStatement": "Given an integer array `nums`, return the length of the longest strictly increasing subsequence.", "inputFormat": "Space-separated array nums.", "outputFormat": "Length of LIS.", "constraints": "1 <= nums.length <= 2500", "sampleInput": "10 9 2 5 3 7 101 18", "sampleOutput": "4", "difficulty": "Hard", "category": "Dynamic Programming"},
        {"title": "Word Break Dictionary", "problemStatement": "Given a string `s` and a dictionary of strings `wordDict`, return `true` if `s` can be segmented into a space-separated sequence of dictionary words.", "inputFormat": "Line 1: string s. Line 2: dictionary words comma-separated.", "outputFormat": "true or false", "constraints": "1 <= s.length <= 300", "sampleInput": "leetcode\nleet,code", "sampleOutput": "true", "difficulty": "Medium", "category": "Dynamic Programming"},
        {"title": "Unique Paths Grid Count", "problemStatement": "There is a robot on an `m x n` grid. The robot can only move either down or right at any point in time. The robot is trying to reach the bottom-right corner. How many possible unique paths are there?", "inputFormat": "Two integers m and n.", "outputFormat": "Number of unique paths.", "constraints": "1 <= m, n <= 100", "sampleInput": "3 7", "sampleOutput": "28", "difficulty": "Medium", "category": "Dynamic Programming"},

        # ── Heap / Priority Queue ─────────────────────────────────────────────
        {"title": "Kth Largest Element", "problemStatement": "Given an integer array `nums` and an integer `k`, return the `k`th largest element in the array. Note that it is the kth largest element in sorted order, not the kth distinct element.", "inputFormat": "Line 1: space-separated nums. Line 2: k.", "outputFormat": "Kth largest element.", "constraints": "1 <= k <= nums.length <= 10^5", "sampleInput": "3 2 1 5 6 4\n2", "sampleOutput": "5", "difficulty": "Medium", "category": "Heap / Priority Queue"},
        {"title": "Merge K Sorted Lists", "problemStatement": "You are given an array of `k` linked-lists lists, each linked-list is sorted in ascending order. Merge all the linked-lists into one sorted linked-list and return it.", "inputFormat": "k lines, each with sorted list values.", "outputFormat": "Single merged sorted list.", "constraints": "k == lists.length\n0 <= k <= 10^4", "sampleInput": "1 4 5\n1 3 4\n2 6", "sampleOutput": "1 1 2 3 4 4 5 6", "difficulty": "Hard", "category": "Heap / Priority Queue"},

        # ── Backtracking ──────────────────────────────────────────────────────
        {"title": "Subsets Power Set", "problemStatement": "Given an integer array `nums` of unique elements, return all possible subsets (the power set). The solution set must not contain duplicate subsets.", "inputFormat": "Space-separated unique integers.", "outputFormat": "All subsets, one per line.", "constraints": "1 <= nums.length <= 10\n-10 <= nums[i] <= 10", "sampleInput": "1 2 3", "sampleOutput": "[]\n[1]\n[2]\n[1,2]\n[3]\n[1,3]\n[2,3]\n[1,2,3]", "difficulty": "Medium", "category": "Backtracking"},
        {"title": "Combination Sum Target", "problemStatement": "Given an array of distinct integers `candidates` and a target integer `target`, return a list of all unique combinations of `candidates` where the chosen numbers sum to `target`. You may use the same number an unlimited number of times.", "inputFormat": "Line 1: candidates. Line 2: target.", "outputFormat": "All combinations, one per line.", "constraints": "1 <= candidates.length <= 30\n1 <= target <= 40", "sampleInput": "2 3 6 7\n7", "sampleOutput": "[2,2,3]\n[7]", "difficulty": "Medium", "category": "Backtracking"},
        {"title": "Word Search Grid", "problemStatement": "Given an `m x n` board of characters and a string `word`, return `true` if the word exists in the grid. The word can be constructed from letters of sequentially adjacent cells (horizontal/vertical). Each cell may only be used once.", "inputFormat": "m x n grid rows then target word.", "outputFormat": "true or false", "constraints": "1 <= m, n <= 6\n1 <= word.length <= 15", "sampleInput": "ABCEFG\nSFCS\nADEE\nSEE", "sampleOutput": "true", "difficulty": "Medium", "category": "Backtracking"},
    ]

    # Shuffle and sample CODING_COUNT unique problems
    random.shuffle(full_pool)
    problems = full_pool[:CODING_COUNT]

    for p in problems:
        p["programmingLanguage"] = primary_lang
        p["leetcodeStyle"] = True

    return problems


def generate_aptitude_questions_ai(profile: Dict[str, Any]) -> List[Dict]:
    """Generate 25 aptitude MCQs via Groq AI with automatic heuristic fallback."""
    prompt = _build_aptitude_prompt(profile)
    try:
        raw = _call_groq(APTITUDE_SYSTEM_PROMPT, prompt, APTITUDE_MAX_TOKENS)
        questions = _parse_json_from_response(raw)
        return _validate_and_fix_mcq_list(questions, APTITUDE_COUNT, "aptitude")
    except Exception as exc:
        logger.warning(f"Groq AI aptitude generation notice ({exc}). Using curated 25 Aptitude question engine.")
        return generate_aptitude_questions_heuristic(profile)


def generate_technical_questions_ai(profile: Dict[str, Any]) -> List[Dict]:
    """Generate 25 technical MCQs via Groq AI with automatic heuristic fallback."""
    prompt = _build_technical_prompt(profile)
    try:
        raw = _call_groq(TECHNICAL_SYSTEM_PROMPT, prompt, TECHNICAL_MAX_TOKENS)
        questions = _parse_json_from_response(raw)
        return _validate_and_fix_mcq_list(questions, TECHNICAL_COUNT, "technical")
    except Exception as exc:
        logger.warning(f"Groq AI technical generation notice ({exc}). Using personalized 25 Technical question engine.")
        return generate_technical_questions_heuristic(profile)


def generate_coding_questions_ai(profile: Dict[str, Any]) -> List[Dict]:
    """Generate 15 coding problems via Groq AI with automatic heuristic fallback."""
    prompt = _build_coding_prompt(profile)
    try:
        raw = _call_groq(CODING_SYSTEM_PROMPT, prompt, CODING_MAX_TOKENS)
        questions = _parse_json_from_response(raw)
        return _validate_coding_list(questions)
    except Exception as exc:
        logger.warning(f"Groq AI coding generation notice ({exc}). Using personalized 15 Coding problem engine.")
        return generate_coding_questions_heuristic(profile)


# ---------------------------------------------------------------------------
# Prompts & Templates
# ---------------------------------------------------------------------------

APTITUDE_SYSTEM_PROMPT = (
    "You are a professional assessment designer creating aptitude questions for candidate evaluation. "
    "Return ONLY a raw JSON array — no markdown, no code fences, no commentary."
)

APTITUDE_USER_TEMPLATE = """
Generate exactly {count} aptitude MCQ questions for a candidate assessment.

Candidate experience level: {experience_level}

Question distribution:
- 8 Quantitative Aptitude (arithmetic, percentages, ratios, profit/loss, time/work)
- 9 Logical Reasoning (sequences, patterns, syllogisms, blood relations, arrangements)
- 5 Analytical Reasoning (data interpretation, Venn diagrams, puzzles)
- 3 Verbal Reasoning (reading comprehension, sentence completion, analogies)

Difficulty distribution:
- Easy: 5 questions
- Medium: 15 questions
- Hard: 5 questions

{experience_note}

Return ONLY a JSON array of exactly {count} objects:
[
  {{
    "question": "<question text>",
    "options": ["<A>", "<B>", "<C>", "<D>"],
    "correctAnswer": "<exact text of correct option>",
    "category": "<Quantitative|Logical|Analytical|Verbal>",
    "difficulty": "<Easy|Medium|Hard>",
    "explanation": "<brief explanation>"
  }}
]
""".strip()

TECHNICAL_SYSTEM_PROMPT = (
    "You are a senior software engineer creating technical assessment MCQs for candidate evaluation. "
    "Questions must be non-trivial, scenario-based, and test real-world understanding. "
    "Return ONLY a raw JSON array — no markdown, no code fences, no commentary."
)

TECHNICAL_USER_TEMPLATE = """
Generate exactly {count} technical MCQ questions personalized to this candidate's resume skills.

Candidate profile:
- Experience level: {experience_level}
- Programming languages: {languages}
- Frameworks: {frameworks}
- Databases: {databases}
- Tools: {tools}
- Domains: {domains}
- Cloud: {cloud}
- Projects: {projects}

CRITICAL rules:
1. Questions MUST relate to the candidate's actual listed skills — do NOT invent skills they don't have.
2. Do NOT ask trivial questions like "What is Python?" or "What is a database?"
3. Questions should test: understanding, debugging, architecture, tradeoffs, real-world scenarios.
4. Cover {count} different topics from the candidate's skill set (spread across technologies).
5. Difficulty: Easy 5, Medium 15, Hard 5.

Return ONLY a JSON array of exactly {count} objects:
[
  {{
    "question": "<scenario-based question text>",
    "options": ["<A>", "<B>", "<C>", "<D>"],
    "correctAnswer": "<exact text of correct option>",
    "technology": "<specific technology this question covers>",
    "category": "<category>",
    "difficulty": "<Easy|Medium|Hard>",
    "explanation": "<brief explanation>"
  }}
]
""".strip()

CODING_SYSTEM_PROMPT = (
    "You are a coding assessment designer. Create LeetCode-style coding problems. "
    "Problems must have complete problem statements, examples, and constraints. "
    "Return ONLY a raw JSON array — no markdown, no code fences, no commentary."
)

CODING_USER_TEMPLATE = """
Generate exactly {count} coding problems for a candidate assessment.

Candidate profile:
- Primary languages: {languages}
- Experience level: {experience_level}
- Domains: {domains}

Problem requirements:
- Create algorithmic problems solvable in any programming language
- Prefer problems relevant to the candidate's domain but algorithmically sound
- Include real problem statement, input/output format, constraints, sample test cases
- Difficulty: Easy 4, Medium 8, Hard 3

DSA topics to cover (select most relevant):
Arrays, Strings, Hashing, Two Pointers, Binary Search, Stacks, Queues, Trees, Graphs, Dynamic Programming, Greedy, Sorting, Linked Lists

Return ONLY a JSON array of exactly {count} objects:
[
  {{
    "title": "<problem title>",
    "problemStatement": "<full problem description>",
    "inputFormat": "<input format description>",
    "outputFormat": "<output format description>",
    "constraints": "<constraints like 1 <= n <= 10^5>",
    "sampleTestCases": [
      {{"input": "<example input>", "output": "<expected output>", "explanation": "<brief explanation>"}}
    ],
    "difficulty": "<Easy|Medium|Hard>",
    "category": "<DSA topic e.g. Arrays, Trees, DP>",
    "programmingLanguage": "{primary_language}",
    "tags": ["<tag1>", "<tag2>"],
    "leetcodeStyle": true
  }}
]
""".strip()


def _build_technical_prompt(profile: Dict[str, Any]) -> str:
    languages = ", ".join(profile.get("programming_languages", [])) or "General"
    frameworks = ", ".join(profile.get("frameworks", [])) or "None"
    databases = ", ".join(profile.get("databases", [])) or "None"
    tools = ", ".join(profile.get("tools", [])) or "None"
    domains = ", ".join(profile.get("domains", [])) or "General Software Development"
    cloud = ", ".join(profile.get("cloud_technologies", [])) or "None"
    projects = "; ".join(
        f"{p.get('name','?')} ({', '.join(p.get('technologies',[]))})"
        for p in profile.get("projects", [])[:3]
    ) or "None"
    experience_level = profile.get("experience_level", "Junior")

    return TECHNICAL_USER_TEMPLATE.format(
        count=TECHNICAL_COUNT,
        experience_level=experience_level,
        languages=languages,
        frameworks=frameworks,
        databases=databases,
        tools=tools,
        domains=domains,
        cloud=cloud,
        projects=projects,
    )


def _build_aptitude_prompt(profile: Dict[str, Any]) -> str:
    experience_level = profile.get("experience_level", "Junior")
    experience_note = ""
    if experience_level in ("Mid", "Senior"):
        experience_note = "The candidate is experienced — avoid trivially easy questions."
    elif experience_level == "Fresher":
        experience_note = "The candidate is a fresher — keep difficulty fair but not too easy."
    return APTITUDE_USER_TEMPLATE.format(
        count=APTITUDE_COUNT,
        experience_level=experience_level,
        experience_note=experience_note,
    )


def _build_coding_prompt(profile: Dict[str, Any]) -> str:
    languages = profile.get("programming_languages", [])
    primary_language = languages[0] if languages else "Python"
    all_languages = ", ".join(languages) if languages else "Python"
    domains = ", ".join(profile.get("domains", [])) or "General"
    experience_level = profile.get("experience_level", "Junior")
    return CODING_USER_TEMPLATE.format(
        count=CODING_COUNT,
        languages=all_languages,
        experience_level=experience_level,
        domains=domains,
        primary_language=primary_language,
    )


def _validate_and_fix_mcq_list(questions: List[Any], expected_count: int, q_type: str) -> List[Dict]:
    """Validate MCQ question list structure."""
    if not isinstance(questions, list):
        raise ValueError(f"AI returned non-list for {q_type} questions.")

    valid = []
    for q in questions:
        if not isinstance(q, dict):
            continue
        text = q.get("question") or q.get("problemStatement") or q.get("title")
        if not text:
            continue
        options = q.get("options", [])
        correct = q.get("correctAnswer") or q.get("correct_answer")
        if q_type != "coding" and (not isinstance(options, list) or len(options) < 2 or not correct):
            continue
        valid.append(q)

    if len(valid) < expected_count:
        raise ValueError(
            f"AI generated only {len(valid)} valid {q_type} questions (expected {expected_count})."
        )
    return valid[:expected_count]


def _validate_coding_list(questions: List[Any]) -> List[Dict]:
    """Validate coding problem list structure."""
    if not isinstance(questions, list):
        raise ValueError("AI returned non-list for coding problems.")
    valid = []
    for q in questions:
        if not isinstance(q, dict):
            continue
        if not q.get("title") or not q.get("problemStatement"):
            continue
        valid.append(q)
    if len(valid) < CODING_COUNT:
        raise ValueError(
            f"AI generated only {len(valid)} valid coding problems (expected {CODING_COUNT})."
        )
    return valid[:CODING_COUNT]


# ---------------------------------------------------------------------------
# Persist Generated Questions to DB
# ---------------------------------------------------------------------------

def _save_aptitude_questions(questions: List[Dict], user_id: str) -> List[ObjectId]:
    db = Database.get_db()
    ids = []
    now = datetime.now(timezone.utc)
    for q in questions:
        options = q.get("options", [])
        correct = q.get("correctAnswer") or q.get("correct_answer") or ""
        doc = AptitudeQuestion.create_question(
            category=q.get("category", "General Aptitude"),
            question=q["question"],
            options=options,
            correct_answer=correct,
            difficulty=q.get("difficulty", "Medium"),
            marks=1,
            explanation=q.get("explanation", ""),
            question_type="MCQ",
            tags=q.get("tags", []),
            created_by=user_id,
        )
        doc["isPersonalized"] = True
        doc["generatedForUser"] = user_id
        result = db.aptitude_questions.insert_one(doc)
        ids.append(result.inserted_id)
    return ids


def _save_technical_questions(questions: List[Dict], user_id: str) -> List[ObjectId]:
    db = Database.get_db()
    ids = []
    for q in questions:
        options = q.get("options", [])
        correct = q.get("correctAnswer") or q.get("correct_answer") or ""
        technology = q.get("technology", q.get("category", "General"))
        doc = TechnicalQuestion.create_question(
            technology=technology,
            category=q.get("category", technology),
            question=q["question"],
            options=options,
            correct_answer=correct,
            difficulty=q.get("difficulty", "Medium"),
            marks=1,
            explanation=q.get("explanation", ""),
            question_type="MCQ",
            tags=q.get("tags", []),
            created_by=user_id,
        )
        doc["isPersonalized"] = True
        doc["generatedForUser"] = user_id
        result = db.technical_questions.insert_one(doc)
        ids.append(result.inserted_id)
    return ids


def _save_coding_questions(questions: List[Dict], user_id: str) -> List[ObjectId]:
    db = Database.get_db()
    ids = []
    for q in questions:
        sample_tcs = q.get("sampleTestCases", [])
        if not isinstance(sample_tcs, list):
            sample_tcs = []
        doc = CodingQuestion.create_question(
            title=q["title"],
            problem_statement=q["problemStatement"],
            programming_language=q.get("programmingLanguage", "Python"),
            difficulty=q.get("difficulty", "Medium"),
            input_format=q.get("inputFormat", ""),
            output_format=q.get("outputFormat", ""),
            constraints=q.get("constraints", ""),
            sample_test_cases=sample_tcs,
            hidden_test_cases=[],
            marks=10,
            category=q.get("category", "Algorithms"),
            tags=q.get("tags", []),
            created_by=user_id,
        )
        doc["isPersonalized"] = True
        doc["generatedForUser"] = user_id
        doc["leetcodeStyle"] = q.get("leetcodeStyle", False)
        result = db.coding_questions.insert_one(doc)
        ids.append(result.inserted_id)
    return ids


# ---------------------------------------------------------------------------
# Assessment Creation / Persistence
# ---------------------------------------------------------------------------

def _create_personalized_assessment(
    user_id: str,
    apt_ids: List[ObjectId],
    tech_ids: List[ObjectId],
    cod_ids: List[ObjectId],
    profile: Dict[str, Any],
) -> ObjectId:
    """Create an assessment document in the existing assessments collection."""
    db = Database.get_db()
    experience_level = profile.get("experience_level", "Junior")
    languages = ", ".join(profile.get("programming_languages", [])[:3]) or "General"
    now = datetime.now(timezone.utc)

    total_marks = float(len(apt_ids) + len(tech_ids) + len(cod_ids) * 10)

    doc = Assessment.create_assessment(
        title=f"Personalized Assessment — {languages} ({experience_level})",
        assessment_type="Personalized",
        user_id=user_id,
        aptitude_questions=[str(i) for i in apt_ids],
        technical_questions=[str(i) for i in tech_ids],
        coding_questions=[str(i) for i in cod_ids],
        duration=120,
        total_marks=total_marks,
        created_by=user_id,
        instructions=[
            "This assessment is personalized based on your uploaded resume.",
            "Read all questions carefully before answering.",
            "Aptitude: 25 questions | Technical: 25 questions | Coding: 15 problems.",
            "Do not refresh the page — your progress is saved.",
        ],
        passing_percentage=40.0,
    )
    doc["isPersonalized"] = True
    doc["resumeSkills"] = profile.get("skills", [])
    doc["experienceLevel"] = experience_level

    result = db.assessments.insert_one(doc)
    return result.inserted_id


def get_or_create_personalized_assessment(
    user_id: str,
    profile: Dict[str, Any],
    profile_version: int,
    force_new: bool = False,
) -> Dict[str, Any]:
    """
    Returns an existing Pending/In-Progress personalized assessment for the user,
    or generates a new one if none exists (or force_new=True).
    """
    db = Database.get_db()

    if not force_new:
        existing = db.personalized_assessments.find_one({
            "userId": user_id,
            "profileVersion": profile_version,
            "status": {"$in": ["Pending", "In Progress"]},
        })
        if existing:
            assessment_id = str(existing["assessmentId"])
            logger.info(f"Reusing existing personalized assessment {assessment_id} for user {user_id}")
            return {
                "assessmentId": assessment_id,
                "isNew": False,
                "aptitudeCount": APTITUDE_COUNT,
                "technicalCount": TECHNICAL_COUNT,
                "codingCount": CODING_COUNT,
            }

    logger.info(f"Generating new personalized assessment for user {user_id}")

    apt_questions  = generate_aptitude_questions_ai(profile)
    tech_questions = generate_technical_questions_ai(profile)
    cod_questions  = generate_coding_questions_ai(profile)

    apt_ids  = _save_aptitude_questions(apt_questions, user_id)
    tech_ids = _save_technical_questions(tech_questions, user_id)
    cod_ids  = _save_coding_questions(cod_questions, user_id)

    assessment_id = _create_personalized_assessment(user_id, apt_ids, tech_ids, cod_ids, profile)

    now = datetime.now(timezone.utc)
    db.personalized_assessments.insert_one({
        "userId": user_id,
        "profileVersion": profile_version,
        "assessmentId": assessment_id,
        "status": "Pending",
        "aptitudeCount": len(apt_ids),
        "technicalCount": len(tech_ids),
        "codingCount": len(cod_ids),
        "createdAt": now,
        "updatedAt": now,
    })

    logger.info(
        f"Created personalized assessment {assessment_id} for user {user_id} "
        f"({len(apt_ids)} apt, {len(tech_ids)} tech, {len(cod_ids)} coding)"
    )
    return {
        "assessmentId": str(assessment_id),
        "isNew": True,
        "aptitudeCount": len(apt_ids),
        "technicalCount": len(tech_ids),
        "codingCount": len(cod_ids),
    }


# ---------------------------------------------------------------------------
# Candidate Profile CRUD
# ---------------------------------------------------------------------------

class ResumeService:
    """Service class for resume upload, analysis, and candidate profile management."""

    @classmethod
    def upload_and_analyze(
        cls,
        user_id: str,
        file_bytes: bytes,
        filename: str,
    ) -> Dict[str, Any]:
        """
        Upload a resume, extract text, analyze via Groq/heuristic, and store the skill profile.
        Returns the stored profile document.
        """
        try:
            # 1. Extract text
            try:
                resume_text = extract_resume_text(file_bytes, filename)
            except ValueError as exc:
                return {"success": False, "status_code": 400, "message": str(exc)}

            if len(resume_text.strip()) < 30:
                return {
                    "success": False,
                    "status_code": 422,
                    "message": "Resume appears to be empty or has no extractable text.",
                }

            # 2. Analyze via Groq AI (with heuristic fallback)
            skill_profile = analyze_resume_with_groq(resume_text)

            # 3. Persist to MongoDB
            db = Database.get_db()
            now = datetime.now(timezone.utc)
            existing = db.candidate_profiles.find_one({"userId": user_id})
            new_version = 1
            if existing:
                new_version = existing.get("resumeVersion", 0) + 1
                db.candidate_profiles.update_one(
                    {"userId": user_id},
                    {"$set": {
                        "resumeFilename": filename,
                        "resumeText": resume_text[:5000],
                        "skillProfile": skill_profile,
                        "resumeVersion": new_version,
                        "analyzedAt": now,
                        "updatedAt": now,
                    }},
                )
                updated = db.candidate_profiles.find_one({"userId": user_id})
            else:
                doc = {
                    "userId": user_id,
                    "resumeFilename": filename,
                    "resumeText": resume_text[:5000],
                    "skillProfile": skill_profile,
                    "resumeVersion": new_version,
                    "analyzedAt": now,
                    "createdAt": now,
                    "updatedAt": now,
                }
                db.candidate_profiles.insert_one(doc)
                updated = doc

            return {
                "success": True,
                "status_code": 200,
                "message": "Resume uploaded and analyzed successfully.",
                "data": cls._serialize_profile(updated),
            }

        except PyMongoError as db_err:
            logger.error(f"DB error in upload_and_analyze: {db_err}")
            return {"success": False, "status_code": 500, "message": "Database error."}
        except Exception as exc:
            logger.critical(f"Unexpected error in upload_and_analyze: {exc}", exc_info=True)
            return {"success": False, "status_code": 500, "message": "Internal server error."}

    @classmethod
    def get_resume_status(cls, user_id: str) -> Dict[str, Any]:
        """Return resume status: whether a resume exists and high-level summary."""
        try:
            db = Database.get_db()
            profile_doc = db.candidate_profiles.find_one({"userId": user_id})
            if not profile_doc:
                return {
                    "success": True,
                    "status_code": 200,
                    "data": {
                        "hasResume": False,
                        "analyzedAt": None,
                        "resumeFilename": None,
                        "resumeVersion": 0,
                        "profileSummary": None,
                    },
                }
            profile = profile_doc.get("skillProfile", {})
            summary = {
                "experienceLevel": profile.get("experience_level", ""),
                "topSkills": (profile.get("programming_languages", []) + profile.get("frameworks", []))[:6],
                "totalSkills": len(profile.get("skills", [])),
            }
            analyzed_at = profile_doc.get("analyzedAt")
            return {
                "success": True,
                "status_code": 200,
                "data": {
                    "hasResume": True,
                    "analyzedAt": analyzed_at.isoformat() if isinstance(analyzed_at, datetime) else str(analyzed_at),
                    "resumeFilename": profile_doc.get("resumeFilename"),
                    "resumeVersion": profile_doc.get("resumeVersion", 1),
                    "profileSummary": summary,
                },
            }
        except Exception as exc:
            logger.error(f"Error in get_resume_status: {exc}")
            return {"success": False, "status_code": 500, "message": "Internal server error."}

    @classmethod
    def get_skill_profile(cls, user_id: str) -> Dict[str, Any]:
        """Return the full structured skill profile for the candidate."""
        try:
            db = Database.get_db()
            doc = db.candidate_profiles.find_one({"userId": user_id})
            if not doc:
                return {"success": False, "status_code": 404, "message": "No resume found. Please upload your resume first."}
            return {
                "success": True,
                "status_code": 200,
                "data": cls._serialize_profile(doc),
            }
        except Exception as exc:
            logger.error(f"Error in get_skill_profile: {exc}")
            return {"success": False, "status_code": 500, "message": "Internal server error."}

    @classmethod
    def generate_assessment(cls, user_id: str, force_new: bool = False) -> Dict[str, Any]:
        """
        Generate (or retrieve existing) personalized assessment for the user.
        Returns the assessment ID and counts.
        """
        try:
            db = Database.get_db()
            profile_doc = db.candidate_profiles.find_one({"userId": user_id})
            if not profile_doc:
                return {
                    "success": False,
                    "status_code": 400,
                    "message": "No resume found. Please upload your resume before generating an assessment.",
                }
            profile = profile_doc.get("skillProfile", {})
            profile_version = profile_doc.get("resumeVersion", 1)

            result = get_or_create_personalized_assessment(
                user_id=user_id,
                profile=profile,
                profile_version=profile_version,
                force_new=force_new,
            )
            return {
                "success": True,
                "status_code": 200,
                "message": "Personalized assessment ready.",
                "data": result,
            }
        except Exception as exc:
            logger.critical(f"Unexpected error in generate_assessment: {exc}", exc_info=True)
            return {"success": False, "status_code": 500, "message": "Internal server error."}

    @classmethod
    def delete_resume(cls, user_id: str) -> Dict[str, Any]:
        """Delete the candidate's resume and profile (allows re-upload)."""
        try:
            db = Database.get_db()
            result = db.candidate_profiles.delete_one({"userId": user_id})
            if result.deleted_count == 0:
                return {"success": False, "status_code": 404, "message": "No resume found to delete."}
            return {"success": True, "status_code": 200, "message": "Resume deleted. You can upload a new resume."}
        except Exception as exc:
            logger.error(f"Error deleting resume: {exc}")
            return {"success": False, "status_code": 500, "message": "Internal server error."}

    @staticmethod
    def _serialize_profile(doc: Dict) -> Dict:
        """Convert a MongoDB profile document to a JSON-serializable dict."""
        out = {}
        for k, v in doc.items():
            if k == "_id":
                out["id"] = str(v)
            elif isinstance(v, ObjectId):
                out[k] = str(v)
            elif isinstance(v, datetime):
                out[k] = v.isoformat()
            else:
                out[k] = v
        return out
