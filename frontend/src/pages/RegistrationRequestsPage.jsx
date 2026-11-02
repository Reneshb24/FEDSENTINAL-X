import React, { useState, useEffect } from 'react'
import {
  ClipboardCheck,
  CheckCircle,
  XCircle,
  Eye,
  Clock,
  Building,
  Mail,
  Phone,
  Globe,
  MapPin,
  FileText,
  AlertTriangle,
  RefreshCw,
  Search
} from 'lucide-react'

import { getApiBaseUrl } from '../apiConfig'
const API = getApiBaseUrl()

export default function RegistrationRequestsPage({ token, onDataRefresh }) {
  const [applications, setApplications] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [statusFilter, setStatusFilter] = useState('ALL')
  const [search, setSearch] = useState('')

  // Modals state
  const [selectedApp, setSelectedApp] = useState(null)
  const [reviewModalOpen, setReviewModalOpen] = useState(false)
  const [approveModalOpen, setApproveModalOpen] = useState(false)
  const [rejectModalOpen, setRejectModalOpen] = useState(false)
  const [notes, setNotes] = useState('')
  const [rejectionReason, setRejectionReason] = useState('')
  const [actionBusy, setActionBusy] = useState(false)
  const [actionMessage, setActionMessage] = useState('')

  async function loadApplications() {
    setLoading(true)
    setError('')
    try {
      const resp = await fetch(`${API}/api/v1/hospitals/applications`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      })
      if (!resp.ok) {
        throw new Error(`Failed to load applications: ${resp.status}`)
      }
      const data = await resp.json()
      setApplications(Array.isArray(data) ? data : [])
    } catch (err) {
      setError(err.message || 'Error loading applications')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadApplications()
  }, [])

  const filtered = applications.filter((app) => {
    const s = String(app.application_status || app.status || '').toUpperCase()
    if (statusFilter !== 'ALL' && s !== statusFilter) return false

    if (search.trim()) {
      const q = search.toLowerCase()
      const matchName = String(app.name || '').toLowerCase().includes(q)
      const matchCode = String(app.code || '').toLowerCase().includes(q)
      const matchEmail = String(app.contact_email || '').toLowerCase().includes(q)
      if (!matchName && !matchCode && !matchEmail) return false
    }
    return true
  })

  const submittedCount = applications.filter(a => (a.application_status === 'SUBMITTED' || a.status === 'PENDING')).length
  const underReviewCount = applications.filter(a => a.application_status === 'UNDER_REVIEW').length
  const rejectedCount = applications.filter(a => (a.application_status === 'REJECTED' || a.status === 'REJECTED')).length

  async function handleMarkReview(app) {
    setActionBusy(true)
    setActionMessage('')
    try {
      const resp = await fetch(`${API}/api/v1/hospitals/${app.id}/review`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ notes: 'Application marked under review by administrator' })
      })
      if (!resp.ok) {
        const d = await resp.json().catch(() => null)
        throw new Error(d?.detail || `Failed with status ${resp.status}`)
      }
      setActionMessage(`Application for ${app.name} (${app.code}) is now UNDER_REVIEW.`)
      await loadApplications()
      onDataRefresh?.()
    } catch (err) {
      alert(`Error: ${err.message}`)
    } finally {
      setActionBusy(false)
    }
  }

  async function handleApprove() {
    if (!selectedApp) return
    setActionBusy(true)
    try {
      const resp = await fetch(`${API}/api/v1/hospitals/${selectedApp.id}/application-approve`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ notes: notes || undefined })
      })
      if (!resp.ok) {
        const d = await resp.json().catch(() => null)
        throw new Error(d?.detail || `Approval failed with status ${resp.status}`)
      }
      setApproveModalOpen(false)
      setSelectedApp(null)
      setNotes('')
      setActionMessage(`Approved ${selectedApp.name}! Enrolled into active federation membership.`)
      await loadApplications()
      onDataRefresh?.()
    } catch (err) {
      alert(`Approval error: ${err.message}`)
    } finally {
      setActionBusy(false)
    }
  }

  async function handleReject() {
    if (!selectedApp) return
    if (!rejectionReason.trim() || rejectionReason.trim().length < 3) {
      alert('A valid mandatory rejection reason must be provided.')
      return
    }
    setActionBusy(true)
    try {
      const resp = await fetch(`${API}/api/v1/hospitals/${selectedApp.id}/application-reject`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ rejection_reason: rejectionReason.trim() })
      })
      if (!resp.ok) {
        const d = await resp.json().catch(() => null)
        throw new Error(d?.detail || `Rejection failed with status ${resp.status}`)
      }
      setRejectModalOpen(false)
      setSelectedApp(null)
      setRejectionReason('')
      setActionMessage(`Application for ${selectedApp.name} rejected. Mandatory reason recorded in audit log.`)
      await loadApplications()
      onDataRefresh?.()
    } catch (err) {
      alert(`Rejection error: ${err.message}`)
    } finally {
      setActionBusy(false)
    }
  }

  return (
    <div className="page-container" style={{ padding: '24px' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <div>
          <div style={{ color: '#00e5ff', fontSize: 11, fontWeight: 700, letterSpacing: '0.1em' }}>
            FEDERATION / ONBOARDING CONTROL
          </div>
          <h1 style={{ fontSize: 26, margin: '4px 0', color: '#fff', display: 'flex', alignItems: 'center', gap: 10 }}>
            <ClipboardCheck size={26} color="#00e5ff" />
            Institutional Registration Requests
          </h1>
          <p style={{ color: '#94a3b8', fontSize: 13, margin: 0 }}>
            Global Administrative review queue for incoming hospital enclaves. Strict verification prevents unapproved nodes from participating.
          </p>
        </div>

        <button
          onClick={loadApplications}
          className="hp-button"
          disabled={loading}
          style={{ display: 'flex', alignItems: 'center', gap: 6, background: '#1e293b', border: '1px solid #334155', color: '#f8fafc', padding: '8px 14px', borderRadius: 6, cursor: 'pointer' }}
        >
          <RefreshCw size={14} className={loading ? 'hp-spin' : ''} />
          Refresh Queue
        </button>
      </div>

      {actionMessage && (
        <div style={{ padding: '12px 16px', background: 'rgba(16, 185, 129, 0.15)', border: '1px solid #10b981', color: '#10b981', borderRadius: 6, marginBottom: 16, fontSize: 13 }}>
          {actionMessage}
        </div>
      )}

      {error && (
        <div style={{ padding: '12px 16px', background: 'rgba(239, 68, 68, 0.15)', border: '1px solid #ef4444', color: '#ef4444', borderRadius: 6, marginBottom: 16, fontSize: 13 }}>
          {error}
        </div>
      )}

      {/* Metric Chips */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 12, marginBottom: 20 }}>
        <div style={{ background: '#0f172a', border: '1px solid #1e293b', padding: '14px', borderRadius: 6 }}>
          <div style={{ color: '#64748b', fontSize: 11 }}>AWAITING INTAKE</div>
          <div style={{ fontSize: 22, fontWeight: 700, color: '#f59e0b', marginTop: 4 }}>{submittedCount}</div>
          <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 2 }}>Pending initial review</div>
        </div>
        <div style={{ background: '#0f172a', border: '1px solid #1e293b', padding: '14px', borderRadius: 6 }}>
          <div style={{ color: '#64748b', fontSize: 11 }}>UNDER SECURITY REVIEW</div>
          <div style={{ fontSize: 22, fontWeight: 700, color: '#38bdf8', marginTop: 4 }}>{underReviewCount}</div>
          <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 2 }}>Credentials verification in progress</div>
        </div>
        <div style={{ background: '#0f172a', border: '1px solid #1e293b', padding: '14px', borderRadius: 6 }}>
          <div style={{ color: '#64748b', fontSize: 11 }}>REJECTED APPLICATIONS</div>
          <div style={{ fontSize: 22, fontWeight: 700, color: '#ef4444', marginTop: 4 }}>{rejectedCount}</div>
          <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 2 }}>Declined with justification</div>
        </div>
      </div>

      {/* Filters */}
      <div style={{ display: 'flex', gap: 12, marginBottom: 16, flexWrap: 'wrap', alignItems: 'center' }}>
        <div style={{ display: 'flex', gap: 6 }}>
          {['ALL', 'SUBMITTED', 'UNDER_REVIEW', 'REJECTED'].map((st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              style={{
                background: statusFilter === st ? '#0284c7' : '#1e293b',
                color: statusFilter === st ? '#fff' : '#94a3b8',
                border: '1px solid #334155',
                padding: '6px 12px',
                borderRadius: 4,
                fontSize: 11,
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              {st}
            </button>
          ))}
        </div>

        <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', background: '#0f172a', border: '1px solid #334155', borderRadius: 4, padding: '4px 8px' }}>
          <Search size={14} color="#64748b" style={{ marginRight: 6 }} />
          <input
            type="text"
            placeholder="Search code, name, email..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ background: 'transparent', border: 'none', color: '#fff', fontSize: 12, outline: 'none', width: '180px' }}
          />
        </div>
      </div>

      {/* Applications List */}
      {filtered.length === 0 ? (
        <div style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: 8, padding: 40, textAlign: 'center', color: '#64748b' }}>
          <ClipboardCheck size={36} style={{ margin: '0 auto 12px', opacity: 0.5 }} />
          <div style={{ fontSize: 14, color: '#cbd5e1', fontWeight: 600 }}>No Registration Requests Found</div>
          <div style={{ fontSize: 12, marginTop: 4 }}>
            {statusFilter !== 'ALL' ? `No applications matching status "${statusFilter}"` : 'All hospital applications have been processed.'}
          </div>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {filtered.map((app) => {
            const st = String(app.application_status || app.status || 'SUBMITTED').toUpperCase()
            const isSubmitted = st === 'SUBMITTED' || st === 'PENDING'
            const isReview = st === 'UNDER_REVIEW'
            const isRejected = st === 'REJECTED'

            const badgeBg = isRejected ? 'rgba(239, 68, 68, 0.2)' : isReview ? 'rgba(56, 189, 248, 0.2)' : 'rgba(245, 158, 11, 0.2)'
            const badgeColor = isRejected ? '#ef4444' : isReview ? '#38bdf8' : '#f59e0b'

            return (
              <div
                key={app.id}
                style={{
                  background: '#0f172a',
                  border: '1px solid #1e293b',
                  borderRadius: 8,
                  padding: 16,
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 12
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 8 }}>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <span style={{ background: '#1e293b', color: '#38bdf8', fontWeight: 700, fontSize: 12, padding: '2px 8px', borderRadius: 4 }}>
                        {app.code}
                      </span>
                      <strong style={{ fontSize: 16, color: '#f8fafc' }}>{app.name}</strong>
                      <span style={{ background: badgeBg, color: badgeColor, fontSize: 11, fontWeight: 700, padding: '2px 8px', borderRadius: 4 }}>
                        {st}
                      </span>
                    </div>
                    <div style={{ fontSize: 11, color: '#64748b', marginTop: 4 }}>
                      Application ID: <span style={{ fontFamily: 'monospace' }}>{app.id}</span> • Registered: {new Date(app.created_at).toLocaleString()}
                    </div>
                  </div>

                  {/* Actions */}
                  <div style={{ display: 'flex', gap: 8 }}>
                    {isSubmitted && (
                      <button
                        onClick={() => handleMarkReview(app)}
                        disabled={actionBusy}
                        style={{
                          background: '#1e293b',
                          border: '1px solid #38bdf8',
                          color: '#38bdf8',
                          padding: '6px 12px',
                          borderRadius: 4,
                          fontSize: 11,
                          cursor: 'pointer',
                          fontWeight: 600
                        }}
                      >
                        Start Review
                      </button>
                    )}

                    {!isRejected && (
                      <>
                        <button
                          onClick={() => {
                            setSelectedApp(app)
                            setApproveModalOpen(true)
                          }}
                          disabled={actionBusy}
                          style={{
                            background: '#059669',
                            border: '1px solid #10b981',
                            color: '#fff',
                            padding: '6px 12px',
                            borderRadius: 4,
                            fontSize: 11,
                            cursor: 'pointer',
                            fontWeight: 600
                          }}
                        >
                          Approve Enclave
                        </button>

                        <button
                          onClick={() => {
                            setSelectedApp(app)
                            setRejectModalOpen(true)
                          }}
                          disabled={actionBusy}
                          style={{
                            background: 'transparent',
                            border: '1px solid #ef4444',
                            color: '#ef4444',
                            padding: '6px 12px',
                            borderRadius: 4,
                            fontSize: 11,
                            cursor: 'pointer',
                            fontWeight: 600
                          }}
                        >
                          Reject
                        </button>
                      </>
                    )}
                  </div>
                </div>

                {/* Details Grid */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 10, background: '#020617', padding: 12, borderRadius: 6, fontSize: 11 }}>
                  <div>
                    <span style={{ color: '#64748b' }}>Institution Type:</span>{' '}
                    <strong style={{ color: '#cbd5e1' }}>{app.institution_type || 'General Hospital'}</strong>
                  </div>
                  <div>
                    <span style={{ color: '#64748b' }}>Contact Email:</span>{' '}
                    <strong style={{ color: '#cbd5e1' }}>{app.contact_email || '—'}</strong>
                  </div>
                  <div>
                    <span style={{ color: '#64748b' }}>Phone:</span>{' '}
                    <strong style={{ color: '#cbd5e1' }}>{app.contact_phone || '—'}</strong>
                  </div>
                  <div>
                    <span style={{ color: '#64748b' }}>Location / Country:</span>{' '}
                    <strong style={{ color: '#cbd5e1' }}>{app.location || app.address || app.country || '—'}</strong>
                  </div>
                  {app.website && (
                    <div>
                      <span style={{ color: '#64748b' }}>Website:</span>{' '}
                      <a href={app.website} target="_blank" rel="noreferrer" style={{ color: '#38bdf8' }}>{app.website}</a>
                    </div>
                  )}
                  {app.description && (
                    <div style={{ gridColumn: '1 / -1' }}>
                      <span style={{ color: '#64748b' }}>Description:</span>{' '}
                      <span style={{ color: '#94a3b8' }}>{app.description}</span>
                    </div>
                  )}
                </div>

                {/* If rejected, display rejection reason */}
                {isRejected && app.rejection_reason && (
                  <div style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid #ef4444', padding: '8px 12px', borderRadius: 4, fontSize: 11, color: '#f87171' }}>
                    <strong>Mandatory Rejection Justification:</strong> {app.rejection_reason}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}

      {/* Approve Modal */}
      {approveModalOpen && selectedApp && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)', zIndex: 9999, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20 }}>
          <div style={{ background: '#0f172a', border: '1px solid #334155', borderRadius: 8, maxWidth: 500, width: '100%', padding: 24, boxShadow: '0 20px 40px rgba(0,0,0,0.8)' }}>
            <h3 style={{ margin: '0 0 10px', color: '#10b981', display: 'flex', alignItems: 'center', gap: 8 }}>
              <CheckCircle size={20} />
              Approve Institutional Application
            </h3>
            <p style={{ color: '#cbd5e1', fontSize: 12, lineHeight: 1.5 }}>
              Approving <strong>{selectedApp.name} ({selectedApp.code})</strong> will grant active federation membership, mark application status as APPROVED, and permit local enclave training.
            </p>

            <label style={{ display: 'block', fontSize: 11, color: '#94a3b8', marginTop: 14 }}>
              APPROVAL AUDIT NOTES (OPTIONAL)
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="e.g. Verified institutional credentials and data residency compliance."
                style={{ width: '100%', background: '#020617', border: '1px solid #334155', color: '#fff', padding: 8, borderRadius: 4, marginTop: 4, minHeight: 60, fontSize: 12 }}
              />
            </label>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10, marginTop: 20 }}>
              <button
                type="button"
                onClick={() => { setApproveModalOpen(false); setSelectedApp(null); }}
                style={{ background: '#1e293b', border: '1px solid #334155', color: '#cbd5e1', padding: '6px 14px', borderRadius: 4, cursor: 'pointer', fontSize: 12 }}
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleApprove}
                disabled={actionBusy}
                style={{ background: '#059669', border: 'none', color: '#fff', padding: '6px 16px', borderRadius: 4, cursor: 'pointer', fontWeight: 600, fontSize: 12 }}
              >
                {actionBusy ? 'Enrolling...' : 'Confirm Approval & Enroll'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Reject Modal */}
      {rejectModalOpen && selectedApp && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)', zIndex: 9999, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20 }}>
          <div style={{ background: '#0f172a', border: '1px solid #ef4444', borderRadius: 8, maxWidth: 500, width: '100%', padding: 24, boxShadow: '0 20px 40px rgba(0,0,0,0.8)' }}>
            <h3 style={{ margin: '0 0 10px', color: '#ef4444', display: 'flex', alignItems: 'center', gap: 8 }}>
              <XCircle size={20} />
              Reject Institutional Application
            </h3>
            <p style={{ color: '#cbd5e1', fontSize: 12, lineHeight: 1.5 }}>
              Rejecting <strong>{selectedApp.name} ({selectedApp.code})</strong> requires a mandatory reason. This reason is permanently recorded in the immutable audit log and displayed to the institution.
            </p>

            <label style={{ display: 'block', fontSize: 11, color: '#f87171', marginTop: 14 }}>
              MANDATORY REJECTION REASON *
              <textarea
                value={rejectionReason}
                onChange={(e) => setRejectionReason(e.target.value)}
                placeholder="e.g. Incomplete institutional documentation or failed HIPAA/GDPR clinical boundary verification."
                required
                style={{ width: '100%', background: '#020617', border: '1px solid #ef4444', color: '#fff', padding: 8, borderRadius: 4, marginTop: 4, minHeight: 70, fontSize: 12 }}
              />
            </label>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10, marginTop: 20 }}>
              <button
                type="button"
                onClick={() => { setRejectModalOpen(false); setSelectedApp(null); setRejectionReason(''); }}
                style={{ background: '#1e293b', border: '1px solid #334155', color: '#cbd5e1', padding: '6px 14px', borderRadius: 4, cursor: 'pointer', fontSize: 12 }}
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleReject}
                disabled={actionBusy || !rejectionReason.trim()}
                style={{ background: '#dc2626', border: 'none', color: '#fff', padding: '6px 16px', borderRadius: 4, cursor: 'pointer', fontWeight: 600, fontSize: 12 }}
              >
                {actionBusy ? 'Rejecting...' : 'Confirm Rejection'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
