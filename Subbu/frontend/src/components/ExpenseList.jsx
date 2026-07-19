export default function ExpenseList({ expenses, onDelete, onEdit }) {
  if (expenses.length === 0) {
    return <p>No expenses yet.</p>;
  }

  return (
    <div className="expenses-list">
      {expenses.map((expense) => (
        <div key={expense.id} className="expense-item">
          <span>{expense.description}</span>
          <span>₹{expense.amount}</span>
          <div>
            <button onClick={() => onEdit(expense)} className="primary-btn" style={{marginRight: '10px', fontSize: '0.9rem'}}>
              Edit
            </button>
            <button onClick={() => onDelete(expense.id)} className="delete-btn">
              Delete
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
