import React, { useState, useEffect } from 'react'
import api from '../services/api'
import { toast } from 'react-toastify'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

const Dashboard = () => {
  const { user } = useAuth()
  const isAdmin = user?.role === 'admin'
  
  const [stats, setStats] = useState({
    activeVisitors: 0,
    totalVisitsToday: 0,
    pendingApprovals: 0,
    activeEmployees: 0,
    alertsCount: 0,
    checkedInVisitors: 0,
    flaggedVisitors: 0,
    lateArrivals: 0
  })
  const [alerts, setAlerts] = useState([])
  const [signedInEmployees, setSignedInEmployees] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStats()
    const interval = setInterval(fetchStats, 30000) // Refresh every 30 seconds
    return () => clearInterval(interval)
  }, [])

  const fetchStats = async () => {
    try {
      setLoading(true)
      
      // Fetch all data in parallel
      const promises = [
        api.get('/visit/active-visits'),
        api.get('/scan/alerts'),
        api.get('/site/active-employees-count')
      ]
      
      if (isAdmin) {
        promises.push(api.get('/alerts/flagged-visitors'))
        promises.push(api.get('/site/employees/signed-in'))
      }
      
      const results = await Promise.all(promises)
      
      const activeVisits = results[0].data || []
      const alertsData = results[1].data?.alerts || []
      const activeEmployeesCount = results[2].data?.active_employees_count || 0
      const flaggedVisitors = isAdmin && results[3] ? results[3].data?.visitors || [] : []
      const signedIn = isAdmin && results[4] ? results[4].data?.employees || [] : []
      
      // Calculate today's visits
      const today = new Date().toISOString().split('T')[0]
      const todayVisits = activeVisits.filter(v => {
        const visitDate = v.issue_date ? v.issue_date.split('T')[0] : null
        return visitDate === today
      })
      
      setStats({
        activeVisitors: activeVisits.length,
        totalVisitsToday: todayVisits.length,
        pendingApprovals: activeVisits.filter(v => v.status === 'pending').length,
        activeEmployees: activeEmployeesCount,
        alertsCount: alertsData.length,
        checkedInVisitors: activeVisits.filter(v => v.status === 'checked_in').length,
        flaggedVisitors: flaggedVisitors.length,
        lateArrivals: 0 // Would need backend endpoint for this
      })
      
      // Set recent alerts (last 5)
      setAlerts(alertsData.slice(0, 5))
      setSignedInEmployees(signedIn.slice(0, 5))
    } catch (error) {
      toast.error('Failed to fetch statistics')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const handleSendLateAlerts = async () => {
    try {
      const response = await api.post('/email/alert-late', {})
      toast.success(response.data.message || 'Late arrival alerts sent')
      fetchStats()
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to send late alerts')
      console.error(error)
    }
  }

  const handleExportExcel = async () => {
    try {
      const today = new Date().toISOString().split('T')[0]
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/logs/export?start_date=${today}&end_date=${today}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      
      if (!response.ok) throw new Error('Export failed')
      
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `visitor_logs_${today}.xlsx`
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
      
      toast.success('Excel file downloaded successfully')
    } catch (error) {
      toast.error('Failed to export to Excel')
      console.error(error)
    }
  }

  if (loading) {
    return <div className="loading"><div className="spinner"></div></div>
  }

  return (
    <div className="container">
      <h1>{isAdmin ? 'Admin Dashboard' : 'Security Dashboard'}</h1>
      
      {/* Statistics Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginTop: '20px' }}>
        <div className="card" style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
          <h3 style={{ marginBottom: '10px', fontSize: '0.9rem', opacity: 0.9 }}>Active Visitors</h3>
          <p style={{ fontSize: '2.5rem', fontWeight: 'bold', margin: 0 }}>
            {stats.activeVisitors}
          </p>
          <p style={{ fontSize: '0.8rem', marginTop: '5px', opacity: 0.8 }}>
            {stats.checkedInVisitors} checked in
          </p>
        </div>
        
        <div className="card" style={{ background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', color: 'white' }}>
          <h3 style={{ marginBottom: '10px', fontSize: '0.9rem', opacity: 0.9 }}>Visits Today</h3>
          <p style={{ fontSize: '2.5rem', fontWeight: 'bold', margin: 0 }}>
            {stats.totalVisitsToday}
          </p>
          <p style={{ fontSize: '0.8rem', marginTop: '5px', opacity: 0.8 }}>
            Total visits
          </p>
        </div>
        
        <div className="card" style={{ background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)', color: 'white' }}>
          <h3 style={{ marginBottom: '10px', fontSize: '0.9rem', opacity: 0.9 }}>Active Employees</h3>
          <p style={{ fontSize: '2.5rem', fontWeight: 'bold', margin: 0 }}>
            {stats.activeEmployees}
          </p>
          <p style={{ fontSize: '0.8rem', marginTop: '5px', opacity: 0.8 }}>
            Currently signed in
          </p>
        </div>
        
        <div className="card" style={{ background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)', color: 'white' }}>
          <h3 style={{ marginBottom: '10px', fontSize: '0.9rem', opacity: 0.9 }}>Pending Approvals</h3>
          <p style={{ fontSize: '2.5rem', fontWeight: 'bold', margin: 0 }}>
            {stats.pendingApprovals}
          </p>
          <p style={{ fontSize: '0.8rem', marginTop: '5px', opacity: 0.8 }}>
            Awaiting approval
          </p>
        </div>
        
        <div className="card" style={{ background: 'linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%)', color: 'white' }}>
          <h3 style={{ marginBottom: '10px', fontSize: '0.9rem', opacity: 0.9 }}>Active Alerts</h3>
          <p style={{ fontSize: '2.5rem', fontWeight: 'bold', margin: 0 }}>
            {stats.alertsCount}
          </p>
          <p style={{ fontSize: '0.8rem', marginTop: '5px', opacity: 0.8 }}>
            Security alerts
          </p>
        </div>

        {isAdmin && (
          <>
            <div className="card" style={{ background: 'linear-gradient(135deg, #ff9a56 0%, #ff6a88 100%)', color: 'white' }}>
              <h3 style={{ marginBottom: '10px', fontSize: '0.9rem', opacity: 0.9 }}>Flagged Visitors</h3>
              <p style={{ fontSize: '2.5rem', fontWeight: 'bold', margin: 0 }}>
                {stats.flaggedVisitors}
              </p>
              <p style={{ fontSize: '0.8rem', marginTop: '5px', opacity: 0.8 }}>
                Security flags
              </p>
            </div>

            <div className="card" style={{ background: 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)', color: '#333' }}>
              <h3 style={{ marginBottom: '10px', fontSize: '0.9rem', opacity: 0.9 }}>Late Arrivals</h3>
              <p style={{ fontSize: '2.5rem', fontWeight: 'bold', margin: 0 }}>
                {stats.lateArrivals}
              </p>
              <button 
                onClick={handleSendLateAlerts}
                className="btn btn-warning"
                style={{ marginTop: '10px', fontSize: '0.8rem', padding: '5px 10px' }}
              >
                Send Alerts Now
              </button>
            </div>
          </>
        )}
      </div>

      {/* Admin Only Sections */}
      {isAdmin && (
        <>
          {/* Signed-In Employees */}
          {signedInEmployees.length > 0 && (
            <div className="card" style={{ marginTop: '30px' }}>
              <h2>Recently Signed-In Employees</h2>
              <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
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
            </div>
          )}

          {/* Flagged Visitors */}
          {stats.flaggedVisitors > 0 && (
            <div className="card" style={{ marginTop: '30px', border: '2px solid #dc3545' }}>
              <h2 style={{ color: '#dc3545' }}>⚠️ Flagged Visitors</h2>
              <Link to="/logs" className="btn btn-danger" style={{ textDecoration: 'none', marginTop: '10px' }}>
                View Flagged Visitors
              </Link>
            </div>
          )}
        </>
      )}

      {/* Alerts Section */}
      {alerts.length > 0 && (
        <div className="card" style={{ marginTop: '30px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
            <h2>Recent Security Alerts</h2>
            <Link to="/logs" className="btn btn-primary" style={{ textDecoration: 'none' }}>
              View All Alerts
            </Link>
          </div>
          <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
            <table className="table">
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Visitor</th>
                  <th>Description</th>
                </tr>
              </thead>
              <tbody>
                {alerts.map((alert, index) => (
                  <tr key={alert.alert_id || index} style={{ background: alert.alert_id ? 'transparent' : '#fff3cd' }}>
                    <td>{new Date(alert.created_at).toLocaleString()}</td>
                    <td>{alert.visitor_name || 'Unknown'}</td>
                    <td>{alert.description || 'Invalid QR code scan'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="card" style={{ marginTop: '30px' }}>
        <h2>Quick Actions</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px', marginTop: '15px' }}>
          <Link to="/visitor-entry" className="btn btn-primary" style={{ textDecoration: 'none', textAlign: 'center', padding: '15px' }}>
            Register New Visitor
          </Link>
          <Link to="/employee-qr" className="btn btn-success" style={{ textDecoration: 'none', textAlign: 'center', padding: '15px' }}>
            Generate Employee QR
          </Link>
          <Link to="/checkin-out" className="btn btn-warning" style={{ textDecoration: 'none', textAlign: 'center', padding: '15px' }}>
            Check-In/Out
          </Link>
          <Link to="/employee-attendance" className="btn btn-info" style={{ textDecoration: 'none', textAlign: 'center', padding: '15px' }}>
            Employee Attendance
          </Link>
          <Link to="/logs" className="btn btn-secondary" style={{ textDecoration: 'none', textAlign: 'center', padding: '15px' }}>
            View Logs
          </Link>
          {isAdmin && (
            <>
              <Link to="/users" className="btn btn-danger" style={{ textDecoration: 'none', textAlign: 'center', padding: '15px' }}>
                Manage Users
              </Link>
              <button onClick={handleExportExcel} className="btn btn-success" style={{ padding: '15px' }}>
                Export to Excel
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default Dashboard
