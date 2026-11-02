import React, { useRef, useMemo, useState } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Html } from '@react-three/drei'
import * as THREE from 'three'

function ThresholdPlane({ y, color, label }) {
  return (
    <group position={[0, y, 0]}>
      <mesh rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[6, 6]} />
        <meshBasicMaterial color={color} transparent opacity={0.12} side={THREE.DoubleSide} />
      </mesh>
      <lineSegments>
        <edgesGeometry args={[new THREE.PlaneGeometry(6, 6)]} />
        <lineBasicMaterial color={color} transparent opacity={0.3} />
      </lineSegments>
      <Html position={[3.1, 0, 3.1]} center>
        <span style={{ fontSize: '8px', color, fontWeight: 700, letterSpacing: '0.05em' }}>
          {label}
        </span>
      </Html>
    </group>
  )
}

function TrustNode({ record, index, total }) {
  const meshRef = useRef()
  const [hovered, setHovered] = useState(false)

  const score = Number(record.score ?? record.trust_score ?? 0.85)
  const compliance = Number(record.compliance ?? 0.9)
  const consistency = Number(record.consistency ?? 0.88)

  // Map into 3D box: X in [-2.5, 2.5], Y in [-1.5, 1.5] (mapped from score 0-1), Z in [-2.5, 2.5]
  const x = (compliance - 0.5) * 5
  const y = (score - 0.5) * 3
  const z = (consistency - 0.5) * 5

  const status = String(record.decision || record.status || (score < 0.4 ? 'QUARANTINED' : score < 0.7 ? 'REVIEW' : 'TRUSTED')).toUpperCase()

  const color = useMemo(() => {
    if (status === 'QUARANTINED') return '#ef4444'
    if (status === 'REVIEW' || status === 'MONITOR') return '#f59e0b'
    return '#10b981'
  }, [status])

  useFrame((state, delta) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += delta * 0.6
      if (hovered) {
        meshRef.current.scale.setScalar(1.3 + Math.sin(state.clock.elapsedTime * 6) * 0.1)
      } else {
        meshRef.current.scale.setScalar(1.0)
      }
    }
  })

  return (
    <group position={[x, y, z]}>
      {/* Stem to base */}
      <line>
        <bufferGeometry attach="geometry" {...new THREE.BufferGeometry().setFromPoints([
          new THREE.Vector3(0, 0, 0),
          new THREE.Vector3(0, -1.5 - y, 0)
        ])} />
        <lineBasicMaterial attach="material" color={color} transparent opacity={0.25} />
      </line>

      <mesh
        ref={meshRef}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
      >
        <sphereGeometry args={[0.18, 16, 16]} />
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.8} />
      </mesh>

      {hovered && (
        <Html position={[0, 0.4, 0]} center>
          <div style={{
            background: 'rgba(6, 15, 24, 0.95)',
            border: `1px solid ${color}`,
            borderRadius: '4px',
            padding: '4px 8px',
            color: '#fff',
            fontSize: '9px',
            whiteSpace: 'nowrap',
            pointerEvents: 'none',
          }}>
            <strong>{record.hospital_code || record.hospital_id || `NODE-${index + 1}`}</strong>
            <div>TRUST: {(score * 100).toFixed(1)}% ({status})</div>
          </div>
        </Html>
      )}
    </group>
  )
}

export default function TrustMatrix3D({ trustRecords = [], height = '260px' }) {
  const records = useMemo(() => {
    if (Array.isArray(trustRecords) && trustRecords.length > 0) return trustRecords
    // Synthetic fallback distribution if records not yet populated
    return [
      { hospital_code: 'MAYO-01', score: 0.94, compliance: 0.98, consistency: 0.92, status: 'TRUSTED' },
      { hospital_code: 'JHU-02', score: 0.89, compliance: 0.92, consistency: 0.88, status: 'TRUSTED' },
      { hospital_code: 'MASS-03', score: 0.84, compliance: 0.85, consistency: 0.82, status: 'TRUSTED' },
      { hospital_code: 'STAN-04', score: 0.62, compliance: 0.70, consistency: 0.58, status: 'REVIEW' },
      { hospital_code: 'CLEV-05', score: 0.31, compliance: 0.45, consistency: 0.32, status: 'QUARANTINED' },
    ]
  }, [trustRecords])

  return (
    <div style={{ width: '100%', height, position: 'relative', background: 'radial-gradient(ellipse at center, rgba(10, 30, 36, 0.95) 0%, rgba(4, 9, 14, 0.98) 85%)', borderRadius: '8px', overflow: 'hidden' }}>
      <Canvas camera={{ position: [5, 4, 6], fov: 42 }}>
        <ambientLight intensity={0.6} />
        <pointLight position={[6, 8, 6]} intensity={1.2} />
        <OrbitControls enableZoom={true} zoomSpeed={1.0} minDistance={2} maxDistance={35} enablePan={true} panSpeed={1.0} enableRotate={true} rotateSpeed={0.8} enableDamping={true} dampingFactor={0.05} autoRotate autoRotateSpeed={0.6} />

        {/* 3D Threshold Decision Planes */}
        <ThresholdPlane y={0.6} color="#10b981" label="TRUSTED (>= 0.70)" />
        <ThresholdPlane y={0.0} color="#f59e0b" label="REVIEW (0.40 - 0.70)" />
        <ThresholdPlane y={-0.6} color="#ef4444" label="QUARANTINE (< 0.40)" />

        {/* Hospital Reputation Points */}
        {records.map((rec, i) => (
          <TrustNode key={rec.id || i} record={rec} index={i} total={records.length} />
        ))}
      </Canvas>
    </div>
  )
}
