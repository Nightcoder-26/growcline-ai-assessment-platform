export default function Header({ totalSpent }) {
  return (
    <div className="header">
      <h1>Expense Tracker</h1>
      <h2>Total Expenses: ₹{totalSpent}</h2>
    </div>
  );
}
