import React, { useState, useEffect, useMemo } from 'react'
import {
  Compass,
  Layers,
  ShieldAlert,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  PieChart,
  HelpCircle,
  FileText,
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

export default function L5AttributePage({ data, token, onNavigate }) {
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

  const activeUpdate =
    parsedUpdates.find((u) => u.id === selectedUpdateId) || parsedUpdates[0] || null

  return (
    <div className="security-page">
      <SecurityPageHeader
        title="L5 — Multi-Signal Evidence Attribution Engine"
        subtitle="Synthesizing multi-layer forensics into probabilistic threat hypotheses and explanatory evidence graphs."
        badgeText="SECURITY LAYER 5 / ATTRIBUTION"
        rounds={rounds}
        selectedRoundId={activeRound?.id}
        onSelectRound={setSelectedRoundId}
        onRefresh={loadUpdates}
        loading={loading}
      />

      <SecurityPhilosophyBanner
        principle="EVIDENCE HYPOTHESIS != GROUND TRUTH"
        context="Simulator ground truth (e.g. injected label flips or scaling factors) is strictly quarantined from detection logic. L5 produces an empirical hypothesis derived strictly from observable sensor data across anomaly, influence, counterfactual effect, integrity, and node history."
      />

      {/* Attribution Canonical Weights Banner */}
      <div className="sec-panel">
        <div className="sec-panel-header">
          <h2>
            <PieChart size={16} />
            Attribution Synthesis Weighting Formula
          </h2>
          <span className="sec-badge sec-badge-neutral">CANONICAL WEIGHTS</span>
        </div>
        <div className="sec-panel-body">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 12 }}>
            <div style={{ background: '#161b22', padding: 12, borderRadius: 6, border: '1px solid #30363d' }}>
              <div style={{ color: '#00e5ff', fontSize: '0.75rem', fontWeight: 600 }}>ANOMALY (L2)</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 700, marginTop: 4 }}>30%</div>
              <div style={{ fontSize: '0.7rem', color: '#8b949e' }}>Robust MAD divergence</div>
            </div>
            <div style={{ background: '#161b22', padding: 12, borderRadius: 6, border: '1px solid #30363d' }}>
              <div style={{ color: '#ffb020', fontSize: '0.75rem', fontWeight: 600 }}>INFLUENCE (L3)</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 700, marginTop: 4 }}>25%</div>
              <div style={{ fontSize: '0.7rem', color: '#8b949e' }}>Validation pull vector</div>
            </div>
            <div style={{ background: '#161b22', padding: 12, borderRadius: 6, border: '1px solid #30363d' }}>
              <div style={{ color: '#ff3b5c', fontSize: '0.75rem', fontWeight: 600 }}>COUNTERFACTUAL (L4)</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 700, marginTop: 4 }}>30%</div>
              <div style={{ fontSize: '0.7rem', color: '#8b949e' }}>Leave-one-out Δ loss</div>
            </div>
            <div style={{ background: '#161b22', padding: 12, borderRadius: 6, border: '1px solid #30363d' }}>
              <div style={{ color: '#00e676', fontSize: '0.75rem', fontWeight: 600 }}>INTEGRITY (L0)</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 700, marginTop: 4 }}>10%</div>
              <div style={{ fontSize: '0.7rem', color: '#8b949e' }}>Artifact sanity & hash</div>
            </div>
            <div style={{ background: '#161b22', padding: 12, borderRadius: 6, border: '1px solid #30363d' }}>
              <div style={{ color: '#a371f7', fontSize: '0.75rem', fontWeight: 600 }}>HISTORY (ENCLAVE)</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 700, marginTop: 4 }}>5%</div>
              <div style={{ fontSize: '0.7rem', color: '#8b949e' }}>Prior round telemetry</div>
            </div>
          </div>
        </div>
      </div>

      {/* Attribution Detail Grid */}
      <div className="sec-grid-2col">
        {/* Table of Participant Hypotheses */}
        <div className="sec-panel">
          <div className="sec-panel-header">
            <h2>
              <Compass size={16} />
              Generated Attribution Hypotheses
            </h2>
            <span className="sec-badge sec-badge-neutral">{parsedUpdates.length} Updates</span>
          </div>
          <div className="sec-table-container">
            <table className="sec-table">
              <thead>
                <tr>
                  <th>NODE</th>
                  <th>HYPOTHESIS</th>
                  <th>SCORE</th>
                  <th>CONFIDENCE</th>
                  <th>SELECT</th>
                </tr>
              </thead>
              <tbody>
                {parsedUpdates.map((u) => {
                  const l5 = u.parsed.l5
                  const isSelected = u.id === activeUpdate?.id
                  const isAnomalous = l5.hypothesis.includes('ANOMALOUS')
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
                        <span
                          className={`sec-badge ${
                            isAnomalous ? 'sec-badge-quarantined' : 'sec-badge-accepted'
                          }`}
                        >
                          {l5.hypothesis || 'BENIGN'}
                        </span>
                      </td>
                      <td>
                        <span style={{ fontFamily: 'monospace' }}>
                          {formatNumber(l5.attribution_score, 2)}
                        </span>
                      </td>
                      <td>
                        <span style={{ fontFamily: 'monospace', color: '#00e5ff' }}>
                          {formatNumber(l5.confidence, 2)}
                        </span>
                      </td>
                      <td>
                        <button
                          type="button"
                          className={`security-btn ${isSelected ? 'security-btn-primary' : 'security-btn-secondary'}`}
                          style={{ padding: '3px 8px', fontSize: '0.7rem' }}
                          onClick={() => setSelectedUpdateId(u.id)}
                        >
                          {isSelected ? 'ACTIVE' : 'EXAMINE'}
                        </button>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Selected Update Evidence Dossier */}
        <div className="sec-panel">
          <div className="sec-panel-header">
            <h2>
              <FileText size={16} />
              Forensic Synthesis: {activeUpdate?.hospital_code || 'NODE'}
            </h2>
            {activeUpdate && (
              <span className="sec-badge sec-badge-info">
                CONFIDENCE: {formatNumber(activeUpdate.parsed.l5.confidence, 2)}
              </span>
            )}
          </div>
          <div className="sec-panel-body">
            {activeUpdate ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                <div>
                  <div style={{ fontSize: '0.75rem', color: '#8b949e' }}>PRIMARY ATTRIBUTION HYPOTHESIS</div>
                  <div
                    style={{
                      fontSize: '1.25rem',
                      fontWeight: 700,
                      color: activeUpdate.parsed.l5.hypothesis.includes('ANOMALOUS')
                        ? '#ff3b5c'
                        : '#00e676',
                      marginTop: 4,
                    }}
                  >
                    {activeUpdate.parsed.l5.hypothesis}
                  </div>
                </div>

                <div>
                  <div style={{ fontSize: '0.75rem', color: '#8b949e', marginBottom: 8 }}>
                    SUPPORTING EVIDENCE PILLARS
                  </div>
                  {activeUpdate.parsed.l5.supporting_evidence.length > 0 ? (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                      {activeUpdate.parsed.l5.supporting_evidence.map((ev, i) => (
                        <div
                          key={i}
                          style={{
                            background: '#161b22',
                            border: '1px solid #30363d',
                            padding: '8px 12px',
                            borderRadius: 6,
                            fontSize: '0.8125rem',
                            display: 'flex',
                            alignItems: 'center',
                            gap: 8,
                          }}
                        >
                          <span style={{ color: '#00e5ff' }}>•</span>
                          <span>{ev}</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div style={{ fontSize: '0.8125rem', color: '#8b949e' }}>
                      All layer metrics within nominal tolerances.
                    </div>
                  )}
                </div>

                <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 12 }}>
                  <button
                    type="button"
                    className="security-btn security-btn-primary"
                    onClick={() => onNavigate?.('trust')}
                  >
                    <span>EVALUATE TRUST ENGINE</span>
                    <ArrowRight size={14} />
                  </button>
                </div>
              </div>
            ) : (
              <div style={{ color: '#8b949e', textAlign: 'center', padding: 24 }}>
                Select an update to inspect attribution signals.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
