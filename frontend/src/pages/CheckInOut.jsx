import React, { useState, useEffect } from 'react'
import api from '../services/api'
import { toast } from 'react-toastify'

const CheckInOut = () => {
  const [qrCode, setQrCode] = useState('')
  const [verificationResult, setVerificationResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [scanning, setScanning] = useState(false)
  const [scanner, setScanner] = useState(null)
  const [alertVisible, setAlertVisible] = useState(false)
  const [alertMessage, setAlertMessage] = useState('')

  useEffect(() => {
    return () => {
      if (scanner) {
        scanner.stop().catch(() => {})
      }
    }
  }, [scanner])

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
        (decodedText) => {
          setQrCode(decodedText)
          html5QrCode.stop()
          setScanning(false)
          setScanner(null)
          toast.success('QR code scanned!')
        },
        (errorMessage) => {
          // Ignore errors
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

  const handleVerify = async () => {
    if (!qrCode.trim()) {
      toast.error('Please enter or scan a QR code')
      return
    }

    setLoading(true)
    try {
      const response = await api.post('/scan/verify', {
        qr_code: qrCode.trim()
      })
      setVerificationResult(response.data)
      
      // Check for flags if visitor
      if (response.data.type === 'visitor' && response.data.status === 'valid') {
        // Flags will be checked during check-in
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to verify QR code')
      setVerificationResult(null)
    } finally {
      setLoading(false)
    }
  }

  const handleCheckIn = async () => {
    if (!qrCode.trim()) {
      toast.error('Please enter or scan a QR code')
      return
    }

    setLoading(true)
    try {
      const response = await api.post('/visitor/checkin', {
        qr_code: qrCode.trim()
      })
      
      // Check for security alerts
      if (response.data.alert || response.data.flags) {
        setAlertVisible(true)
        setAlertMessage(response.data.message || 'SECURITY ALERT: This visitor has been flagged!')
        toast.error('SECURITY ALERT: Flagged visitor detected!')
      } else {
        toast.success(`Visitor ${response.data.visitor_name} checked in successfully!`)
        setVerificationResult(null)
        setQrCode('')
      }
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Failed to check in visitor'
      toast.error(errorMsg)
      
      // Check if it's a flag alert
      if (errorMsg.includes('flag') || errorMsg.includes('Flag')) {
        setAlertVisible(true)
        setAlertMessage(errorMsg)
      }
    } finally {
      setLoading(false)
    }
  }

  const handleCheckOut = async () => {
    if (!qrCode.trim()) {
      toast.error('Please enter or scan a QR code')
      return
    }

    setLoading(true)
    try {
      const response = await api.post('/visitor/checkout', {
        qr_code: qrCode.trim()
      })
      
      // Check for flags (informational)
      if (response.data.alert) {
        toast.warning('Note: Visitor has active security flags')
      } else {
        toast.success(`Visitor ${response.data.visitor_name} checked out successfully!`)
      }
      
      setVerificationResult(null)
      setQrCode('')
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to check out visitor')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <h1>Visitor Check-In / Check-Out</h1>
      
      {/* Security Alert Banner */}
      {alertVisible && (
        <div style={{
          padding: '20px',
          background: '#dc3545',
          color: 'white',
          borderRadius: '8px',
          marginBottom: '20px',
          border: '3px solid #c82333',
          fontSize: '1.2rem',
          fontWeight: 'bold',
          textAlign: 'center'
        }}>
          <div style={{ marginBottom: '10px' }}>⚠️ SECURITY ALERT ⚠️</div>
          <div>{alertMessage}</div>
          <button
            onClick={() => setAlertVisible(false)}
            style={{
              marginTop: '15px',
              padding: '8px 16px',
              background: 'white',
              color: '#dc3545',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontWeight: 'bold'
            }}
          >
            Acknowledge
          </button>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginTop: '20px' }}>
        {/* Scanner Section */}
        <div className="card">
          <h2>Scan QR Code</h2>
          
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

          <div className="form-group">
            <label htmlFor="qrCode">Or Enter QR Code Manually</label>
            <input
              type="text"
              id="qrCode"
              value={qrCode}
              onChange={(e) => setQrCode(e.target.value)}
              placeholder="Enter QR code value"
              style={{ width: '100%', padding: '10px' }}
            />
          </div>

          <div style={{ display: 'flex', gap: '10px', marginTop: '15px' }}>
            <button
              onClick={handleVerify}
              className="btn btn-info"
              disabled={loading || !qrCode.trim()}
            >
              Verify QR
            </button>
            <button
              onClick={handleCheckIn}
              className="btn btn-success"
              disabled={loading || !qrCode.trim()}
            >
              {loading ? 'Processing...' : 'Check In'}
            </button>
            <button
              onClick={handleCheckOut}
              className="btn btn-warning"
              disabled={loading || !qrCode.trim()}
            >
              {loading ? 'Processing...' : 'Check Out'}
            </button>
          </div>
        </div>

        {/* Verification Result */}
        <div className="card">
          <h2>Verification Result</h2>
          {loading ? (
            <div className="loading"><div className="spinner"></div></div>
          ) : verificationResult ? (
            <div>
              <p><strong>Type:</strong> {verificationResult.type}</p>
              <p><strong>Status:</strong> 
                <span style={{
                  padding: '4px 8px',
                  borderRadius: '4px',
                  marginLeft: '10px',
                  background: verificationResult.status === 'valid' ? '#28a745' : '#dc3545',
                  color: 'white'
                }}>
                  {verificationResult.status}
                </span>
              </p>
              {verificationResult.type === 'visitor' && (
                <>
                  <p><strong>Visitor:</strong> {verificationResult.visitor_name || 'N/A'}</p>
                  <p><strong>Visit ID:</strong> {verificationResult.visit_id || 'N/A'}</p>
                </>
              )}
              {verificationResult.type === 'employee' && (
                <>
                  <p><strong>Employee:</strong> {verificationResult.employee_name || 'N/A'}</p>
                  <p><strong>Employee ID:</strong> {verificationResult.employee_id || 'N/A'}</p>
                </>
              )}
              {verificationResult.message && (
                <p style={{ color: verificationResult.status === 'valid' ? '#28a745' : '#dc3545' }}>
                  {verificationResult.message}
                </p>
              )}
            </div>
          ) : (
            <p style={{ color: '#6c757d' }}>No QR code verified yet. Scan or enter a QR code and click Verify.</p>
          )}
        </div>
      </div>
    </div>
  )
}

export default CheckInOut
