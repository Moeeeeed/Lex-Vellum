import React, { useState, useEffect } from 'react';

const UserManagement = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  
  // New user form state
  const [newEmail, setNewEmail] = useState('');
  const [newFullName, setNewFullName] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [newRole, setNewRole] = useState('Editor');

  const fetchUsers = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/auth/users', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (!response.ok) throw new Error('Failed to fetch users');
      const data = await response.json();
      setUsers(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleAddUser = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:8000/api/auth/users', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          email: newEmail,
          full_name: newFullName,
          password: newPassword,
          role: newRole
        })
      });
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to add user');
      }
      setShowAddModal(false);
      setNewEmail('');
      setNewFullName('');
      setNewPassword('');
      fetchUsers();
    } catch (err) {
      alert(err.message);
    }
  };

  const handleDeleteUser = async (userId) => {
    if (!window.confirm('Are you sure you want to revoke access for this user?')) return;
    try {
      const response = await fetch(`http://localhost:8000/api/auth/users/${userId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (!response.ok) throw new Error('Failed to delete user');
      fetchUsers();
    } catch (err) {
      alert(err.message);
    }
  };

  if (loading) return <div className="p-4 text-center">Loading users...</div>;

  return (
    <div className="user-management">
      <div className="management-header">
        <h2>User Management</h2>
        <button className="btn btn-primary" onClick={() => setShowAddModal(true)}>+ Add New User</button>
      </div>

      {error && <div className="error-message">{error}</div>}

      <table className="user-table">
        <thead>
          <tr>
            <th>Full Name</th>
            <th>Email</th>
            <th>Role</th>
            <th>Joined</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {users.map(user => (
            <tr key={user.id}>
              <td>{user.full_name}</td>
              <td>{user.email}</td>
              <td><span className={`role-badge role-${user.role.toLowerCase()}`}>{user.role}</span></td>
              <td>{new Date(user.created_at).toLocaleDateString()}</td>
              <td>
                <button 
                  className="btn-revoke" 
                  onClick={() => handleDeleteUser(user.id)}
                  disabled={user.role === 'CEO'}
                >
                  Revoke Access
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {showAddModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h3>Add New Team Member</h3>
            <form onSubmit={handleAddUser}>
              <div className="input-group">
                <label>Full Name</label>
                <input type="text" value={newFullName} onChange={e => setNewFullName(e.target.value)} required />
              </div>
              <div className="input-group">
                <label>Email Address</label>
                <input type="email" value={newEmail} onChange={e => setNewEmail(e.target.value)} required />
              </div>
              <div className="input-group">
                <label>Temporary Password</label>
                <input type="text" value={newPassword} onChange={e => setNewPassword(e.target.value)} required />
              </div>
              <div className="input-group">
                <label>Role</label>
                <select value={newRole} onChange={e => setNewRole(e.target.value)}>
                  <option value="Editor">Editor (Upload & Edit)</option>
                  <option value="Approver">Approver (Review Only)</option>
                </select>
              </div>
              <div className="modal-actions">
                <button type="button" className="btn" onClick={() => setShowAddModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">Create Account</button>
              </div>
            </form>
          </div>
        </div>
      )}

      <style>{`
        .user-management {
          padding: 20px;
          background: #000;
          min-height: 100%;
        }
        .management-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 30px;
        }
        .user-table {
          width: 100%;
          border-collapse: collapse;
          border: 1px solid #333;
        }
        .user-table th, .user-table td {
          padding: 15px;
          text-align: left;
          border-bottom: 1px solid #222;
          font-size: 0.85rem;
        }
        .user-table th {
          background: #111;
          color: #888;
          text-transform: uppercase;
          letter-spacing: 1px;
          font-size: 0.7rem;
        }
        .role-badge {
          padding: 4px 8px;
          border-radius: 4px;
          font-size: 0.7rem;
          font-weight: 600;
          text-transform: uppercase;
        }
        .role-ceo { background: #fff; color: #000; }
        .role-editor { background: #333; color: #fff; }
        .role-approver { background: #222; color: #aaa; border: 1px solid #444; }
        
        .btn-revoke {
          background: none;
          border: 1px solid #ff5555;
          color: #ff5555;
          padding: 5px 10px;
          border-radius: 4px;
          font-size: 0.7rem;
          cursor: pointer;
          transition: all 0.2s;
        }
        .btn-revoke:hover:not(:disabled) {
          background: #ff5555;
          color: #fff;
        }
        .btn-revoke:disabled {
          opacity: 0.3;
          cursor: not-allowed;
          border-color: #666;
          color: #666;
        }

        .modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0,0,0,0.8);
          display: flex;
          justify-content: center;
          align-items: center;
          z-index: 1000;
        }
        .modal-content {
          background: #111;
          padding: 30px;
          border-radius: 8px;
          border: 1px solid #333;
          width: 100%;
          max-width: 400px;
        }
        .modal-actions {
          display: flex;
          justify-content: flex-end;
          gap: 10px;
          margin-top: 20px;
        }
      `}</style>
    </div>
  );
};

export default UserManagement;
