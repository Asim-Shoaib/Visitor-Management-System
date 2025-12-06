import React, { createContext, useContext, useState, useEffect } from 'react'
import api from '../services/api'

const DataContext = createContext()

export const useData = () => {
  const context = useContext(DataContext)
  if (!context) {
    throw new Error('useData must be used within DataProvider')
  }
  return context
}

export const DataProvider = ({ children }) => {
  const [sites, setSites] = useState([])
  const [employees, setEmployees] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchData()
    // Refresh every 5 minutes
    const interval = setInterval(fetchData, 300000)
    return () => clearInterval(interval)
  }, [])

  const fetchData = async () => {
    try {
      const [sitesRes, employeesRes] = await Promise.all([
        api.get('/site/list'),
        api.get('/site/employees')
      ])
      setSites(sitesRes.data.sites || [])
      setEmployees(employeesRes.data.employees || [])
    } catch (error) {
      console.error('Failed to fetch data:', error)
    } finally {
      setLoading(false)
    }
  }

  const refreshData = () => {
    fetchData()
  }

  return (
    <DataContext.Provider value={{ sites, employees, loading, refreshData }}>
      {children}
    </DataContext.Provider>
  )
}

