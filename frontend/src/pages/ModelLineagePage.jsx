import React, { useState } from 'react'
import { GitBranch, Layers3, CheckCircle, Clock, ShieldCheck, Cpu } from 'lucide-react'
import NeuralModel3D from '../components/visualizations/NeuralModel3D'

export default function ModelLineagePage({ data }) {
  const [selectedLayer, setSelectedLayer] = useState(null)
  const rounds = Array.isArray(data?.rounds) ? data.rounds : []

  return (
    <div className="page-container" style={{ padding: '24px' }}>
      <div style={{ marginBottom: 20 }}>
        <div style={{ color: '#00e5ff', fontSize: 11, fontWeight: 700, letterSpacing: '0.1em' }}>
          MODEL LIFECYCLE / EVOLUTIONARY PROVENANCE
        </div>
        <h1 style={{ fontSize: 26, margin: '4px 0', color: '#fff', display: 'flex', alignItems: 'center', gap: 10 }}>
          <GitBranch size={26} color="#00e5ff" />
          Global Model Lineage & Neural Topology
        </h1>
        <p style={{ color: '#94a3b8', fontSize: 13, margin: 0 }}>
          Track the cryptographic lineage of global model weights across federated aggregation rounds with full layer inspection.
        </p>
      </div>

      {/* 3D Neural Architecture Inspector */}
      <div style={{ marginBottom: 24 }}>
        <NeuralModel3D
          selectedLayer={selectedLayer}
          onSelectLayer={setSelectedLayer}
          height="340px"
        />
      </div>

      {/* Round Lineage Hierarchy */}
      <h3 style={{ fontSize: 16, color: '#f8fafc', marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
        <Cpu size={18} color="#38bdf8" />
        Sequential Federated Model Lineage
      </h3>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        {rounds.length === 0 ? (
          <div style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: 8, padding: 30, textAlign: 'center', color: '#64748b' }}>
            No model rounds recorded in lineage tree.
          </div>
        ) : (
          rounds.map((r, i) => {
            const isCompleted = r.status === 'COMPLETED'
            return (
              <div
                key={r.id || i}
                style={{
                  background: '#0f172a',
                  border: '1px solid #1e293b',
                  borderRadius: 8,
                  padding: 16,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  gap: 16,
                  position: 'relative'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                  <div style={{
                    width: 36,
                    height: 36,
                    borderRadius: '50%',
                    background: isCompleted ? 'rgba(16, 185, 129, 0.2)' : 'rgba(56, 189, 248, 0.2)',
                    color: isCompleted ? '#10b981' : '#38bdf8',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontWeight: 700,
                    fontSize: 14
                  }}>
                    {r.round_number ?? i + 1}
                  </div>

                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <strong style={{ fontSize: 14, color: '#f8fafc' }}>
                        Global Model v{r.round_number ?? i + 1}.0
                      </strong>
                      <span style={{
                        padding: '2px 8px',
                        borderRadius: 4,
                        fontSize: 10,
                        fontWeight: 700,
                        background: isCompleted ? 'rgba(16, 185, 129, 0.2)' : 'rgba(56, 189, 248, 0.2)',
                        color: isCompleted ? '#10b981' : '#38bdf8'
                      }}>
                        {r.status}
                      </span>
                    </div>
                    <div style={{ fontSize: 11, color: '#64748b', marginTop: 4 }}>
                      Round ID: <span style={{ fontFamily: 'monospace' }}>{r.id ? r.id.slice(0, 16) : '—'}</span> • Started: {r.started_at ? new Date(r.started_at).toLocaleString() : '—'}
                    </div>
                  </div>
                </div>

                <div style={{ display: 'flex', gap: 20, textAlign: 'right', fontSize: 11 }}>
                  <div>
                    <div style={{ color: '#64748b' }}>Accepted Updates</div>
                    <div style={{ fontWeight: 700, color: '#10b981', marginTop: 2 }}>{r.accepted_updates ?? 0}</div>
                  </div>
                  <div>
                    <div style={{ color: '#64748b' }}>Quarantined</div>
                    <div style={{ fontWeight: 700, color: '#ef4444', marginTop: 2 }}>{r.quarantined_updates ?? 0}</div>
                  </div>
                  <div>
                    <div style={{ color: '#64748b' }}>Participants</div>
                    <div style={{ fontWeight: 700, color: '#cbd5e1', marginTop: 2 }}>{r.participating_clients ?? 0}</div>
                  </div>
                </div>
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}
