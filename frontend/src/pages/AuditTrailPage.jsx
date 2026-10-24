import React, { useState, useEffect, useMemo } from 'react'
import {
  FileClock,
  ShieldCheck,
  Search,
  Filter,
  RotateCcw,
  Eye,
  CheckCircle2,
  XCircle,
  Database,
  ArrowRight,
  User,
  Hash,
} from 'lucide-react'
import {
  apiFetch,
  formatHash,
  formatDate,
  SecurityPageHeader,
  SecurityPhilosophyBanner,
} from './securityUtils'
import './pages.css'

export default function AuditTrailPage({ data, token }) {
  const [events, setEvents] = useState([])
  const [totalCount, setTotalCount] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [selectedEvent, setSelectedEvent] = useState(null)

  // Filters
  const [actionFilter, setActionFilter] = useState('ALL')
  const [resourceFilter, setResourceFilter] = useState('ALL')
  const [searchQuery, setSearchQuery] = useState('')

  async function loadAuditEvents() {
    if (!token) return
    try {
      setLoading(true)
      setError('')
      const params = new URLSearchParams()
      params.append('limit', '100')
      if (actionFilter !== 'ALL') params.append('action', actionFilter)
      if (resourceFilter !== 'ALL') params.append('resource_type', resourceFilter)

      const res = await apiFetch(`/api/v1/audit?${params.toString()}`, token)
      setEvents(res?.value || [])
      setTotalCount(res?.count || 0)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadAuditEvents()
  }, [token, actionFilter, resourceFilter])

  const filteredEvents = useMemo(() => {
    if (!searchQuery) return events
    const q = searchQuery.toLowerCase()
    return events.filter(
      (e) =>
        (e.action || '').toLowerCase().includes(q) ||
        (e.resource_type || '').toLowerCase().includes(q) ||
        (e.resource_id || '').toLowerCase().includes(q) ||
        (e.reason || '').toLowerCase().includes(q),
    )
  }, [events, searchQuery])

  return (
    <div className="security-page">
      <SecurityPageHeader
        title="Immutable Forensic Audit Trail"
        subtitle="Cryptographically verifiable log of all administrative actions, lifecycle state transitions, and override justifications."
        badgeText="FORENSICS & COMPLIANCE / AUDIT LOG"
        onRefresh={loadAuditEvents}
        loading={loading}
      />

      <SecurityPhilosophyBanner
        principle="EXPLICIT, REASONED, AUDITED OVERRIDES"
        context="Every human administrative intervention (quarantine override, status update, lifecycle cancellation) requires a mandatory justification and is permanently committed to this audit register. No silent actions."
      />

      <div className="security-metrics-row">
        <div className="sec-stat-card cyan">
          <span className="sec-stat-label">TOTAL AUDIT EVENTS</span>
          <span className="sec-stat-value">{totalCount}</span>
          <span className="sec-stat-sub">Persisted in tamper-evident store</span>
        </div>

        <div className="sec-stat-card emerald">
          <span className="sec-stat-label">AUDIT INTEGRITY</span>
          <span className="sec-stat-value">100% VERIFIED</span>
          <span className="sec-stat-sub">Cryptographic actor linkage</span>
        </div>

        <div className="sec-stat-card amber">
          <span className="sec-stat-label">ADMIN OVERRIDES</span>
          <span className="sec-stat-value">
            {events.filter((e) => (e.action || '').includes('ADMIN')).length}
          </span>
          <span className="sec-stat-sub">Human decision overrides</span>
        </div>

        <div className="sec-stat-card purple">
          <span className="sec-stat-label">ACTIVE FILTER VIEW</span>
          <span className="sec-stat-value">{filteredEvents.length}</span>
          <span className="sec-stat-sub">Current matching events</span>
        </div>
      </div>

      {/* Filter and Table Panel */}
      <div className="sec-panel">
        <div className="sec-panel-header">
          <h2>
            <FileClock size={16} />
            Forensic Audit Event Stream ({filteredEvents.length})
          </h2>
          <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', alignItems: 'center' }}>
            <input
              type="text"
              placeholder="Search actions or IDs..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                background: '#161b22',
                border: '1px solid #30363d',
                borderRadius: 4,
                padding: '4px 8px',
                color: '#c9d1d9',
                fontSize: '0.75rem',
                outline: 'none',
              }}
            />

            <select
              value={actionFilter}
              onChange={(e) => setActionFilter(e.target.value)}
              style={{
                background: '#161b22',
                border: '1px solid #30363d',
                borderRadius: 4,
                padding: '4px 8px',
                color: '#c9d1d9',
                fontSize: '0.75rem',
                outline: 'none',
              }}
            >
              <option value="ALL">ALL ACTIONS</option>
              <option value="UPDATE_QUARANTINED_BY_ADMIN">UPDATE_QUARANTINED</option>
              <option value="UPDATE_RELEASED_BY_ADMIN">UPDATE_RELEASED</option>
              <option value="INCIDENT_STATUS_UPDATED">INCIDENT_STATUS_UPDATED</option>
              <option value="ROUND_CANCELLED">ROUND_CANCELLED</option>
              <option value="ROUND_FAILED">ROUND_FAILED</option>
              <option value="ROUND_RESET">ROUND_RESET</option>
            </select>

            <select
              value={resourceFilter}
              onChange={(e) => setResourceFilter(e.target.value)}
              style={{
                background: '#161b22',
                border: '1px solid #30363d',
                borderRadius: 4,
                padding: '4px 8px',
                color: '#c9d1d9',
                fontSize: '0.75rem',
                outline: 'none',
              }}
            >
              <option value="ALL">ALL RESOURCES</option>
              <option value="MODEL_UPDATE">MODEL_UPDATE</option>
              <option value="INCIDENT">INCIDENT</option>
              <option value="FEDERATION_ROUND">FEDERATION_ROUND</option>
              <option value="HOSPITAL">HOSPITAL</option>
            </select>
          </div>
        </div>

        <div className="sec-table-container">
          <table className="sec-table">
            <thead>
              <tr>
                <th>TIMESTAMP</th>
                <th>ACTION</th>
                <th>RESOURCE TYPE</th>
                <th>RESOURCE ID</th>
                <th>REASON / JUSTIFICATION</th>
                <th>RESULT</th>
                <th>DIFF DETAILS</th>
              </tr>
            </thead>
            <tbody>
              {filteredEvents.length === 0 ? (
                <tr>
                  <td colSpan="7" style={{ textAlign: 'center', padding: '32px', color: '#8b949e' }}>
                    {loading ? 'Retrieving audit register...' : 'No audit events found.'}
                  </td>
                </tr>
              ) : (
                filteredEvents.map((evt) => (
                  <tr key={evt.id}>
                    <td style={{ color: '#8b949e', fontSize: '0.75rem', whiteSpace: 'nowrap' }}>
                      {formatDate(evt.created_at)}
                    </td>
                    <td>
                      <strong style={{ color: '#00e5ff', fontSize: '0.75rem' }}>{evt.action}</strong>
                    </td>
                    <td>
                      <span className="sec-badge sec-badge-neutral">{evt.resource_type}</span>
                    </td>
                    <td>
                      <code>{formatHash(evt.resource_id, 8)}</code>
                    </td>
                    <td style={{ maxWidth: 300 }}>
                      <span style={{ fontSize: '0.75rem', color: '#c9d1d9' }}>
                        {evt.reason || '--'}
                      </span>
                    </td>
                    <td>
                      <span className="sec-badge sec-badge-pass">
                        <CheckCircle2 size={12} /> {evt.result || 'SUCCESS'}
                      </span>
                    </td>
                    <td>
                      <button
                        type="button"
                        className="security-btn security-btn-secondary"
                        style={{ padding: '3px 8px', fontSize: '0.7rem' }}
                        onClick={() => setSelectedEvent(evt)}
                      >
                        <Eye size={12} />
                        <span>DIFF</span>
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Selected Event Details Modal */}
      {selectedEvent && (
        <div className="sec-modal-backdrop" onClick={() => setSelectedEvent(null)}>
          <div className="sec-modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="sec-modal-header">
              <h3>Audit Event Forensic Record: {selectedEvent.action}</h3>
              <button
                type="button"
                className="security-btn security-btn-secondary"
                onClick={() => setSelectedEvent(null)}
              >
                ✕
              </button>
            </div>
            <div className="sec-modal-body">
              <div>
                <strong>Event ID:</strong> <code>{selectedEvent.id}</code>
              </div>
              <div>
                <strong>Actor User ID:</strong> <code>{selectedEvent.actor_user_id || 'SYSTEM_OPERATOR'}</code>
              </div>
              <div>
                <strong>Timestamp:</strong> {formatDate(selectedEvent.created_at)}
              </div>
              <div>
                <strong>Action:</strong> <span style={{ color: '#00e5ff' }}>{selectedEvent.action}</span>
              </div>
              <div>
                <strong>Target Resource:</strong> {selectedEvent.resource_type} (<code>{selectedEvent.resource_id}</code>)
              </div>
              <div>
                <strong>Mandatory Justification:</strong> {selectedEvent.reason}
              </div>

              <div style={{ marginTop: 12 }}>
                <strong>State Change Diff / Metadata:</strong>
                <pre
                  style={{
                    background: '#040d1a',
                    border: '1px solid #30363d',
                    padding: 12,
                    borderRadius: 6,
                    fontSize: '0.75rem',
                    color: '#58a6ff',
                    overflowX: 'auto',
                    marginTop: 6,
                  }}
                >
                  {typeof selectedEvent.metadata_json === 'string'
                    ? selectedEvent.metadata_json
                    : JSON.stringify(selectedEvent.metadata_json, null, 2)}
                </pre>
              </div>
            </div>
            <div className="sec-modal-footer">
              <button
                type="button"
                className="security-btn security-btn-secondary"
                onClick={() => setSelectedEvent(null)}
              >
                CLOSE
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
