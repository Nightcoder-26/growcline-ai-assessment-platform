import { useState } from "react";
import "../styles/TodoItem.css";

function TodoItem({ todo, onDelete, onUpdate }) {
  const [isEditing, setIsEditing] = useState(false);

  const [title, setTitle] = useState(todo.title);
  const [description, setDescription] = useState(todo.description);
  const [completed, setCompleted] = useState(todo.completed);

  const handleSave = () => {
    onUpdate(todo.id, {
      title,
      description,
      completed,
    });

    setIsEditing(false);
  };

  const handleCancel = () => {
    setTitle(todo.title);
    setDescription(todo.description);
    setCompleted(todo.completed);

    setIsEditing(false);
  };

  if (isEditing) {
    return (
      <div className="todo-card edit-mode">
        <h3>Edit Todo</h3>

        <input
          className="edit-input"
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />

        <textarea
          className="edit-textarea"
          rows="3"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />

        <label className="checkbox-container">
          <input
            type="checkbox"
            checked={completed}
            onChange={(e) => setCompleted(e.target.checked)}
          />
          Completed
        </label>

        <div className="button-group">
          <button className="save-btn" onClick={handleSave}>
            💾 Save
          </button>

          <button className="cancel-btn" onClick={handleCancel}>
            Cancel
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="todo-card">
      <h3>{todo.title}</h3>

      <p>{todo.description}</p>

      <span
        className={
          todo.completed
            ? "status completed"
            : "status pending"
        }
      >
        {todo.completed ? "Completed" : "Pending"}
      </span>

      <div className="button-group">
        <button
          className="edit-btn"
          onClick={() => setIsEditing(true)}
        >
          ✏ Edit
        </button>

        <button
          className="delete-btn"
          onClick={() => onDelete(todo.id)}
        >
          🗑 Delete
        </button>
      </div>
    </div>
  );
}

export default TodoItem;