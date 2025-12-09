import React, { useState, useEffect } from 'react'
import api from '../services/api'
import { toast } from 'react-toastify'

const UserManagement = () => {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(false)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    role_name: 'security'
  })

  useEffect(() => {
    fetchUsers()
  }, [])

  const fetchUsers = async () => {
    try {
      setLoading(true)
      const response = await api.get('/users/list')
      setUsers(response.data.users || [])
    } catch (error) {
      toast.error('Failed to fetch users')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateUser = async (e) => {
    e.preventDefault()
    try {
      await api.post('/users/create', formData)
      toast.success('User created successfully')
      setFormData({ username: '', password: '', role_name: 'security' })
      setShowCreateForm(false)
      fetchUsers()
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create user')
      console.error(error)
    }
  }

  const handleDeleteUser = async (userId) => {
    if (!window.confirm('Are you sure you want to deactivate this user?')) {
      return
    }

    try {
      await api.delete(`/users/${userId}`)
      toast.success('User deactivated successfully')
      fetchUsers()
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to deactivate user')
      console.error(error)
    }
  }

  return (
    <div className="container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1>User Management</h1>
        <button 
          onClick={() => setShowCreateForm(!showCreateForm)} 
          className="btn btn-primary"
        >
          {showCreateForm ? 'Cancel' : 'Create New User'}
        </button>
      </div>

      {showCreateForm && (
        <div className="card" style={{ marginBottom: '20px' }}>
          <h2>Create New User</h2>
          <form onSubmit={handleCreateUser}>
            <div className="form-group">
              <label htmlFor="username">Username *</label>
              <input
                type="text"
                id="username"
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">Password *</label>
              <input
                type="password"
                id="password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                required
                minLength={6}
              />
            </div>

            <div className="form-group">
              <label htmlFor="role_name">Role *</label>
              <select
                id="role_name"
                value={formData.role_name}
                onChange={(e) => setFormData({ ...formData, role_name: e.target.value })}
                required
              >
                <option value="security">Security</option>
                <option value="admin">Admin</option>
              </select>
            </div>

            <button type="submit" className="btn btn-success">
              Create User
            </button>
          </form>
        </div>
      )}

      <div className="card">
        <h2>All Users ({users.length})</h2>
        {loading ? (
          <div className="loading"><div className="spinner"></div></div>
        ) : users.length === 0 ? (
          <p>No users found</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Username</th>
                <th>Role</th>
                <th>Created At</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.user_id}>
                  <td>{user.user_id}</td>
                  <td>{user.username}</td>
                  <td>
                    <span style={{
                      padding: '4px 8px',
                      borderRadius: '4px',
                      background: user.role_name === 'admin' ? '#dc3545' : '#007bff',
                      color: 'white',
                      fontSize: '0.85rem'
                    }}>
                      {user.role_name}
                    </span>
                  </td>
                  <td>{new Date(user.created_at).toLocaleString()}</td>
                  <td>
                    <button
                      onClick={() => handleDeleteUser(user.user_id)}
                      className="btn btn-danger"
                      style={{ padding: '5px 10px', fontSize: '0.9rem' }}
                    >
                      Deactivate
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

export default UserManagement

