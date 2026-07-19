import { useState, useEffect } from 'react';
import { expenseService } from './api/expenseService';
import Header from './components/Header';
import ExpenseForm from './components/ExpenseForm';
import ExpenseList from './components/ExpenseList';
import './index.css';

function App() {
  const [expenses, setExpenses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingExpense, setEditingExpense] = useState(null); // Track which expense we are editing

  // 1. Fetch expenses when the app loads
  useEffect(() => {
    fetchExpenses();
  }, []);

  const fetchExpenses = async () => {
    try {
      const data = await expenseService.getAll();
      setExpenses(data);
    } catch (error) {
      console.error('Error fetching expenses:', error);
    } finally {
      setLoading(false);
    }
  };

  // 2. Add a new expense (CREATE)
  const handleAddExpense = async (description, amount) => {
    try {
      const newExpense = await expenseService.create(description, amount);
      setExpenses([...expenses, newExpense]);
    } catch (error) {
      console.error('Error adding expense:', error);
    }
  };

  // 3. Update an existing expense (UPDATE)
  const handleUpdateExpense = async (id, description, amount) => {
    try {
      const updatedExpense = await expenseService.update(id, description, amount);
      setExpenses(expenses.map(exp => (exp.id === id ? updatedExpense : exp)));
    } catch (error) {
      console.error('Error updating expense:', error);
    }
  };

  // 4. Delete an expense (DELETE)
  const handleDelete = async (id) => {
    try {
      await expenseService.delete(id);
      setExpenses(expenses.filter(exp => exp.id !== id));
    } catch (error) {
      console.error('Error deleting expense:', error);
    }
  };

  // Calculate the total money spent
  const totalSpent = expenses.reduce((sum, exp) => sum + exp.amount, 0);

  return (
    <div className="app-container">
      <Header totalSpent={totalSpent} />
      
      <ExpenseForm 
        onAddExpense={handleAddExpense} 
        onUpdateExpense={handleUpdateExpense}
        editingExpense={editingExpense}
        setEditingExpense={setEditingExpense}
      />

      <ExpenseList 
        expenses={expenses} 
        loading={loading} 
        onDelete={handleDelete} 
        onEdit={setEditingExpense}
      />
    </div>
  );
}

export default App;
