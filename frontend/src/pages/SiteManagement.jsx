import React, { useState, useEffect } from 'react'
import api from '../services/api'
import { toast } from 'react-toastify'
import { useData } from '../contexts/DataContext'

const SiteManagement = () => {
  const { sites, refreshData } = useData()
  const [loading, setLoading] = useState(false)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [formData, setFormData] = useState({
    site_name: '',
    address: ''
  })

  const handleCreateSite = async (e) => {
    e.preventDefault()
    
    // Validate inputs
    if (!formData.site_name.trim()) {
      toast.error('Site name is required')
      return
    }

    try {
      setLoading(true)
      const payload = {
        site_name: formData.site_name.trim(),
        address: formData.address.trim() || null
      }
      
      await api.post('/site/create-site', payload)
      toast.success('Site created successfully')
      setFormData({ site_name: '', address: '' })
      setShowCreateForm(false)
      refreshData()
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create site')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1>Site Management</h1>
        <button 
          onClick={() => setShowCreateForm(!showCreateForm)} 
          className="btn btn-primary"
        >
          {showCreateForm ? 'Cancel' : 'Add New Site'}
        </button>
      </div>

      {showCreateForm && (
        <div className="card" style={{ marginBottom: '20px' }}>
          <h2>Add New Site</h2>
          <form onSubmit={handleCreateSite}>
            <div className="form-group">
              <label htmlFor="site_name">Site Name *</label>
              <input
                type="text"
                id="site_name"
                value={formData.site_name}
                onChange={(e) => setFormData({ ...formData, site_name: e.target.value })}
                required
                minLength={2}
                maxLength={150}
                placeholder="e.g., Main Office, Branch A"
              />
            </div>

            <div className="form-group">
              <label htmlFor="address">Address</label>
              <textarea
                id="address"
                value={formData.address}
                onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                maxLength={500}
                placeholder="Site address (optional)"
                rows="3"
              />
            </div>

            <button type="submit" className="btn btn-success" disabled={loading}>
              {loading ? 'Creating...' : 'Create Site'}
            </button>
          </form>
        </div>
      )}

      <div className="card">
        <h2>All Sites ({sites.length})</h2>
        {sites.length === 0 ? (
          <p>No sites found. Create your first site to get started.</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Site Name</th>
                <th>Address</th>
              </tr>
            </thead>
            <tbody>
              {sites.map((site) => (
                <tr key={site.site_id}>
                  <td>{site.site_id}</td>
                  <td>{site.site_name}</td>
                  <td>{site.address || 'N/A'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

export default SiteManagement
