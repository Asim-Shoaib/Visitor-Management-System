import React, { useState, useEffect } from 'react'
import api from '../services/api'
import { toast } from 'react-toastify'
import { useAuth } from '../contexts/AuthContext'
import { useData } from '../contexts/DataContext'
import { Link } from 'react-router-dom'

const VisitorEntry = () => {
  const { user } = useAuth()
  const { sites, employees } = useData()
  const [formData, setFormData] = useState({
    full_name: '',
    cnic: '',
    contact_number: '',
    email: '',
    site_id: sites.length > 0 ? sites[0].site_id : 1,
    host_employee_id: '',
    purpose_details: ''
  })
  const [loading, setLoading] = useState(false)
  const [qrData, setQrData] = useState(null)

  useEffect(() => {
    // Update site_id when sites are loaded
    if (sites.length > 0 && formData.site_id === 1) {
      setFormData(prev => ({
        ...prev,
        site_id: sites[0].site_id
      }))
    }
  }, [sites])

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const validateCNIC = (cnic) => {
    const pattern = /^[0-9]{5}-[0-9]{7}-[0-9]$/
    return pattern.test(cnic)
  }

  const validateEmail = (email) => {
    const pattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
    return pattern.test(email)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    // Validation
    if (!validateCNIC(formData.cnic)) {
      toast.error('Invalid CNIC format. Use: XXXXX-XXXXXXX-X')
      return
    }

    if (formData.email && !validateEmail(formData.email)) {
      toast.error('Invalid email format')
      return
    }

    setLoading(true)
    try {
      // Step 1: Create visitor
      let visitorResponse
      try {
        visitorResponse = await api.post('/visitor/add-visitor', {
          full_name: formData.full_name,
          cnic: formData.cnic,
          contact_number: formData.contact_number || null
        })
      } catch (error) {
        if (error.response?.status === 400) {
          // Visitor might already exist, try to search
          const searchRes = await api.get(`/visitor/search-visitor?cnic=${formData.cnic}`)
          visitorResponse = { data: { visitor_id: searchRes.data.visitor_id } }
        } else {
          throw error
        }
      }

      const visitorId = visitorResponse.data.visitor_id

      // Step 2: Create visit
      const visitResponse = await api.post('/visit/create-visit', {
        visitor_id: visitorId,
        site_id: parseInt(formData.site_id),
        host_employee_id: formData.host_employee_id && formData.host_employee_id !== '' ? parseInt(formData.host_employee_id) : null,
        purpose_details: formData.purpose_details || null
      })

      const visitId = visitResponse.data.visit_id

      // Step 3: Generate QR code
      if (formData.email) {
        const qrResponse = await api.post('/qr/generate-visitor', {
          visit_id: visitId,
          recipient_email: formData.email
        })
        setQrData(qrResponse.data)
        
        // Step 4: Send QR code via email if email provided
        if (qrResponse.data.code_value) {
          try {
            await api.post('/email/send-qr', {
              email: formData.email,
              visitor_id: visitorId,
              qr_code_data: qrResponse.data.code_value
            })
            toast.success('Visitor registered, visit created, QR code generated, and email sent!')
          } catch (emailError) {
            toast.warning('QR code generated but email sending failed. QR code is available for download.')
            console.error('Email error:', emailError)
          }
        } else {
          toast.success('Visitor registered, visit created, and QR code generated!')
        }
      } else {
        toast.success('Visitor registered and visit created! (No email provided for QR)')
      }

      // Reset form
      setFormData({
        full_name: '',
        cnic: '',
        contact_number: '',
        email: '',
        site_id: 1,
        host_employee_id: '',
        purpose_details: ''
      })
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to process visitor entry')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <h1>Visitor Entry & Visit Creation</h1>
      
      {employees.length === 0 && user?.role === 'admin' && (
        <div style={{
          marginBottom: '20px',
          padding: '15px',
          background: '#fff3cd',
          border: '1px solid #ffc107',
          borderRadius: '4px',
          color: '#856404'
        }}>
          <strong>⚠️ No employees found.</strong> Before creating visits, you need to add employees first.
          <br />
          <Link to="/employees" className="btn btn-warning" style={{ marginTop: '10px', display: 'inline-block' }}>
            Go to Employee Management →
          </Link>
        </div>
      )}
      
      <div className="card">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="full_name">Full Name *</label>
            <input
              type="text"
              id="full_name"
              name="full_name"
              value={formData.full_name}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="cnic">CNIC * (Format: XXXXX-XXXXXXX-X)</label>
            <input
              type="text"
              id="cnic"
              name="cnic"
              value={formData.cnic}
              onChange={handleChange}
              placeholder="12345-1234567-1"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="contact_number">Contact Number</label>
            <input
              type="text"
              id="contact_number"
              name="contact_number"
              value={formData.contact_number}
              onChange={handleChange}
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email (for QR code delivery)</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
            />
          </div>

          <div className="form-group">
            <label htmlFor="site_id">Site</label>
            <select
              id="site_id"
              name="site_id"
              value={formData.site_id}
              onChange={handleChange}
            >
              {sites.map(site => (
                <option key={site.site_id} value={site.site_id}>
                  {site.site_name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="host_employee_id">Host Employee (optional)</label>
            <select
              id="host_employee_id"
              name="host_employee_id"
              value={formData.host_employee_id}
              onChange={handleChange}
            >
              <option value="">None</option>
              {employees.map(emp => (
                <option key={emp.employee_id} value={emp.employee_id}>
                  {emp.name} {emp.department_name ? `(${emp.department_name})` : ''}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="purpose_details">Purpose Details</label>
            <textarea
              id="purpose_details"
              name="purpose_details"
              value={formData.purpose_details}
              onChange={handleChange}
              rows="3"
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
          >
            {loading ? 'Processing...' : 'Create Visit & Generate QR'}
          </button>
        </form>

        {qrData && (
          <div style={{ marginTop: '20px', padding: '20px', background: '#f8f9fa', borderRadius: '4px' }}>
            <h3>QR Code Generated</h3>
            <p><strong>Visitor Name:</strong> {qrData.visitor_name}</p>
            <p><strong>Visit ID:</strong> {qrData.visit_id}</p>
            <p><strong>QR Code Value:</strong> {qrData.code_value}</p>
            <p><strong>Expiry Date:</strong> {new Date(qrData.expiry_date).toLocaleString()}</p>
            <p><strong>Email Sent:</strong> {qrData.email_sent ? 'Yes' : 'No'}</p>
            {qrData.download_url && (
              <a
                href={qrData.download_url}
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-success"
                style={{ marginTop: '10px', display: 'inline-block' }}
              >
                Download QR Code
              </a>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default VisitorEntry


