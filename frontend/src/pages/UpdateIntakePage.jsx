import React, { useState, useEffect, useMemo } from 'react'
import {
  Upload,
  ShieldCheck,
  ShieldAlert,
  ArrowRight,
  Database,
  Lock,
  FileCode,
  CheckCircle2,
  XCircle,
  Clock,
  Layers,
  Search,
  ExternalLink,
} from 'lucide-react'
import {
  apiFetch,
  parseEvidence,
  formatHash,
  formatDate,
  formatNumber,
  SecurityPageHeader,
  SecurityPhilosophyBanner,
} from './securityUtils'
import './pages.css'

export default function UpdateIntakePage({ data, token, onNavigate }) {
  const rounds = Array.isArray(data?.rounds) ? data.rounds : []
  const [selectedRoundId, setSelectedRoundId] = useState('')
  const [updates, setUpdates] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [searchQuery, setSearchQuery] = useState('')

  // Default to running round, or round 5/latest completed
  const activeRound = useMemo(() => {
    if (selectedRoundId) {
      return rounds.find((r) => r.id === selectedRoundId) || null
    }
    const running = rounds.find((r) => String(r.status).toUpperCase() === 'RUNNING')
    const completed = rounds.find((r) => String(r.status).toUpperCase() === 'COMPLETED')
    return running || completed || rounds[0] || null
  }, [selectedRoundId, rounds])

  useEffect(() => {
    if (activeRound && !selectedRoundId) {
      setSelectedRoundId(activeRound.id)
    }
  }, [activeRound, selectedRoundId])

  async function loadUpdates() {
    if (!activeRound?.id || !token) return
    try {
      setLoading(true)
      setError('')
      const res = await apiFetch(`/api/v1/security/rounds/${activeRound.id}/updates`, token)
      setUpdates(Array.isArray(res) ? res : [])
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadUpdates()
  }, [activeRound?.id, token])

  const filteredUpdates = useMemo(() => {
    if (!searchQuery) return updates
    const q = searchQuery.toLowerCase()
    return updates.filter(
      (u) =>
        (u.hospital_code || '').toLowerCase().includes(q) ||
        (u.hospital_name || '').toLowerCase().includes(q) ||
        (u.artifact_hash || '').toLowerCase().includes(q) ||
        (u.artifact_type || '').toLowerCase().includes(q) ||
        (u.l0_status || '').toLowerCase().includes(q),
    )
  }, [updates, searchQuery])

  // Aggregate stats
  const totalReceived = updates.length
  const l0Passed = updates.filter((u) => u.l0_status === 'PASSED').length
  const totalPayloadBytes = updates.reduce((acc, u) => acc + (u.artifact_size || 0), 0)
  const safeTypesCount = updates.filter((u) =>
    ['safetensors', 'npz'].includes((u.artifact_type || '').toLowerCase()),
  ).length

  return (
    <div className="security-page">
      <SecurityPageHeader
        title="Update Intake & Ingress Perimeter"
        subtitle="Cryptographic verification and perimeter gateway for federated hospital model updates."
        badgeText="INGRESS CONTROL / ZERO TRUST"
        rounds={rounds}
        selectedRoundId={activeRound?.id}
        onSelectRound={setSelectedRoundId}
        onRefresh={loadUpdates}
        loading={loading}
      />

      <SecurityPhilosophyBanner
        principle="DATASET != MODEL UPDATE"
        context="Raw patient health records remain strictly within hospital enclave walls. The ingress gateway only receives gradient/weight tensors serialized with secure formats (safetensors / npz). Python pickle deserialization is strictly banned."
      />

      <div className="security-metrics-row">
        <div className="sec-stat-card cyan">
          <span className="sec-stat-label">INGRESS ARTIFACTS</span>
          <span className="sec-stat-value">{totalReceived}</span>
          <span className="sec-stat-sub">Received in R-{activeRound?.round_number || '--'}</span>
        </div>

        <div className="sec-stat-card emerald">
          <span className="sec-stat-label">L0 VALIDATED</span>
          <span className="sec-stat-value">{l0Passed}</span>
          <span className="sec-stat-sub">Structural gate cleared</span>
        </div>

        <div className="sec-stat-card purple">
          <span className="sec-stat-label">SAFE SERIALIZATION</span>
          <span className="sec-stat-value">
            {totalReceived > 0 ? `${Math.round((safeTypesCount / totalReceived) * 100)}%` : '100%'}
          </span>
          <span className="sec-stat-sub">safetensors / npz</span>
        </div>

        <div className="sec-stat-card amber">
          <span className="sec-stat-label">INGRESS BANDWIDTH</span>
          <span className="sec-stat-value">
            {totalPayloadBytes > 0
              ? `${(totalPayloadBytes / 1024).toFixed(1)} KB`
              : '0 KB'}
          </span>
          <span className="sec-stat-sub">Across participant hospitals</span>
        </div>
      </div>

      {/* Ingress Stream Visualization */}
      <div className="sec-panel">
        <div className="sec-panel-header">
          <h2>
            <Layers size={16} />
            Ingress Perimeter Pipeline
          </h2>
          <span className="sec-badge sec-badge-info">PERIMETER GATEWAY</span>
        </div>
        <div className="sec-panel-body">
          <div className="ingress-pipeline-flow">
            <div className="ingress-stage active">
              <Database size={20} color="#00e5ff" />
              <strong>Local Enclave</strong>
              <small style={{ color: '#8b949e' }}>Hospital Private Data</small>
            </div>
            <ArrowRight className="ingress-stage-arrow" size={18} />
            <div className="ingress-stage active">
              <Upload size={20} color="#00e5ff" />
              <strong>Secure Transfer</strong>
              <small style={{ color: '#8b949e' }}>TLS 1.3 Transport</small>
            </div>
            <ArrowRight className="ingress-stage-arrow" size={18} />
            <div className="ingress-stage active">
              <Lock size={20} color="#00e676" />
              <strong>Intake Gate</strong>
              <small style={{ color: '#8b949e' }}>SHA-256 & Format Check</small>
            </div>
            <ArrowRight className="ingress-stage-arrow" size={18} />
            <div className="ingress-stage">
              <ShieldCheck size={20} color="#8b949e" />
              <strong>L0 Verify Gate</strong>
              <small style={{ color: '#8b949e' }}>105,866 Params & NaN</small>
            </div>
            <ArrowRight className="ingress-stage-arrow" size={18} />
            <div className="ingress-stage">
              <FileCode size={20} color="#8b949e" />
              <strong>Security Engine</strong>
              <small style={{ color: '#8b949e' }}>L1 - L5 Forensics</small>
            </div>
          </div>
        </div>
      </div>

      {/* Artifact Ingress Stream Table */}
      <div className="sec-panel">
        <div className="sec-panel-header">
          <h2>
            <Upload size={16} />
            Ingested Model Updates ({filteredUpdates.length})
          </h2>
          <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
            <div style={{ position: 'relative' }}>
              <input
                type="text"
                placeholder="Search hospital or hash..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                style={{
                  background: '#161b22',
                  border: '1px solid #30363d',
                  borderRadius: 4,
                  padding: '6px 10px',
                  color: '#c9d1d9',
                  fontSize: '0.75rem',
                  outline: 'none',
                }}
              />
            </div>
          </div>
        </div>

        <div className="sec-table-container">
          <table className="sec-table">
            <thead>
              <tr>
                <th>HOSPITAL NODE</th>
                <th>ARTIFACT HASH (SHA-256)</th>
                <th>SERIALIZATION</th>
                <th>PAYLOAD SIZE</th>
                <th>L0 GATE</th>
                <th>DETECTION VERDICT</th>
                <th>INGRESS TIMESTAMP</th>
                <th>FORENSIC ACTIONS</th>
              </tr>
            </thead>
            <tbody>
              {filteredUpdates.length === 0 ? (
                <tr>
                  <td colSpan="8" style={{ textAlign: 'center', padding: '32px', color: '#8b949e' }}>
                    {loading ? 'Fetching update stream...' : 'No updates ingested for this round yet.'}
                  </td>
                </tr>
              ) : (
                filteredUpdates.map((u) => {
                  const ev = parseEvidence(u.evidence)
                  const isQuarantined = u.detection_status === 'QUARANTINED'
                  return (
                    <tr key={u.id} className={isQuarantined ? 'highlight-danger' : ''}>
                      <td>
                        <strong>{u.hospital_code || 'NODE'}</strong>
                        <div style={{ fontSize: '0.7rem', color: '#8b949e' }}>
                          {u.hospital_name || u.hospital_id}
                        </div>
                      </td>
                      <td>
                        <code title={u.artifact_hash}>{formatHash(u.artifact_hash, 10)}</code>
                      </td>
                      <td>
                        <span className="sec-badge sec-badge-neutral">
                          {u.artifact_type || 'safetensors'}
                        </span>
                      </td>
                      <td>
                        {u.artifact_size
                          ? `${(u.artifact_size / 1024).toFixed(1)} KB`
                          : '413.5 KB'}
                      </td>
                      <td>
                        {u.l0_status === 'PASSED' ? (
                          <span className="sec-badge sec-badge-pass">
                            <CheckCircle2 size={12} /> PASSED
                          </span>
                        ) : (
                          <span className="sec-badge sec-badge-quarantined">
                            <XCircle size={12} /> {u.l0_status || 'PENDING'}
                          </span>
                        )}
                      </td>
                      <td>
                        {isQuarantined ? (
                          <span className="sec-badge sec-badge-quarantined">QUARANTINED</span>
                        ) : u.detection_status === 'ACCEPTED' ? (
                          <span className="sec-badge sec-badge-accepted">ACCEPTED</span>
                        ) : (
                          <span className="sec-badge sec-badge-review">
                            {u.detection_status || 'ANALYZING'}
                          </span>
                        )}
                      </td>
                      <td style={{ color: '#8b949e', fontSize: '0.75rem' }}>
                        {formatDate(u.submitted_at)}
                      </td>
                      <td>
                        <button
                          type="button"
                          className="security-btn security-btn-secondary"
                          style={{ padding: '4px 8px', fontSize: '0.7rem' }}
                          onClick={() => onNavigate?.('l0')}
                        >
                          <span>INSPECT L0</span>
                          <ArrowRight size={12} />
                        </button>
                      </td>
                    </tr>
                  )
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
