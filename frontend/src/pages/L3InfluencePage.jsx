import React, { useState, useEffect, useMemo } from 'react'
import {
  TrendingUp,
  Activity,
  ShieldCheck,
  ShieldAlert,
  ArrowRight,
  Sliders,
  Compass,
  AlertTriangle,
  CheckCircle2,
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

export default function L3InfluencePage({ data, token, onNavigate }) {
  const rounds = Array.isArray(data?.rounds) ? data.rounds : []
  const [selectedRoundId, setSelectedRoundId] = useState('')
  const [updates, setUpdates] = useState([])
  const [loading, setLoading] = useState(false)

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
      setUpdates(Array.isArray(res) ? res : [])
    } catch {
      // Ignore
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadUpdates()
  }, [activeRound?.id, token])

  const parsedUpdates = useMemo(() => {
    return updates.map((u) => ({
      ...u,
      parsed: parseEvidence(u.evidence),
    }))
  }, [updates])

  const maxInfluence = Math.max(0, ...parsedUpdates.map((u) => Math.abs(u.parsed.l3.influence_score)))

  return (
    <div className="security-page">
      <SecurityPageHeader
        title="L3 — Gradient Influence Analysis"
        subtitle="Empirical influence estimation measuring each participant update's directional pull on global model trajectory."
        badgeText="SECURITY LAYER 3 / INFLUENCE"
        rounds={rounds}
        selectedRoundId={activeRound?.id}
        onSelectRound={setSelectedRoundId}
        onRefresh={loadUpdates}
        loading={loading}
      />

      <SecurityPhilosophyBanner
        principle="INFLUENCE != MALICIOUSNESS"
        context="Influence is evidence of impact, not proof of wrongdoing. High-performing updates with rich clinical pathology naturally exert high influence on gradient descent. Influence only becomes suspicious when correlated with counterfactual harm."
      />

      <div className="security-metrics-row">
        <div className="sec-stat-card cyan">
          <span className="sec-stat-label">INFLUENCE EVALUATOR</span>
          <span className="sec-stat-value">VALIDATION TRAJECTORY</span>
          <span className="sec-stat-sub">Directional gradient alignment</span>
        </div>

        <div className="sec-stat-card emerald">
          <span className="sec-stat-label">EVALUATED UPDATES</span>
          <span className="sec-stat-value">{parsedUpdates.length}</span>
          <span className="sec-stat-sub">Cleared through L0 & L1</span>
        </div>

        <div className="sec-stat-card amber">
          <span className="sec-stat-label">MAX DIRECTIONAL PULL</span>
          <span className="sec-stat-value">{formatNumber(maxInfluence, 2)}</span>
          <span className="sec-stat-sub">Highest absolute influence score</span>
        </div>

        <div className="sec-stat-card purple">
          <span className="sec-stat-label">NEXT CORRELATION GATE</span>
          <span className="sec-stat-value">L4 SIMULATION</span>
          <span className="sec-stat-sub">Counterfactual delta testing</span>
        </div>
      </div>

      {/* Influence Table */}
      <div className="sec-panel">
        <div className="sec-panel-header">
          <h2>
            <TrendingUp size={16} />
            Participant Update Influence Signatures
          </h2>
          <span className="sec-badge sec-badge-neutral">
            ROUND R-{activeRound?.round_number || '--'}
          </span>
        </div>

        <div className="sec-table-container">
          <table className="sec-table">
            <thead>
              <tr>
                <th>HOSPITAL NODE</th>
                <th>INFLUENCE SCORE</th>
                <th>VALIDATION DELTA (Δ LOSS)</th>
                <th>DIRECTIONAL PULL</th>
                <th>HARMFUL INFLUENCE</th>
                <th>NEXT LAYER</th>
              </tr>
            </thead>
            <tbody>
              {parsedUpdates.length === 0 ? (
                <tr>
                  <td colSpan="6" style={{ textAlign: 'center', padding: '32px', color: '#8b949e' }}>
                    {loading ? 'Analyzing gradient influence...' : 'No updates for this round.'}
                  </td>
                </tr>
              ) : (
                parsedUpdates.map((u) => {
                  const l3 = u.parsed.l3
                  const isHighPull = Math.abs(l3.influence_score) > 5.0
                  return (
                    <tr key={u.id} className={isHighPull ? 'highlight-danger' : ''}>
                      <td>
                        <strong>{u.hospital_code || 'NODE'}</strong>
                        <div style={{ fontSize: '0.7rem', color: '#8b949e' }}>
                          {u.hospital_name || u.hospital_id}
                        </div>
                      </td>
                      <td>
                        <span
                          style={{
                            fontFamily: 'monospace',
                            fontWeight: 700,
                            color: isHighPull ? '#ffb020' : '#58a6ff',
                          }}
                        >
                          {l3.influence_score > 0 ? `+${formatNumber(l3.influence_score, 4)}` : formatNumber(l3.influence_score, 4)}
                        </span>
                      </td>
                      <td>
                        <span style={{ fontFamily: 'monospace' }}>
                          {l3.validation_delta > 0 ? `+${formatNumber(l3.validation_delta, 6)}` : formatNumber(l3.validation_delta, 6)}
                        </span>
                      </td>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          <div style={{ width: 80 }} className="sec-bar-meter">
                            <div
                              className={`sec-bar-meter-fill ${isHighPull ? 'amber' : 'cyan'}`}
                              style={{ width: `${Math.min(100, (Math.abs(l3.influence_score) / Math.max(1, maxInfluence)) * 100)}%` }}
                            />
                          </div>
                          <span style={{ fontSize: '0.75rem', color: '#8b949e' }}>
                            {isHighPull ? 'DOMINANT PULL' : 'NOMINAL'}
                          </span>
                        </div>
                      </td>
                      <td>
                        {l3.harmful_influence === 1.0 ? (
                          <span className="sec-badge sec-badge-quarantined">
                            <AlertTriangle size={12} /> HARMFUL DETECTED
                          </span>
                        ) : (
                          <span className="sec-badge sec-badge-pass">
                            <CheckCircle2 size={12} /> BENIGN DRIFT
                          </span>
                        )}
                      </td>
                      <td>
                        <button
                          type="button"
                          className="security-btn security-btn-secondary"
                          style={{ padding: '4px 8px', fontSize: '0.7rem' }}
                          onClick={() => onNavigate?.('l4')}
                        >
                          <span>L4 SIMULATE</span>
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
