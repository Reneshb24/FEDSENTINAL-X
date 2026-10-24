import React, { useState, useEffect, useMemo } from 'react'
import {
  Sliders,
  GitCompare,
  TrendingDown,
  TrendingUp,
  AlertTriangle,
  ShieldCheck,
  CheckCircle2,
  ArrowRight,
  Eye,
  RefreshCw,
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

export default function L4SimulatePage({ data, token, onNavigate }) {
  const rounds = Array.isArray(data?.rounds) ? data.rounds : []
  const [selectedRoundId, setSelectedRoundId] = useState('')
  const [updates, setUpdates] = useState([])
  const [loading, setLoading] = useState(false)
  const [activeSimulationNode, setActiveSimulationNode] = useState(null)

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
      if (list.length > 0 && !activeSimulationNode) {
        setActiveSimulationNode(list[0])
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

  const selectedParsed = activeSimulationNode
    ? parsedUpdates.find((u) => u.id === activeSimulationNode.id) || parsedUpdates[0]
    : parsedUpdates[0]

  return (
    <div className="security-page">
      <SecurityPageHeader
        title="L4 — Counterfactual Simulation Engine"
        subtitle="Evaluating causal model behavior under inclusion vs exclusion hypothesis: What happens if this update is excluded?"
        badgeText="SECURITY LAYER 4 / COUNTERFACTUAL"
        rounds={rounds}
        selectedRoundId={activeRound?.id}
        onSelectRound={setSelectedRoundId}
        onRefresh={loadUpdates}
        loading={loading}
      />

      <SecurityPhilosophyBanner
        principle="COUNTERFACTUAL HARM != AUTOMATIC MALICE"
        context="An update whose exclusion improves global validation metrics is not automatically malicious. Complex non-IID partitions, client drift, or specialized label distribution can create counterfactual loss deltas without malicious intent."
      />

      <div className="security-metrics-row">
        <div className="sec-stat-card cyan">
          <span className="sec-stat-label">SIMULATION PARADIGM</span>
          <span className="sec-stat-value">LEAVE-ONE-OUT (LOO)</span>
          <span className="sec-stat-sub">Counterfactual cohort ablation</span>
        </div>

        <div className="sec-stat-card emerald">
          <span className="sec-stat-label">BENCHMARK TEST BED</span>
          <span className="sec-stat-value">1,000 EXAMPLES</span>
          <span className="sec-stat-sub">Central holdout validation sample</span>
        </div>

        <div className="sec-stat-card amber">
          <span className="sec-stat-label">SIMULATION ACCURACY IMPACT</span>
          <span className="sec-stat-value">
            {selectedParsed
              ? `${selectedParsed.parsed.l4.accuracy_delta > 0 ? '+' : ''}${(selectedParsed.parsed.l4.accuracy_delta * 100).toFixed(2)}%`
              : '--'}
          </span>
          <span className="sec-stat-sub">Δ Accuracy if excluded</span>
        </div>

        <div className="sec-stat-card purple">
          <span className="sec-stat-label">LOSS DELTA IMPACT</span>
          <span className="sec-stat-value">
            {selectedParsed
              ? `${selectedParsed.parsed.l4.loss_delta > 0 ? '+' : ''}${formatNumber(selectedParsed.parsed.l4.loss_delta, 4)}`
              : '--'}
          </span>
          <span className="sec-stat-sub">Δ Cross-entropy loss</span>
        </div>
      </div>

      {/* Counterfactual Interactive Sandbox */}
      {selectedParsed && (
        <div className="sec-panel">
          <div className="sec-panel-header">
            <h2>
              <GitCompare size={16} />
              Side-by-Side Counterfactual Comparison: {selectedParsed.hospital_code || 'NODE'}
            </h2>
            <span className="sec-badge sec-badge-info">CAUSAL HYPOTHESIS TEST</span>
          </div>
          <div className="sec-panel-body">
            <div className="sec-grid-2col">
              {/* With Update */}
              <div
                style={{
                  background: '#161b22',
                  border: '1px solid #30363d',
                  borderRadius: 8,
                  padding: 16,
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                  <strong style={{ color: '#00e5ff' }}>HYPOTHESIS A: INCLUDE UPDATE</strong>
                  <span className="sec-badge sec-badge-neutral">CURRENT STATE</span>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: '#8b949e', fontSize: '0.8125rem' }}>Global Accuracy Impact:</span>
                    <span style={{ fontWeight: 600 }}>Baseline</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: '#8b949e', fontSize: '0.8125rem' }}>Global Validation Loss:</span>
                    <span style={{ fontWeight: 600 }}>Baseline</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: '#8b949e', fontSize: '0.8125rem' }}>Cohort Aggregation:</span>
                    <span style={{ color: '#00e676' }}>Full Participant Cohort</span>
                  </div>
                </div>
              </div>

              {/* Without Update */}
              <div
                style={{
                  background: '#161b22',
                  border: '1px solid #30363d',
                  borderRadius: 8,
                  padding: 16,
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                  <strong style={{ color: '#ffb020' }}>HYPOTHESIS B: EXCLUDE UPDATE</strong>
                  <span className="sec-badge sec-badge-warning">SIMULATED LOO</span>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: '#8b949e', fontSize: '0.8125rem' }}>Δ Accuracy if Removed:</span>
                    <span
                      style={{
                        fontWeight: 700,
                        color: selectedParsed.parsed.l4.accuracy_delta < 0 ? '#00e676' : '#ff3b5c',
                      }}
                    >
                      {selectedParsed.parsed.l4.accuracy_delta > 0 ? '+' : ''}
                      {(selectedParsed.parsed.l4.accuracy_delta * 100).toFixed(2)}%
                    </span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: '#8b949e', fontSize: '0.8125rem' }}>Δ Loss if Removed:</span>
                    <span
                      style={{
                        fontWeight: 700,
                        color: selectedParsed.parsed.l4.loss_delta < 0 ? '#00e676' : '#ff3b5c',
                      }}
                    >
                      {selectedParsed.parsed.l4.loss_delta > 0 ? '+' : ''}
                      {formatNumber(selectedParsed.parsed.l4.loss_delta, 4)}
                    </span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: '#8b949e', fontSize: '0.8125rem' }}>Counterfactual Harm Flag:</span>
                    {selectedParsed.parsed.l4.harmful_counterfactual === 1 ? (
                      <span className="sec-badge sec-badge-quarantined">HARMFUL</span>
                    ) : (
                      <span className="sec-badge sec-badge-pass">NON-HARMFUL</span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* All Nodes Counterfactual Table */}
      <div className="sec-panel">
        <div className="sec-panel-header">
          <h2>
            <Sliders size={16} />
            Counterfactual Impact Summary by Node
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
                <th>Δ ACCURACY (IF REMOVED)</th>
                <th>Δ LOSS (IF REMOVED)</th>
                <th>COUNTERFACTUAL STATUS</th>
                <th>SIMULATE ACTION</th>
                <th>NEXT STAGE</th>
              </tr>
            </thead>
            <tbody>
              {parsedUpdates.length === 0 ? (
                <tr>
                  <td colSpan="6" style={{ textAlign: 'center', padding: '32px', color: '#8b949e' }}>
                    No counterfactual simulation data available.
                  </td>
                </tr>
              ) : (
                parsedUpdates.map((u) => {
                  const l4 = u.parsed.l4
                  const isSelected = u.id === selectedParsed?.id
                  return (
                    <tr key={u.id} style={{ background: isSelected ? 'rgba(0, 229, 255, 0.05)' : undefined }}>
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
                            fontWeight: 600,
                            color: l4.accuracy_delta < 0 ? '#ffb020' : '#00e676',
                          }}
                        >
                          {l4.accuracy_delta > 0 ? '+' : ''}
                          {(l4.accuracy_delta * 100).toFixed(2)}%
                        </span>
                      </td>
                      <td>
                        <span style={{ fontFamily: 'monospace' }}>
                          {l4.loss_delta > 0 ? '+' : ''}
                          {formatNumber(l4.loss_delta, 4)}
                        </span>
                      </td>
                      <td>
                        {l4.loss_delta < 0 ? (
                          <span className="sec-badge sec-badge-review">
                            REMOVAL REDUCES LOSS
                          </span>
                        ) : (
                          <span className="sec-badge sec-badge-pass">
                            BENIGN INCLUSION
                          </span>
                        )}
                      </td>
                      <td>
                        <button
                          type="button"
                          className={`security-btn ${isSelected ? 'security-btn-primary' : 'security-btn-secondary'}`}
                          style={{ padding: '3px 8px', fontSize: '0.7rem' }}
                          onClick={() => setActiveSimulationNode(u)}
                        >
                          {isSelected ? 'ACTIVE' : 'SELECT'}
                        </button>
                      </td>
                      <td>
                        <button
                          type="button"
                          className="security-btn security-btn-secondary"
                          style={{ padding: '4px 8px', fontSize: '0.7rem' }}
                          onClick={() => onNavigate?.('l5')}
                        >
                          <span>L5 ATTRIBUTE</span>
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
