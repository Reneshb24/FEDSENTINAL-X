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

export default function SecurityPipeline3D({ currentStep, activeUpdates, height = '260px' }) {
  const updatesMap = useAppStore(state => state.updates);
  const roundsMap = useAppStore(state => state.rounds);
  const storeUpdates = useMemo(() => Object.values(updatesMap || {}), [updatesMap]);
  const updates = activeUpdates && activeUpdates.length > 0 ? activeUpdates : storeUpdates;

  const stageKeys = ['UPDATE_INTAKE', 'L0', 'L1', 'L2', 'L3', 'L4', 'L5', 'TRUST', 'AGGREGATION', 'GLOBAL'];

  const stageStatus = useMemo(() => {
    const s = {};
    stageKeys.forEach((key, idx) => {
      if (currentStep !== undefined && currentStep !== null) {
        if (idx < currentStep - 1) {
          s[key] = 'PASSED';
        } else if (idx === currentStep - 1) {
          s[key] = 'RUNNING';
        } else {
          s[key] = 'PENDING';
        }
      } else {
        s[key] = 'PENDING';
      }
    });
    return s;
  }, [currentStep]);

  return (
    <div style={{ height, width: '100%', position: 'relative', borderRadius: 8, overflow: 'hidden', background: '#070c11', border: '1px solid #1e293b', marginBottom: 16 }}>
      <Canvas camera={{ position: [9, 5, 16], fov: 45 }} style={{ height: '100%', width: '100%' }}>
        <ambientLight intensity={0.6} />
        <directionalLight position={[5, 10, 5]} intensity={1.2} />
        <OrbitControls enableZoom={true} zoomSpeed={1.0} minDistance={2} maxDistance={35} enablePan={true} panSpeed={1.0} enableRotate={true} rotateSpeed={0.8} enableDamping={true} dampingFactor={0.05} autoRotate autoRotateSpeed={0.4} />
        {/* Pipeline stages */}
        {Object.entries(stagePositions).map(([stage, pos]) => (
          <StageNode
            key={stage}
            label={stage.replace('_', ' ')}
            position={pos}
            status={stageStatus[stage] || 'PENDING'}
          />
        ))}
        {/* Render animated particles representing hospital model updates */}
        {updates.slice(0, 15).map((u, i) => {
          const isQuarantined = u.detection_status === 'QUARANTINED';
          const stageIdx = currentStep ? Math.min(currentStep - 1, stageKeys.length - 1) : 0;
          const stageName = stageKeys[stageIdx];
          const basePos = stagePositions[stageName] || [0, 0, 0];
          const offsetPos = [
            basePos[0] + ((i % 5) - 2) * 0.35,
            basePos[1] + (isQuarantined && stageIdx >= 4 ? -1.8 : ((Math.floor(i / 5) - 1) * 0.35)),
            basePos[2] + ((i % 3) - 1) * 0.25,
          ];
          const color = isQuarantined && stageIdx >= 4 ? '#ef4444' : (stageIdx >= 8 ? '#10b981' : '#00e5ff');
          return (
            <mesh key={u.id || i} position={offsetPos}>
              <sphereGeometry args={[0.22, 14, 14]} />
              <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.8} />
            </mesh>
          );
        })}
      </Canvas>
      <div style={{ position: 'absolute', bottom: 8, right: 12, fontSize: 10, color: '#64748b', pointerEvents: 'none', background: 'rgba(5,8,12,0.7)', padding: '2px 8px', borderRadius: 4 }}>
        3D Zero-Trust Security Pipeline · Stage {currentStep || 1} of 10 · {updates.length} Updates Ingested
      </div>
    </div>
  );
}
