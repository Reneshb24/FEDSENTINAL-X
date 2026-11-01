// SecurityPipeline3D.jsx
// 3D visualisation of the security pipeline (L0‑L5 → TRUST → AGGREGATION)
// It reacts only to real backend events stored in the global Zustand store.

import React, { useMemo } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Html } from '@react-three/drei';
import * as THREE from 'three';
import { useAppStore } from '../../store/appStore';

// Simple helper to map stage to position in the pipeline
const stagePositions = {
  UPDATE_INTAKE: [0, 0, 0],
  L0: [2, 0, 0],
  L1: [4, 0, 0],
  L2: [6, 0, 0],
  L3: [8, 0, 0],
  L4: [10, 0, 0],
  L5: [12, 0, 0],
  TRUST: [14, 0, 0],
  AGGREGATION: [16, 0, 0],
  GLOBAL: [18, 0, 0],
};

function StageNode({ label, position, status }) {
  const colorMap = {
    PENDING: '#64748b',
    RUNNING: '#2563eb',
    PASSED: '#10b981',
    FAILED: '#ef4444',
    QUARANTINED: '#b91c1c',
    ACCEPTED: '#14b8a6',
  };
  const color = colorMap[status] || '#334155';
  return (
    <group position={position}>
      <mesh>
        <boxGeometry args={[1.6, 1, 0.5]} />
        <meshStandardMaterial color={color} />
      </mesh>
      <Html distanceFactor={12} center>
        <div style={{
          background: 'rgba(10,17,30,0.9)',
          padding: '4px 6px',
          borderRadius: '4px',
          color: '#fff',
          fontSize: '10px',
          whiteSpace: 'nowrap',
        }}>{label}</div>
      </Html>
    </group>
  );
}

function UpdateParticle({ update }) {
  // Position is interpolated between stages based on status.
  const stageOrder = ['UPDATE_INTAKE', 'L0', 'L1', 'L2', 'L3', 'L4', 'L5', 'TRUST', 'AGGREGATION'];
  const index = stageOrder.indexOf(update.status) >= 0 ? stageOrder.indexOf(update.status) : 0;
  const pos = stagePositions[stageOrder[index]] || [0, 0, 0];
  return (
    <mesh position={pos}>
      <sphereGeometry args={[0.2, 12, 12]} />
      <meshStandardMaterial color="#fbbf24" emissive="#fbbf24" emissiveIntensity={0.6} />
    </mesh>
  );
}

export default function SecurityPipeline3D() {
  const updatesMap = useAppStore(state => state.updates);
  const roundsMap = useAppStore(state => state.rounds);
  const updates = useMemo(() => Object.values(updatesMap || {}), [updatesMap]);
  const rounds = useMemo(() => Object.values(roundsMap || {}), [roundsMap]);
  const activeRound = useMemo(() => rounds.find(r => r.status === 'RUNNING' || r.status === 'OPEN') || {}, [rounds]);

  // Determine status for each stage (simple aggregation of updates at that stage)
  const stageStatus = {};
  updates.forEach(u => {
    const s = u.status;
    if (s && stagePositions[s]) {
      stageStatus[s] = stageStatus[s] === 'PASSED' ? 'PASSED' : s;
    }
  });

  return (
    <Canvas camera={{ position: [10, 6, 20], fov: 50 }} style={{ height: '100%', width: '100%' }}>
      <ambientLight intensity={0.5} />
      <directionalLight position={[5, 10, 5]} intensity={1} />
      <OrbitControls enablePan={false} />
      {/* Pipeline stages */}
      {Object.entries(stagePositions).map(([stage, pos]) => (
        <StageNode
          key={stage}
          label={stage.replace('_', ' ')}
          position={pos}
          status={stageStatus[stage] || 'PENDING'}
        />
      ))}
      {/* Render a particle for each update */}
      {updates.map(u => (
        <UpdateParticle key={u.id} update={u} />
      ))}
    </Canvas>
  );
}
