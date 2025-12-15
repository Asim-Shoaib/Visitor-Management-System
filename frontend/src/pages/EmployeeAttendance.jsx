import React, { useState, useEffect } from 'react'
import api from '../services/api'
import { toast } from 'react-toastify'

const EmployeeAttendance = () => {
  const [scanning, setScanning] = useState(false)
  const [scanner, setScanner] = useState(null)
  const [lastScan, setLastScan] = useState(null)
  const [signedInEmployees, setSignedInEmployees] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchSignedInEmployees()
    const interval = setInterval(fetchSignedInEmployees, 10000) // Refresh every 10 seconds
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    return () => {
      if (scanner) {
        scanner.stop().catch(() => {})
      }
    }
  }, [scanner])

  const fetchSignedInEmployees = async () => {
    try {
      const response = await api.get('/site/employees/signed-in')
      setSignedInEmployees(response.data.employees || [])
    } catch (error) {
      console.error('Failed to fetch signed-in employees:', error)
    }
  }

  const startScanning = async () => {
    try {
      const { Html5Qrcode } = await import('html5-qrcode')
      setScanning(true)
      const html5QrCode = new Html5Qrcode("reader")
      
      await html5QrCode.start(
        { facingMode: "environment" },
        {
          fps: 10,
          qrbox: { width: 250, height: 250 }
        },
        async (decodedText, decodedResult) => {
          try {
            // Temporary debug logging as requested: raw repr, type, length
            const raw = decodedText ?? decodedResult
            console.debug('scan raw value:', raw, 'type:', typeof raw, 'length:', (typeof raw === 'string' && raw.length) || (raw && JSON.stringify(raw).length))

            // Normalize scanned value to a trimmed string
            let value = ''
            if (typeof decodedText === 'string') {
              value = decodedText.trim()
            } else if (decodedResult && typeof decodedResult === 'object') {
              // html5-qrcode may provide decodedText or decodedResult; prefer decodedText-like fields
              value = (decodedResult.decodedText || decodedResult.text || JSON.stringify(decodedResult) || '').trim()
            } else {
              value = String(decodedText).trim()
            }

            if (!value) {
              toast.error('Scanned QR code is empty or invalid')
              return
            }

            await handleScan(value)
          } catch (err) {
            console.error('Error handling scanned QR:', err)
            toast.error('Failed to process scanned QR code')
          } finally {
            try { await html5QrCode.stop() } catch (_) {}
            setScanning(false)
            setScanner(null)
          }
        },
        (errorMessage) => {
          // Ignore scanning errors
        }
      )

      setScanner(html5QrCode)
    } catch (err) {
      toast.error('Failed to start camera. Please check permissions or use manual entry.')
      setScanning(false)
      console.error('Camera error:', err)
    }
  }

  const stopScanning = async () => {
    if (scanner) {
      try {
        await scanner.stop()
        setScanning(false)
        setScanner(null)
      } catch (err) {
        setScanning(false)
        setScanner(null)
      }
    }
  }

  const handleScan = async (qrCode) => {
    setLoading(true)
    try {
      const response = await api.post('/attendance/scan', {
        qr_code: qrCode
      })
      
      setLastScan(response.data)
      toast.success(`Employee ${response.data.employee.name} ${response.data.status === 'checked_in' ? 'checked in' : 'checked out'} at ${new Date(response.data.time).toLocaleTimeString()}`)
      
      // Refresh signed-in list
      fetchSignedInEmployees()
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to process attendance scan')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const handleManualScan = async (e) => {
    e.preventDefault()
    const qrCode = e.target.qrCode.value.trim()
    if (!qrCode) {
      toast.error('Please enter a QR code')
      return
    }
    await handleScan(qrCode)
    e.target.qrCode.value = ''
  }

  return (
    <div className="container">
      <h1>Employee Attendance Scanner</h1>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginTop: '20px' }}>
        {/* Scanner Section */}
        <div className="card">
          <h2>Scan Employee QR Code</h2>
          
          <div style={{ marginBottom: '20px' }}>
            {!scanning ? (
              <button onClick={startScanning} className="btn btn-primary" style={{ marginBottom: '15px' }}>
                Start Camera Scanner
              </button>
            ) : (
              <button onClick={stopScanning} className="btn btn-danger" style={{ marginBottom: '15px' }}>
                Stop Scanner
              </button>
            )}
          </div>

          <div id="reader" style={{ width: '100%', marginBottom: '20px' }}></div>

          <div style={{ borderTop: '1px solid #ddd', paddingTop: '20px', marginTop: '20px' }}>
            <h3>Or Enter QR Code Manually</h3>
            <form onSubmit={handleManualScan}>
              <div className="form-group">
                <input
                  type="text"
                  name="qrCode"
                  placeholder="Enter QR code value"
                  style={{ width: '100%', padding: '10px' }}
                />
              </div>
              <button type="submit" className="btn btn-primary" disabled={loading}>
                {loading ? 'Processing...' : 'Submit'}
              </button>
            </form>
          </div>

          {lastScan && (
            <div style={{ marginTop: '20px', padding: '15px', background: '#d4edda', borderRadius: '5px', border: '1px solid #c3e6cb' }}>
              <h3>Last Scan Result</h3>
              <p><strong>Employee:</strong> {lastScan.employee.name} (ID: {lastScan.employee.id})</p>
              <p><strong>Status:</strong> {lastScan.status === 'checked_in' ? '✅ Checked In' : '✅ Checked Out'}</p>
              <p><strong>Time:</strong> {new Date(lastScan.time).toLocaleString()}</p>
            </div>
          )}
        </div>

        {/* Signed-In Employees List */}
        <div className="card">
          <h2>Currently Signed-In Employees</h2>
          <p style={{ color: '#6c757d', marginBottom: '15px' }}>
            Total: {signedInEmployees.length}
          </p>
          
          {signedInEmployees.length === 0 ? (
            <p style={{ color: '#6c757d' }}>No employees currently signed in</p>
          ) : (
            <div style={{ maxHeight: '500px', overflowY: 'auto' }}>
              <table className="table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Department</th>
                    <th>Last Scan</th>
                  </tr>
                </thead>
                <tbody>
                  {signedInEmployees.map((emp, index) => (
                    <tr key={emp.employee_id || index}>
                      <td>{emp.name}</td>
                      <td>{emp.department_name || 'N/A'}</td>
                      <td>{new Date(emp.last_scan_time).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default EmployeeAttendance

