import TodoItem from "./TodoItem";
import "../styles/TodoList.css";

function TodoList({ todos, onDelete, onUpdate }) {
  return (
    <div className="todo-list">
      {todos.length === 0 ? (
        <p>No Todos Found</p>
      ) : (
        todos.map((todo) => (
          <TodoItem
            key={todo.id}
            todo={todo}
            onDelete={onDelete}
            onUpdate={onUpdate}
          />
        ))
      )}
    </div>
  );
}

export default TodoList;