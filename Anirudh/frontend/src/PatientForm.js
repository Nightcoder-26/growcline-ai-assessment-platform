import React, { useState, useEffect } from "react";

const EMPTY = {
  first_name: "", last_name: "", date_of_birth: "",
  gender: "", email: "", phone: "", address: "", medical_history: ""
};

function PatientForm({ patient, onSave, onClose }) {
  const [form, setForm] = useState(EMPTY);

  useEffect(() => {
    setForm(patient ? { ...patient } : EMPTY);
  }, [patient]);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(form, patient?.id);
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{patient ? "Edit Patient" : "Add Patient"}</h2>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>

        <form onSubmit={handleSubmit} className="form">
          <div className="form-row">
            <div className="form-group">
              <label>First Name *</label>
              <input name="first_name" value={form.first_name} onChange={handleChange} required />
            </div>
            <div className="form-group">
              <label>Last Name *</label>
              <input name="last_name" value={form.last_name} onChange={handleChange} required />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Date of Birth</label>
              <input type="date" name="date_of_birth" value={form.date_of_birth || ""} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label>Gender</label>
              <select name="gender" value={form.gender || ""} onChange={handleChange}>
                <option value="">Select</option>
                <option>Male</option>
                <option>Female</option>
                <option>Other</option>
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Email</label>
              <input type="email" name="email" value={form.email || ""} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label>Phone</label>
              <input name="phone" value={form.phone || ""} onChange={handleChange} />
            </div>
          </div>

          <div className="form-group">
            <label>Address</label>
            <input name="address" value={form.address || ""} onChange={handleChange} />
          </div>

          <div className="form-group">
            <label>Medical History</label>
            <textarea name="medical_history" value={form.medical_history || ""} onChange={handleChange} rows={3} />
          </div>

          <div className="form-actions">
            <button type="button" className="btn-cancel" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn-primary">{patient ? "Update" : "Add Patient"}</button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default PatientForm;
