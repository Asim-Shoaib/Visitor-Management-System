import React, { useState, useEffect } from 'react'
import api from '../services/api'
import { toast } from 'react-toastify'

const AdminProfile = () => {
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchProfile()
  }, [])

  const fetchProfile = async () => {
    try {
      setLoading(true)
      const response = await api.get('/auth/me')
      setProfile(response.data)
    } catch (error) {
      toast.error('Failed to fetch profile information')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="container">
        <div className="loading"><div className="spinner"></div></div>
      </div>
    )
  }

  if (!profile) {
    return (
      <div className="container">
        <div className="card">
          <p>Unable to load profile information</p>
        </div>
      </div>
    )
  }

  return (
    <div className="container">
      <h1>Admin Profile</h1>
      
      <div className="card" style={{ maxWidth: '600px', margin: '0 auto' }}>
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '30px' }}>
          <div
            style={{
              width: '80px',
              height: '80px',
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              fontSize: '32px',
              fontWeight: 'bold',
              marginRight: '20px',
            }}
          >
            {profile.username?.charAt(0).toUpperCase() || 'A'}
          </div>
          <div>
            <h2 style={{ margin: '0 0 5px 0' }}>{profile.username}</h2>
            <p style={{ margin: '0', color: '#6c757d' }}>
              <span style={{
                display: 'inline-block',
                padding: '5px 12px',
                borderRadius: '20px',
                background: '#e7f3ff',
                color: '#0066cc',
                fontSize: '0.9rem',
                fontWeight: 'bold',
                textTransform: 'capitalize'
              }}>
                {profile.role}
              </span>
            </p>
          </div>
        </div>

        <div style={{ display: 'grid', gap: '20px' }}>
          <div style={{ padding: '15px', background: '#f8f9fa', borderRadius: '5px' }}>
            <label style={{ color: '#6c757d', fontSize: '0.9rem' }}>User ID</label>
            <p style={{ margin: '5px 0 0 0', fontSize: '1.1rem', fontWeight: '500' }}>
              {profile.user_id}
            </p>
          </div>

          <div style={{ padding: '15px', background: '#f8f9fa', borderRadius: '5px' }}>
            <label style={{ color: '#6c757d', fontSize: '0.9rem' }}>Username</label>
            <p style={{ margin: '5px 0 0 0', fontSize: '1.1rem', fontWeight: '500' }}>
              {profile.username}
            </p>
          </div>

          <div style={{ padding: '15px', background: '#f8f9fa', borderRadius: '5px' }}>
            <label style={{ color: '#6c757d', fontSize: '0.9rem' }}>Role</label>
            <p style={{ margin: '5px 0 0 0', fontSize: '1.1rem', fontWeight: '500', textTransform: 'capitalize' }}>
              {profile.role}
            </p>
          </div>
        </div>

        <div style={{ marginTop: '30px', padding: '15px', background: '#e7f3ff', borderRadius: '5px', borderLeft: '4px solid #0066cc' }}>
          <p style={{ margin: '0', color: '#004085', fontSize: '0.95rem' }}>
            ✓ You are logged in as <strong>{profile.username}</strong> with <strong>{profile.role}</strong> privileges
          </p>
        </div>
      </div>
    </div>
  )
}

export default AdminProfile
