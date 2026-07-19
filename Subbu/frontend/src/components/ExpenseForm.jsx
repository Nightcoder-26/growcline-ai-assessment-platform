import { useState, useEffect } from 'react';

export default function ExpenseForm({ onAddExpense, onUpdateExpense, editingExpense, setEditingExpense }) {
  const [description, setDescription] = useState('');
  const [amount, setAmount] = useState('');

  // When clicking 'Edit', fill the form with the existing data
  useEffect(() => {
    if (editingExpense) {
      setDescription(editingExpense.description);
      setAmount(editingExpense.amount);
    }
  }, [editingExpense]);

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (editingExpense) {
      onUpdateExpense(editingExpense.id, description, amount);
      setEditingExpense(null); // Exit edit mode
    } else {
      onAddExpense(description, amount);
    }
    
    // Clear form
    setDescription('');
    setAmount('');
  };

  const handleCancel = () => {
    setEditingExpense(null);
    setDescription('');
    setAmount('');
  };

  return (
    <form onSubmit={handleSubmit} className="add-form">
      <input
        type="text"
        placeholder="What did you buy?"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        required
      />
      <input
        type="number"
        placeholder="Amount"
        value={amount}
        onChange={(e) => setAmount(e.target.value)}
        required
      />
      <button type="submit" className="primary-btn">
        {editingExpense ? 'Update' : 'Add'}
      </button>
      {editingExpense && (
        <button type="button" onClick={handleCancel} className="delete-btn" style={{marginLeft: '10px'}}>
          Cancel
        </button>
      )}
    </form>
  );
}
