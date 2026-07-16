import { useState } from "react";
import "../styles/TodoForm.css";

function TodoForm({ onAddTodo }) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!title.trim() || !description.trim()) {
      alert("Please fill all fields.");
      return;
    }

    onAddTodo({
      title,
      description,
    });

    setTitle("");
    setDescription("");
  };

  return (
    <div className="todo-form-card">
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Title</label>

          <input
            type="text"
            placeholder="Enter todo title..."
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
        </div>

        <div className="form-group">
          <label>Description</label>

          <textarea
            rows="4"
            placeholder="Enter todo description..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </div>

        <button className="add-btn" type="submit">
          ➕ Add Todo
        </button>
      </form>
    </div>
  );
}

export default TodoForm;