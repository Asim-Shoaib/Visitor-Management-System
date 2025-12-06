import React from 'react'
import { Outlet, Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import './Layout.css'

const Layout = () => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="layout">
      <nav className="navbar">
        <div className="nav-brand">Visitor Management System</div>
        <div className="nav-links">
          <Link to="/">Dashboard</Link>
          <Link to="/employee-qr">Employee QR</Link>
          <Link to="/visitor-entry">Visitor Entry</Link>
          <Link to="/checkin-out">Check-In/Out</Link>
          <Link to="/employee-attendance">Employee Attendance</Link>
          <Link to="/logs">Logs</Link>
          {user?.role === 'admin' && (
            <>
              <Link to="/users">Users</Link>
              <Link to="/sites">Sites</Link>
              <Link to="/employees">Employees</Link>
              <Link to="/salary">Salary</Link>
            </>
          )}
        </div>
        <div className="nav-user">
          <span>{user?.username} ({user?.role})</span>
          <Link to="/profile" className="btn btn-info" style={{ marginRight: '10px' }}>Profile</Link>
          <button onClick={handleLogout} className="btn btn-secondary">
            Logout
          </button>
        </div>
      </nav>
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  )
}

export default Layout


