# 📝 Full Stack Todo CRUD Application

A full-stack Todo CRUD application built using **React (JavaScript)**, **FastAPI**, and **MongoDB Atlas**. The application allows users to create, view, update, and delete todo items through a modern web interface.

---

## 🚀 Features

- ✅ Create Todo
- 📋 View All Todos
- ✏️ Edit Todo
- 🗑️ Delete Todo
- ✅ Mark Todo as Completed / Pending
- 🌐 RESTful API using FastAPI
- ☁️ MongoDB Atlas Database
- ⚡ Axios for API communication
- 📱 Responsive React Frontend

---

# 🛠️ Tech Stack

### Frontend

- React (JavaScript)
- Axios
- CSS

### Backend

- FastAPI
- Python
- PyMongo
- Pydantic
- Uvicorn

### Database

- MongoDB Atlas

---

# 📁 Project Structure

```
Sarang_Bahikar/
│
├── backend/
│   ├── app/
│   │   ├── crud.py
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── routes.py
│   │   ├── schemas.py
│   │   └── __init__.py
│   │
│   ├── requirements.txt
│   ├── .env
│   └── venv/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── TodoForm.js
│   │   │   ├── TodoItem.js
│   │   │   └── TodoList.js
│   │   │
│   │   ├── services/
│   │   │   └── api.js
│   │   │
│   │   ├── styles/
│   │   │   ├── App.css
│   │   │   ├── TodoForm.css
│   │   │   ├── TodoItem.css
│   │   │   └── TodoList.css
│   │   │
│   │   ├── App.js
│   │   └── index.js
│   │
│   ├── package.json
│   └── node_modules/
│
└── README.md
```

---

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone <repository-url>
```

---

## 2. Backend Setup

Navigate to backend

```bash
cd backend
```

Create virtual environment

```bash
python -m venv venv
```

Activate virtual environment

### Windows

```bash
venv\Scripts\activate
```

### macOS / Linux

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

## 3. Create Environment File

Create a `.env` file inside the backend folder.

Example:

```env
MONGODB_URI=your_mongodb_connection_string
DATABASE_NAME=todo_app
```

---

## 4. Start Backend

```bash
uvicorn app.main:app --reload
```

Backend runs on

```
http://127.0.0.1:8000
```

Swagger Documentation

```
http://127.0.0.1:8000/docs
```

---

# Frontend Setup

Navigate to frontend

```bash
cd frontend
```

Install dependencies

```bash
npm install
```

Start React

```bash
npm start
```

Frontend runs on

```
http://localhost:3000
```

---

# 📡 API Endpoints

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | `/` | Welcome API |
| POST | `/todos` | Create Todo |
| GET | `/todos` | Get All Todos |
| GET | `/todos/{id}` | Get Todo by ID |
| PUT | `/todos/{id}` | Update Todo |
| DELETE | `/todos/{id}` | Delete Todo |

---

# 📸 Screenshots

Add screenshots here after completing the project.

Example:

```
screenshots/
│
├── home.png
├── add-todo.png
├── edit-todo.png
└── completed-todo.png
```

---

# 🔮 Future Improvements

- User Authentication
- Search Todos
- Filter by Status
- Due Dates
- Categories
- Priority Levels
- Dark Mode
- Pagination

---

# 👨‍💻 Author

**Sarang Bahikar**

Built as part of a Full Stack CRUD internship assignment using React, FastAPI, and MongoDB Atlas.