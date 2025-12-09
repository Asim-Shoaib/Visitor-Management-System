import React, { useState, useEffect } from 'react'
import api from '../services/api'
import { toast } from 'react-toastify'

const VisitLogs = () => {
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(false)
  const [filters, setFilters] = useState({
    startDate: '',
    endDate: '',
    action: ''
  })

  useEffect(() => {
    fetchLogs()
  }, [])

  const fetchLogs = async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      if (filters.startDate) params.append('start_date', filters.startDate)
      if (filters.endDate) params.append('end_date', filters.endDate)
      if (filters.action) params.append('action', filters.action)
      
      const response = await api.get(`/logs/access?${params.toString()}`)
      setLogs(response.data.logs || [])
    } catch (error) {
      toast.error('Failed to fetch logs')
      console.error(error)
      setLogs([])
    } finally {
      setLoading(false)
    }
  }

  const handleFilterChange = (e) => {
    setFilters({
      ...filters,
      [e.target.name]: e.target.value
    })
  }

  const handleApplyFilters = () => {
    fetchLogs()
  }

  const handleExportExcel = async () => {
    try {
      const params = new URLSearchParams()
      if (filters.startDate) params.append('start_date', filters.startDate)
      if (filters.endDate) params.append('end_date', filters.endDate)
      if (filters.action) params.append('action', filters.action)
      
      // Use fetch directly for blob response
      const token = localStorage.getItem('token')
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/logs/export?${params.toString()}`, {
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
      let filename = 'access_logs.xlsx'
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?(.+)"?/i)
        if (filenameMatch) {
          filename = filenameMatch[1]
        }
      } else {
        // Generate filename if not provided
        if (filters.startDate && filters.endDate) {
          filename = `access_logs_${filters.startDate}_to_${filters.endDate}.xlsx`
        } else if (filters.startDate) {
          filename = `access_logs_from_${filters.startDate}.xlsx`
        } else if (filters.endDate) {
          filename = `access_logs_until_${filters.endDate}.xlsx`
        }
      }
      
      link.setAttribute('download', filename)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
      
      toast.success('Excel file downloaded successfully')
    } catch (error) {
      toast.error('Failed to export logs to Excel')
      console.error(error)
    }
  }

  const handleFlagVisitor = async (visitorId, reason) => {
    const reasonInput = prompt('Enter reason for flagging this visitor:', reason || '')
    if (!reasonInput) return

    try {
      await api.post('/alerts/flag', {
        visitor_id: visitorId,
        reason: reasonInput
      })
      toast.success('Visitor flagged successfully')
      fetchLogs()
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to flag visitor')
      console.error(error)
    }
  }

  return (
    <div className="container">
      <h1>Visit Logs</h1>
      
      <div className="card">
        <h2>Filters</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px', marginBottom: '20px' }}>
          <div className="form-group">
            <label htmlFor="startDate">Start Date</label>
            <input
              type="date"
              id="startDate"
              name="startDate"
              value={filters.startDate}
              onChange={handleFilterChange}
            />
          </div>
          <div className="form-group">
            <label htmlFor="endDate">End Date</label>
            <input
              type="date"
              id="endDate"
              name="endDate"
              value={filters.endDate}
              onChange={handleFilterChange}
            />
          </div>
          <div className="form-group">
            <label htmlFor="action">Action Type</label>
            <select
              id="action"
              name="action"
              value={filters.action}
              onChange={handleFilterChange}
            >
              <option value="">All</option>
              <option value="login">Login</option>
              <option value="visitor_checkin">Visitor Check-In</option>
              <option value="visitor_checkout">Visitor Check-Out</option>
              <option value="generate_visitor_qr">Generate Visitor QR</option>
              <option value="scan_employee_qr">Scan Employee QR</option>
            </select>
          </div>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button onClick={handleApplyFilters} className="btn btn-primary">
            Apply Filters
          </button>
          <button onClick={handleExportExcel} className="btn btn-success">
            Export to Excel
          </button>
        </div>
      </div>

      <div className="card">
        <h2>Access Logs</h2>
        {loading ? (
          <div className="loading"><div className="spinner"></div></div>
        ) : logs.length === 0 ? (
          <p>No logs found for the selected filters.</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>User ID</th>
                <th>Action</th>
                <th>Details</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log, index) => (
                <tr key={index}>
                  <td>{new Date(log.timestamp).toLocaleString()}</td>
                  <td>{log.user_id}</td>
                  <td>{log.action}</td>
                  <td>{log.details}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

export default VisitLogs


