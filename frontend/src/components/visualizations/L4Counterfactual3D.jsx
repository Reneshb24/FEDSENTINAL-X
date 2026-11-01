import React, { useRef, useMemo } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Html } from '@react-three/drei'
import * as THREE from 'three'

function BifurcatedPaths() {
  const pointsA = useMemo(() => {
    const pts = []
    for (let i = 0; i <= 20; i++) {
      const t = i / 20
      pts.push(new THREE.Vector3(-2.5 + t * 5, 0.2 + Math.sin(t * 3) * 0.2, t * 0.4))
    }
    return pts
  }, [])

  const pointsB = useMemo(() => {
    const pts = []
    for (let i = 0; i <= 20; i++) {
      const t = i / 20
      // Diverges downward into loss penalty
      const y = t < 0.4 ? 0.2 + Math.sin(t * 3) * 0.2 : 0.2 - (t - 0.4) * 2.2
      const z = t < 0.4 ? t * 0.4 : t * 0.4 + (t - 0.4) * 2.0
      pts.push(new THREE.Vector3(-2.5 + t * 5, y, z))
    }
    return pts
  }, [])

  const geomA = useMemo(() => new THREE.BufferGeometry().setFromPoints(pointsA), [pointsA])
  const geomB = useMemo(() => new THREE.BufferGeometry().setFromPoints(pointsB), [pointsB])

  return (
    <group>
      {/* Branch A: Baseline Excluded (Stable) */}
      <line>
        <bufferGeometry attach="geometry" {...geomA} />
        <lineBasicMaterial attach="material" color="#10b981" linewidth={2} />
      </line>

      {/* Branch B: Candidate Included (Degrading) */}
      <line>
        <bufferGeometry attach="geometry" {...geomB} />
        <lineBasicMaterial attach="material" color="#ef4444" linewidth={2} />
      </line>

      {/* Bifurcation Fork Marker */}
      <mesh position={[-0.5, 0.2, 0.16]}>
        <sphereGeometry args={[0.15, 12, 12]} />
        <meshStandardMaterial color="#00e5ff" emissive="#0284c7" emissiveIntensity={0.8} />
      </mesh>

      <Html position={[2.6, 0.4, 0.4]} center>
        <span style={{ fontSize: '8px', color: '#10b981', fontWeight: 700, whiteSpace: 'nowrap' }}>
          BASELINE (\theta_{'{-\\mathrm{k}}'})
        </span>
      </Html>

      <Html position={[2.6, -1.2, 1.8]} center>
        <span style={{ fontSize: '8px', color: '#ef4444', fontWeight: 700, whiteSpace: 'nowrap' }}>
          CANDIDATE (\theta_{'{+\\mathrm{k}}'}) LOO DEGRADATION
        </span>
      </Html>
    </group>
  )
}

export default function L4Counterfactual3D({ height = '250px' }) {
  return (
    <div style={{ width: '100%', height, position: 'relative', background: 'radial-gradient(ellipse at center, rgba(14, 28, 42, 0.95) 0%, rgba(4, 8, 12, 0.98) 85%)', borderRadius: '8px', overflow: 'hidden' }}>
      <Canvas camera={{ position: [0, 2.5, 6], fov: 42 }}>
        <ambientLight intensity={0.7} />
        <pointLight position={[5, 8, 5]} intensity={1.2} />
        <OrbitControls enableZoom={false} enablePan={false} autoRotate autoRotateSpeed={0.6} />

        <BifurcatedPaths />

        <Html position={[0, -1.8, 0]} center>
          <div style={{
            background: 'rgba(5, 18, 26, 0.9)',
            border: '1px solid #10b981',
            borderRadius: '4px',
            padding: '2px 8px',
            color: '#10b981',
            fontSize: '9px',
            fontWeight: 700,
            whiteSpace: 'nowrap',
          }}>
            L4 LEAVE-ONE-OUT (LOO) COUNTERFACTUAL SIMULATION
          </div>
        </Html>
      </Canvas>
    </div>
  )
}
