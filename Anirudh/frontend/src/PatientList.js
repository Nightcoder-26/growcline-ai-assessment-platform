import React from "react";

function PatientList({ patients, onEdit, onDelete }) {
  if (patients.length === 0) {
    return <p className="empty">No patients found. Click "Add Patient" to get started.</p>;
  }

  return (
    <div className="table-wrapper">
      <table className="table">
        <thead>
          <tr>
            <th>#</th>
            <th>Name</th>
            <th>Date of Birth</th>
            <th>Gender</th>
            <th>Email</th>
            <th>Phone</th>
            <th>Address</th>
            <th>Medical History</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {patients.map((p) => (
            <tr key={p.id}>
              <td>{p.id}</td>
              <td>{p.first_name} {p.last_name}</td>
              <td>{p.date_of_birth || "—"}</td>
              <td>{p.gender || "—"}</td>
              <td>{p.email || "—"}</td>
              <td>{p.phone || "—"}</td>
              <td>{p.address || "—"}</td>
              <td>{p.medical_history || "—"}</td>
              <td>
                <button className="btn-edit" onClick={() => onEdit(p)}>Edit</button>
                <button className="btn-delete" onClick={() => onDelete(p.id)}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default PatientList;
