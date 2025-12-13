import React, { useState, useEffect } from 'react'
import api from '../services/api'
import { toast } from 'react-toastify'

const EmployeeQR = () => {
  const [employeeId, setEmployeeId] = useState('')
  const [employees, setEmployees] = useState([])
  const [qrData, setQrData] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchEmployees()
  }, [])

  const fetchEmployees = async () => {
    try {
      const response = await api.get('/site/employees')
      setEmployees(response.data.employees || [])
    } catch (error) {
      console.error('Failed to fetch employees:', error)
      toast.error('Failed to load employees list')
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!employeeId) {
      toast.error('Please select an employee')
      return
    }

    setLoading(true)
    try {
      const response = await api.post('/qr/generate-employee', {
        employee_id: parseInt(employeeId)
      })
      setQrData(response.data)
      toast.success('Employee QR code generated successfully!')
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to generate QR code')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const downloadQR = () => {
    if (qrData?.code_value) {
      // Construct download URL for employee QR
      const qrId = qrData.emp_qr_id
      const downloadUrl = `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/qr/download/employee/${qrId}`
      window.open(downloadUrl, '_blank')
    }
  }

  return (
    <div className="container">
      <h1>Employee QR Code Management</h1>
      
      <div className="card">
        <h2>Generate Employee QR Code</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="employee_id">Select Employee *</label>
            <select
              id="employee_id"
              value={employeeId}
              onChange={(e) => setEmployeeId(e.target.value)}
              required
              style={{ width: '100%', padding: '10px', fontSize: '1rem' }}
            >
              <option value="">-- Select Employee --</option>
              {employees.map(emp => (
                <option key={emp.employee_id} value={emp.employee_id}>
                  {emp.name} {emp.department_name ? `(${emp.department_name})` : ''} - ID: {emp.employee_id}
                </option>
              ))}
            </select>
            {employees.length === 0 && (
              <p style={{ color: '#e74c3c', fontSize: '0.9rem', marginTop: '5px' }}>
                No employees found. Please add employees to the database first.
              </p>
            )}
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading || !employeeId}
            style={{ marginTop: '15px' }}
          >
            {loading ? 'Generating...' : 'Generate QR Code'}
          </button>
        </form>

        {qrData && (
          <div style={{ marginTop: '30px', padding: '20px', background: '#f8f9fa', borderRadius: '8px', border: '2px solid #28a745' }}>
            <h3 style={{ color: '#28a745', marginBottom: '15px' }}>✓ QR Code Generated Successfully</h3>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '15px', marginBottom: '20px' }}>
              <div>
                <strong>Employee ID:</strong> {qrData.employee_id}
              </div>
              <div>
                <strong>Employee Name:</strong> {qrData.employee_name}
              </div>
              <div>
                <strong>QR Code ID:</strong> {qrData.emp_qr_id}
              </div>
              <div>
                <strong>QR Code Value:</strong> <code style={{ background: '#e9ecef', padding: '2px 6px', borderRadius: '3px' }}>{qrData.code_value}</code>
              </div>
              <div>
                <strong>Status:</strong> <span style={{ color: '#28a745', fontWeight: 'bold' }}>{qrData.status || 'active'}</span>
              </div>
              <div>
                <strong>Issue Date:</strong> {new Date(qrData.issue_date).toLocaleString()}
              </div>
            </div>

            <div style={{ marginTop: '20px', padding: '15px', background: 'white', borderRadius: '5px' }}>
              <h4 style={{ marginBottom: '10px' }}>Download QR Code</h4>
              <p style={{ color: '#6c757d', marginBottom: '15px' }}>
                Click the button below to download the QR code image (PNG format).
              </p>
              <button
                onClick={downloadQR}
                className="btn btn-success"
                style={{ marginRight: '10px' }}
              >
                Download QR Code Image
              </button>
              <button
                onClick={() => setQrData(null)}
                className="btn btn-secondary"
              >
                Generate Another
              </button>
            </div>

            <div style={{ marginTop: '20px', padding: '15px', background: '#fff3cd', borderRadius: '5px', border: '1px solid #ffc107' }}>
              <strong>Note:</strong> Employee QR codes are permanent and do not expire. 
              Keep this QR code secure as it provides access to the system.
            </div>
          </div>
        )}
      </div>

      {/* Instructions */}
      <div className="card" style={{ marginTop: '20px' }}>
        <h2>Instructions</h2>
        <ol style={{ lineHeight: '1.8' }}>
          <li>Select an employee from the dropdown list</li>
          <li>Click "Generate QR Code" to create a permanent QR code for the employee</li>
          <li>Download the QR code image and provide it to the employee</li>
          <li>The employee can use this QR code for check-in/check-out</li>
        </ol>
      </div>
    </div>
  )
}

export default EmployeeQR
