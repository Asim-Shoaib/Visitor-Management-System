import React, { useState, useEffect } from 'react'
import api from '../services/api'
import { toast } from 'react-toastify'
import { useData } from '../contexts/DataContext'

const SalaryCalculation = () => {
  const { employees } = useData()
  const [selectedEmployee, setSelectedEmployee] = useState('')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [salaryData, setSalaryData] = useState(null)
  const [loading, setLoading] = useState(false)

  // Set default date range (last 30 days)
  useEffect(() => {
    const today = new Date()
    const thirtyDaysAgo = new Date(today)
    thirtyDaysAgo.setDate(today.getDate() - 30)
    
    setEndDate(today.toISOString().split('T')[0])
    setStartDate(thirtyDaysAgo.toISOString().split('T')[0])
  }, [])

  const handleCalculate = async (e) => {
    e.preventDefault()
    
    if (!selectedEmployee) {
      toast.error('Please select an employee')
      return
    }
    
    if (!startDate || !endDate) {
      toast.error('Please select both start and end dates')
      return
    }
    
    if (new Date(startDate) > new Date(endDate)) {
      toast.error('Start date must be before end date')
      return
    }

    try {
      setLoading(true)
      const params = new URLSearchParams({
        start_date: startDate,
        end_date: endDate
      })
      
      const response = await api.get(`/site/employees/${selectedEmployee}/salary?${params.toString()}`)
      setSalaryData(response.data)
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to calculate salary')
      console.error(error)
      setSalaryData(null)
    } finally {
      setLoading(false)
    }
  }

  const handleExportExcel = async () => {
    if (!selectedEmployee || !salaryData) {
      toast.error('Please calculate salary first')
      return
    }

    try {
      const params = new URLSearchParams()
      if (startDate) params.append('start_date', startDate)
      if (endDate) params.append('end_date', endDate)
      
      const token = localStorage.getItem('token')
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/site/employees/${selectedEmployee}/salary/export?${params.toString()}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (!response.ok) {
        throw new Error('Export failed')
      }
      
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      
      // Get filename from Content-Disposition header or generate one
      const contentDisposition = response.headers.get('Content-Disposition')
      let filename = 'salary_report.xlsx'
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?(.+)"?/i)
        if (filenameMatch) {
          filename = filenameMatch[1]
        }
      }
      
      link.setAttribute('download', filename)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
      
      toast.success('Salary report exported successfully')
    } catch (error) {
      toast.error('Failed to export salary report')
      console.error(error)
    }
  }

  return (
    <div className="container">
      <h1>Salary Calculation</h1>
      
      <div className="card" style={{ marginBottom: '20px' }}>
        <h2>Calculate Employee Salary</h2>
        <form onSubmit={handleCalculate}>
          <div className="form-group">
            <label htmlFor="employee">Select Employee *</label>
            <select
              id="employee"
              value={selectedEmployee}
              onChange={(e) => setSelectedEmployee(e.target.value)}
              required
            >
              <option value="">Choose an employee</option>
              {employees.map((emp) => (
                <option key={emp.employee_id} value={emp.employee_id}>
                  {emp.name} {emp.department_name ? `(${emp.department_name})` : ''}
                </option>
              ))}
            </select>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
            <div className="form-group">
              <label htmlFor="start_date">Start Date *</label>
              <input
                type="date"
                id="start_date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="end_date">End Date *</label>
              <input
                type="date"
                id="end_date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                required
              />
            </div>
          </div>

          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Calculating...' : 'Calculate Salary'}
          </button>
        </form>
      </div>

      {salaryData && (
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <h2>Salary Report</h2>
            <button onClick={handleExportExcel} className="btn btn-success">
              Export to Excel
            </button>
          </div>

          <div style={{ marginBottom: '20px' }}>
            <h3>Summary</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px', marginTop: '15px' }}>
              <div style={{ padding: '15px', background: '#f8f9fa', borderRadius: '5px' }}>
                <strong>Employee:</strong> {salaryData.employee_name}
              </div>
              <div style={{ padding: '15px', background: '#f8f9fa', borderRadius: '5px' }}>
                <strong>Department:</strong> {salaryData.department || 'N/A'}
              </div>
              <div style={{ padding: '15px', background: '#f8f9fa', borderRadius: '5px' }}>
                <strong>Hourly Rate:</strong> ${salaryData.hourly_rate.toFixed(2)}
              </div>
              <div style={{ padding: '15px', background: '#f8f9fa', borderRadius: '5px' }}>
                <strong>Period:</strong> {salaryData.start_date} to {salaryData.end_date}
              </div>
              <div style={{ padding: '15px', background: '#e7f3ff', borderRadius: '5px' }}>
                <strong>Total Days Worked:</strong> {salaryData.total_days_worked}
              </div>
              <div style={{ padding: '15px', background: '#e7f3ff', borderRadius: '5px' }}>
                <strong>Total Hours:</strong> {salaryData.total_hours.toFixed(2)}
              </div>
              <div style={{ padding: '15px', background: '#d4edda', borderRadius: '5px' }}>
                <strong style={{ fontSize: '1.2rem' }}>Total Salary:</strong>
                <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#155724' }}>
                  ${salaryData.salary.toFixed(2)}
                </div>
              </div>
            </div>
          </div>

          {salaryData.daily_breakdown && salaryData.daily_breakdown.length > 0 && (
            <div>
              <h3>Daily Breakdown</h3>
              <div style={{ maxHeight: '400px', overflowY: 'auto', marginTop: '15px' }}>
                <table className="table">
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Sign-In</th>
                      <th>Sign-Out</th>
                      <th>Hours</th>
                      <th>Notes</th>
                    </tr>
                  </thead>
                  <tbody>
                    {salaryData.daily_breakdown.map((day, index) => (
                      <tr key={index}>
                        <td>{day.date}</td>
                        <td>{day.signin}</td>
                        <td>{day.signout}</td>
                        <td>{day.hours.toFixed(2)}</td>
                        <td>
                          {day.incomplete && (
                            <span style={{ color: '#dc3545', fontSize: '0.9rem' }}>
                              ⚠️ Incomplete (no sign-out)
                            </span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {(!salaryData.daily_breakdown || salaryData.daily_breakdown.length === 0) && (
            <p style={{ color: '#6c757d', fontStyle: 'italic' }}>
              No attendance records found for the selected period.
            </p>
          )}
        </div>
      )}
    </div>
  )
}

export default SalaryCalculation

