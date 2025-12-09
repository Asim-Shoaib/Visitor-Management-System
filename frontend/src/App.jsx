import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import { DataProvider } from './contexts/DataContext'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import EmployeeQR from './pages/EmployeeQR'
import VisitorEntry from './pages/VisitorEntry'
import CheckInOut from './pages/CheckInOut'
import VisitLogs from './pages/VisitLogs'
import EmployeeAttendance from './pages/EmployeeAttendance'
import UserManagement from './pages/UserManagement'
import EmployeeManagement from './pages/EmployeeManagement'
import SiteManagement from './pages/SiteManagement'
import SalaryCalculation from './pages/SalaryCalculation'
import AdminProfile from './pages/AdminProfile'
import Layout from './components/Layout'

const PrivateRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth()
  
  if (loading) {
    return <div className="loading"><div className="spinner"></div></div>
  }
  
  return isAuthenticated ? children : <Navigate to="/login" />
}

function App() {
  return (
    <AuthProvider>
      <DataProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/"
            element={
              <PrivateRoute>
                <Layout />
              </PrivateRoute>
            }
          >
            <Route index element={<Dashboard />} />
            <Route path="employee-qr" element={<EmployeeQR />} />
            <Route path="visitor-entry" element={<VisitorEntry />} />
            <Route path="checkin-out" element={<CheckInOut />} />
            <Route path="employee-attendance" element={<EmployeeAttendance />} />
            <Route path="logs" element={<VisitLogs />} />
            <Route path="users" element={<UserManagement />} />
            <Route path="employees" element={<EmployeeManagement />} />
            <Route path="sites" element={<SiteManagement />} />
            <Route path="salary" element={<SalaryCalculation />} />
            <Route path="profile" element={<AdminProfile />} />
          </Route>
        </Routes>
      </DataProvider>
    </AuthProvider>
  )
}

export default App


