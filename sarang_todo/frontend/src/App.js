import { useEffect, useState } from "react";
import API from "./services/api";
import TodoForm from "./components/TodoForm";
import TodoList from "./components/TodoList";
import "./styles/App.css";

function App() {
  const [todos, setTodos] = useState([]);

  // Fetch all todos when the app loads
  useEffect(() => {
    fetchTodos();
  }, []);

  // Fetch all todos
  const fetchTodos = async () => {
    try {
      const response = await API.get("/todos");
      setTodos(response.data);
    } catch (error) {
      console.error("Error fetching todos:", error);
    }
  };

  // Add todo
  const addTodo = async (todo) => {
    try {
      await API.post("/todos", todo);
      fetchTodos();
    } catch (error) {
      console.error("Error adding todo:", error);
    }
  };

  // Update todo
  const updateTodo = async (id, updatedTodo) => {
    try {
      await API.put(`/todos/${id}`, updatedTodo);
      fetchTodos();
    } catch (error) {
      console.error("Error updating todo:", error);
    }
  };

  // Delete todo
  const deleteTodo = async (id) => {
    try {
      await API.delete(`/todos/${id}`);
      fetchTodos();
    } catch (error) {
      console.error("Error deleting todo:", error);
    }
  };

  return (
    <div className="app-container">
      <h1 className="app-title">📝 Todo Manager</h1>

      <TodoForm onAddTodo={addTodo} />

      <h2 className="section-title">Todo List</h2>

      <TodoList
        todos={todos}
        onDelete={deleteTodo}
        onUpdate={updateTodo}
      />
    </div>
  );
}

export default App;