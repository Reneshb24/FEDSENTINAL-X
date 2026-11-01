import React, { useRef, useMemo, useState } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Html } from '@react-three/drei'
import * as THREE from 'three'

function CosineVector({ vec }) {
  const [hovered, setHovered] = useState(false)
  const meshRef = useRef()

  useFrame((state, delta) => {
    if (meshRef.current && hovered) {
      meshRef.current.scale.setScalar(1.4)
    } else if (meshRef.current) {
      meshRef.current.scale.setScalar(1.0)
    }
  })

  const color = vec.isAnomaly ? '#ef4444' : '#10b981'

  return (
    <group>
      {/* Ray from centroid */}
      <line>
        <bufferGeometry attach="geometry" {...new THREE.BufferGeometry().setFromPoints([
          new THREE.Vector3(0, 0, 0),
          new THREE.Vector3(...vec.pos)
        ])} />
        <lineBasicMaterial
          attach="material"
          color={color}
          transparent
          opacity={vec.isAnomaly ? 0.85 : 0.45}
        />
      </line>

      {/* Endpoint marker */}
      <mesh
        ref={meshRef}
        position={vec.pos}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
      >
        <sphereGeometry args={[vec.isAnomaly ? 0.18 : 0.12, 12, 12]} />
        <meshStandardMaterial
          color={color}
          emissive={vec.isAnomaly ? '#b91c1c' : '#059669'}
          emissiveIntensity={hovered ? 1.4 : 0.8}
        />
      </mesh>

      {hovered && (
        <Html position={[vec.pos[0], vec.pos[1] + 0.35, vec.pos[2]]} center>
          <div style={{
            background: 'rgba(5, 12, 20, 0.95)',
            border: `1px solid ${color}`,
            borderRadius: '4px',
            padding: '4px 8px',
            color: '#fff',
            fontSize: '9px',
            whiteSpace: 'nowrap',
            boxShadow: `0 0 10px ${color}60`,
            pointerEvents: 'none',
          }}>
            <strong style={{ color }}>{vec.code}</strong>
            <div>Cosine Sim: {vec.sim.toFixed(3)}</div>
            <div>Robust Z-Score: {vec.zScore.toFixed(2)}σ</div>
            <div style={{ color: vec.isAnomaly ? '#ef4444' : '#10b981', fontSize: '8px' }}>
              {vec.isAnomaly ? 'OUTLIER FLAGGED (z > 3.0σ)' : 'CONSENSUS CLUSTER'}
            </div>
          </div>
        </Html>
      )}
    </group>
  )
}

export default function L2CosineCluster3D({ updates = [], height = '250px' }) {
  const vectors = useMemo(() => {
    const list = Array.isArray(updates) && updates.length > 0 ? updates : [
      { hospital_code: 'MAYO-01', zScore: 0.82, sim: 0.94 },
      { hospital_code: 'JHU-02', zScore: 1.15, sim: 0.91 },
      { hospital_code: 'MASS-03', zScore: 0.64, sim: 0.96 },
      { hospital_code: 'STAN-04', zScore: 1.45, sim: 0.88 },
      { hospital_code: 'CLEV-05', zScore: 4.85, sim: 0.38 }, // Anomaly
      { hospital_code: 'UCLA-06', zScore: 0.95, sim: 0.93 },
      { hospital_code: 'NYU-07', zScore: 1.05, sim: 0.92 },
      { hospital_code: 'DUKE-08', zScore: 0.78, sim: 0.95 },
    ]

    return list.map((u, i) => {
      const zScore = Number(u.zScore ?? (u.evidence?.l2?.z_score ?? 1.0))
      const isAnomaly = zScore >= 3.0
      const sim = Number(u.sim ?? (u.evidence?.l2?.cosine_similarity ?? (isAnomaly ? 0.42 : 0.92)))

      // Map into 3D angular coordinates
      if (!isAnomaly) {
        // Tight cluster around [1.0, 1.0, 1.0]
        const spread = 0.4
        const base = new THREE.Vector3(
          1.0 + (Math.sin(i * 1.7) * spread),
          1.0 + (Math.cos(i * 2.1) * spread),
          1.0 + (Math.sin(i * 0.9) * spread)
        ).normalize().multiplyScalar(2.3)
        return { pos: [base.x, base.y, base.z], isAnomaly: false, code: u.hospital_code || `NODE-${i + 1}`, zScore, sim, id: u.id || i }
      } else {
        // Divergent angular trajectory
        const div = new THREE.Vector3(-1.4, 0.4, 0.9).normalize().multiplyScalar(2.6)
        return { pos: [div.x, div.y, div.z], isAnomaly: true, code: u.hospital_code || `NODE-${i + 1}`, zScore, sim, id: u.id || i }
      }
    })
  }, [updates])

  return (
    <div style={{
      width: '100%',
      height,
      position: 'relative',
      background: 'radial-gradient(ellipse at center, rgba(14, 26, 36, 0.95) 0%, rgba(4, 8, 12, 0.98) 85%)',
      borderRadius: '8px',
      overflow: 'hidden',
      border: '1px solid #143540'
    }}>
      <Canvas camera={{ position: [3.5, 3.5, 4.5], fov: 42 }}>
        <ambientLight intensity={0.7} />
        <pointLight position={[5, 8, 5]} intensity={1.2} />
        <OrbitControls enableZoom={false} enablePan={false} autoRotate autoRotateSpeed={0.8} />

        {/* Central Consensus Centroid */}
        <mesh position={[0, 0, 0]}>
          <sphereGeometry args={[0.2, 16, 16]} />
          <meshStandardMaterial color="#00e5ff" emissive="#0284c7" emissiveIntensity={0.8} />
        </mesh>

        {vectors.map((vec) => (
          <CosineVector key={vec.id} vec={vec} />
        ))}

        <Html position={[0, -1.8, 0]} center>
          <div style={{
            background: 'rgba(5, 18, 26, 0.9)',
            border: '1px solid #10b981',
            borderRadius: '4px',
            padding: '3px 10px',
            color: '#10b981',
            fontSize: '9px',
            fontWeight: 700,
            whiteSpace: 'nowrap',
          }}>
            L2 PAIRWISE COSINE SIMILARITY & ROBUST ANOMALY DETECTION (3.0σ CUTOFF)
          </div>
        </Html>
      </Canvas>
    </div>
  )
}
