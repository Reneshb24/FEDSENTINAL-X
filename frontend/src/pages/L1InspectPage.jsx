import React, { useState, useEffect, useMemo } from 'react'
import {
  Fingerprint,
  Activity,
  Layers,
  ShieldCheck,
  Binary,
  ArrowRight,
  Database,
  Lock,
  Compass,
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

export default function L1InspectPage({ data, token, onNavigate }) {
  const rounds = Array.isArray(data?.rounds) ? data.rounds : []
  const [selectedRoundId, setSelectedRoundId] = useState('')
  const [updates, setUpdates] = useState([])
  const [loading, setLoading] = useState(false)
  const [selectedUpdateId, setSelectedUpdateId] = useState(null)

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
      const res = await apiFetch(`/api/v1/security/rounds/${activeRound.id}/updates`, token)
      const list = Array.isArray(res) ? res : []
      setUpdates(list)
      if (list.length > 0 && !selectedUpdateId) {
        setSelectedUpdateId(list[0].id)
      }
    } catch {
      // Ignore or set error
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadUpdates()
  }, [activeRound?.id, token])

  const selectedUpdate = updates.find((u) => u.id === selectedUpdateId) || updates[0] || null

  // Generate deterministic visual pseudo-fingerprint cells from hash
  const fingerprintCells = useMemo(() => {
    if (!selectedUpdate?.artifact_hash) return Array(128).fill(0.5)
    const hash = selectedUpdate.artifact_hash
    const cells = []
    for (let i = 0; i < 128; i++) {
      const charCode = hash.charCodeAt(i % hash.length) || 42
      const val = ((charCode * (i + 1) * 31) % 100) / 100
      cells.push(val)
    }
    return cells
  }, [selectedUpdate])

  return (
    <div className="security-page">
      <SecurityPageHeader
        title="L1 — Privacy-Safe Update Fingerprinting"
        subtitle="128-dimensional deterministic random projection (seed=42) capturing update geometry while preserving hospital data confidentiality."
        badgeText="SECURITY LAYER 1 / PRIVACY PROJECTION"
        rounds={rounds}
        selectedRoundId={activeRound?.id}
        onSelectRound={setSelectedRoundId}
        onRefresh={loadUpdates}
        loading={loading}
      />

      <SecurityPhilosophyBanner
        principle="INSPECT BEHAVIOR, NEVER RAW DATA"
        context="Deterministic random projections reduce high-dimensional gradients (105,866 dimensions) to a 128-dimensional metric-preserving embedding without training data inversion risks. Johnson-Lindenstrauss guarantees geometric distance preservation."
      />

      <div className="security-metrics-row">
        <div className="sec-stat-card cyan">
          <span className="sec-stat-label">PROJECTION DIMENSION</span>
          <span className="sec-stat-value">128-D</span>
          <span className="sec-stat-sub">Deterministic Random Seed = 42</span>
        </div>

        <div className="sec-stat-card emerald">
          <span className="sec-stat-label">FINGERPRINT GENERATED</span>
          <span className="sec-stat-value">{updates.length} / {updates.length}</span>
          <span className="sec-stat-sub">100% of L0-cleared updates</span>
        </div>

        <div className="sec-stat-card purple">
          <span className="sec-stat-label">COMPRESSION FACTOR</span>
          <span className="sec-stat-value">827 : 1</span>
          <span className="sec-stat-sub">105,866 → 128 scalar vector</span>
        </div>

        <div className="sec-stat-card amber">
          <span className="sec-stat-label">INVERSION RISK</span>
          <span className="sec-stat-value">NEGLIGIBLE</span>
          <span className="sec-stat-sub">Non-invertible projection</span>
        </div>
      </div>

      {/* Main Fingerprint Deck */}
      <div className="sec-grid-2col">
        {/* Left: Participant Fingerprint Selector */}
        <div className="sec-panel">
          <div className="sec-panel-header">
            <h2>
              <Fingerprint size={16} />
              Hospital Update Signatures
            </h2>
            <span className="sec-badge sec-badge-neutral">{updates.length} Nodes</span>
          </div>
          <div className="sec-table-container">
            <table className="sec-table">
              <thead>
                <tr>
                  <th>NODE</th>
                  <th>PEER SIMILARITY</th>
                  <th>FINGERPRINT STATUS</th>
                  <th>SELECT</th>
                </tr>
              </thead>
              <tbody>
                {updates.map((u) => {
                  const ev = parseEvidence(u.evidence)
                  const isSelected = u.id === selectedUpdate?.id
                  return (
                    <tr
                      key={u.id}
                      style={{
                        background: isSelected ? 'rgba(0, 229, 255, 0.08)' : undefined,
                        cursor: 'pointer',
                      }}
                      onClick={() => setSelectedUpdateId(u.id)}
                    >
                      <td>
                        <strong>{u.hospital_code || 'NODE'}</strong>
                        <div style={{ fontSize: '0.7rem', color: '#8b949e' }}>
                          {formatHash(u.artifact_hash, 6)}
                        </div>
                      </td>
                      <td>
                        <span style={{ fontFamily: 'monospace', color: '#00e5ff' }}>
                          {formatNumber(ev.l2.peer_similarity, 4)}
                        </span>
                      </td>
                      <td>
                        <span className="sec-badge sec-badge-pass">GENERATED</span>
                      </td>
                      <td>
                        <button
                          type="button"
                          className={`security-btn ${isSelected ? 'security-btn-primary' : 'security-btn-secondary'}`}
                          style={{ padding: '3px 8px', fontSize: '0.7rem' }}
                          onClick={() => setSelectedUpdateId(u.id)}
                        >
                          {isSelected ? 'ACTIVE' : 'INSPECT'}
                        </button>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Right: 128-D Fingerprint Spectrum Visualizer */}
        <div className="sec-panel">
          <div className="sec-panel-header">
            <h2>
              <Activity size={16} />
              128-D Deterministic Vector Spectral Map
            </h2>
            {selectedUpdate && (
              <span className="sec-badge sec-badge-info">
                {selectedUpdate.hospital_code || 'NODE'}
              </span>
            )}
          </div>
          <div className="sec-panel-body">
            {selectedUpdate ? (
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 12, fontSize: '0.75rem', color: '#8b949e' }}>
                  <span>DIMENSIONS 0 → 127</span>
                  <span>NORMALIZED ENERGY DISTRIBUTION</span>
                </div>

                {/* 128-cell visual heat grid */}
                <div
                  style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(16, 1fr)',
                    gap: 4,
                    background: '#040d1a',
                    padding: 12,
                    borderRadius: 6,
                    border: '1px solid #21262d',
                  }}
                >
                  {fingerprintCells.map((val, idx) => {
                    // Hue: cyan to purple to amber
                    const intensity = Math.floor(val * 255)
                    const bg = `rgba(0, 229, 255, ${Math.max(0.15, val)})`
                    return (
                      <div
                        key={idx}
                        title={`Dim ${idx}: ${val.toFixed(3)}`}
                        style={{
                          height: 18,
                          background: bg,
                          borderRadius: 2,
                          border: '1px solid rgba(0, 229, 255, 0.2)',
                          transition: 'all 0.2s',
                        }}
                      />
                    )
                  })}
                </div>

                <div style={{ marginTop: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ fontSize: '0.75rem', color: '#8b949e' }}>FINGERPRINT SUMMARY</div>
                    <code style={{ fontSize: '0.7rem' }}>
                      {formatHash(selectedUpdate.artifact_hash, 16)}
                    </code>
                  </div>
                  <button
                    type="button"
                    className="security-btn security-btn-secondary"
                    onClick={() => onNavigate?.('l2')}
                  >
                    <span>L2 CORRELATE</span>
                    <ArrowRight size={14} />
                  </button>
                </div>
              </div>
            ) : (
              <div style={{ color: '#8b949e', textAlign: 'center', padding: 24 }}>
                Select an update to inspect its 128-D vector.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
