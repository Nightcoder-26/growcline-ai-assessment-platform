import React, { useState, useEffect } from "react";
import PatientList from "./PatientList";
import PatientForm from "./PatientForm";
import "./App.css";

const API = "http://localhost:8000/patients";

function App() {
  const [patients, setPatients] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [editPatient, setEditPatient] = useState(null);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState(null);

  const showToast = (msg, type = "success") => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3000);
  };

  const fetchPatients = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}?search=${search}`);
      const data = await res.json();
      setPatients(data);
    } catch {
      showToast("Failed to connect to server", "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPatients();
  }, [search]);

  const handleSave = async (formData, id) => {
    const url = id ? `${API}/${id}` : `${API}/`;
    const method = id ? "PUT" : "POST";
    try {
      const res = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });
      if (!res.ok) {
        const err = await res.json();
        showToast(err.detail || "Error saving patient", "error");
        return;
      }
      showToast(id ? "Patient updated!" : "Patient added!");
      setShowForm(false);
      setEditPatient(null);
      fetchPatients();
    } catch {
      showToast("Server error", "error");
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Delete this patient?")) return;
    await fetch(`${API}/${id}`, { method: "DELETE" });
    showToast("Patient deleted!");
    fetchPatients();
  };

  const handleEdit = (patient) => {
    setEditPatient(patient);
    setShowForm(true);
  };

  return (
    <div className="app">
      {toast && <div className={`toast ${toast.type}`}>{toast.msg}</div>}

      <header className="header">
        <div className="header-content">
          <h1>🏥 Patient Management</h1>
          <button className="btn-primary" onClick={() => { setEditPatient(null); setShowForm(true); }}>
            + Add Patient
          </button>
        </div>
      </header>

      <main className="main">
        <input
          className="search-input"
          placeholder="🔍 Search by name or email..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />

        {loading ? (
          <p className="loading">Loading...</p>
        ) : (
          <PatientList patients={patients} onEdit={handleEdit} onDelete={handleDelete} />
        )}
      </main>

      {showForm && (
        <PatientForm
          patient={editPatient}
          onSave={handleSave}
          onClose={() => { setShowForm(false); setEditPatient(null); }}
        />
      )}
    </div>
  );
}

export default App;
