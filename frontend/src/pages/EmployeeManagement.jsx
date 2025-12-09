import React, { useState, useEffect } from 'react'
import api from '../services/api'
import { toast } from 'react-toastify'
import { useData } from '../contexts/DataContext'

const EmployeeManagement = () => {
  const { employees, refreshData } = useData()
  const [departments, setDepartments] = useState([])
  const [loading, setLoading] = useState(false)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    hourly_rate: '',
    department_id: ''
  })

  useEffect(() => {
    fetchDepartments()
  }, [])

  const fetchDepartments = async () => {
    try {
      const response = await api.get('/site/departments')
      setDepartments(response.data.departments || [])
    } catch (error) {
      toast.error('Failed to fetch departments')
      console.error(error)
    }
  }

  const handleCreateEmployee = async (e) => {
    e.preventDefault()
    
    // Validate inputs
    if (!formData.name.trim()) {
      toast.error('Name is required')
      return
    }
    
    if (!formData.hourly_rate || parseFloat(formData.hourly_rate) < 0) {
      toast.error('Hourly rate must be a non-negative number')
      return
    }
    
    if (!formData.department_id) {
      toast.error('Department is required')
      return
    }

    try {
      const payload = {
        name: formData.name.trim(),
        hourly_rate: parseFloat(formData.hourly_rate),
        department_id: parseInt(formData.department_id)
      }
      
      await api.post('/site/employees/create', payload)
      toast.success('Employee created successfully')
      setFormData({ name: '', hourly_rate: '', department_id: '' })
      setShowCreateForm(false)
      refreshData() // Refresh employee list from context
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create employee')
      console.error(error)
    }
  }

  return (
    <div className="container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1>Employee Management</h1>
        <button 
          onClick={() => setShowCreateForm(!showCreateForm)} 
          className="btn btn-primary"
        >
          {showCreateForm ? 'Cancel' : 'Add New Employee'}
        </button>
      </div>

      {showCreateForm && (
        <div className="card" style={{ marginBottom: '20px' }}>
          <h2>Add New Employee</h2>
          <form onSubmit={handleCreateEmployee}>
            <div className="form-group">
              <label htmlFor="name">Name *</label>
              <input
                type="text"
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
                minLength={2}
                maxLength={100}
                placeholder="Employee full name"
              />
            </div>

            <div className="form-group">
              <label htmlFor="hourly_rate">Hourly Rate *</label>
              <input
                type="number"
                id="hourly_rate"
                value={formData.hourly_rate}
                onChange={(e) => setFormData({ ...formData, hourly_rate: e.target.value })}
                required
                min="0"
                step="0.01"
                placeholder="0.00"
              />
            </div>

            <div className="form-group">
              <label htmlFor="department_id">Department *</label>
              <select
                id="department_id"
                value={formData.department_id}
                onChange={(e) => setFormData({ ...formData, department_id: e.target.value })}
                required
              >
                <option value="">Select a department</option>
                {departments.map((dept) => (
                  <option key={dept.department_id} value={dept.department_id}>
                    {dept.name}
                  </option>
                ))}
              </select>
            </div>

            <button type="submit" className="btn btn-success">
              Create Employee
            </button>
          </form>
        </div>
      )}

      <div className="card">
        <h2>All Employees ({employees.length})</h2>
        {loading ? (
          <div className="loading"><div className="spinner"></div></div>
        ) : employees.length === 0 ? (
          <p>No employees found</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Department</th>
                <th>Hourly Rate</th>
              </tr>
            </thead>
            <tbody>
              {employees.map((employee) => (
                <tr key={employee.employee_id}>
                  <td>{employee.employee_id}</td>
                  <td>{employee.name}</td>
                  <td>{employee.department_name || 'N/A'}</td>
                  <td>${parseFloat(employee.hourly_rate || 0).toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

export default EmployeeManagement

