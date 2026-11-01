import React, { useRef, useMemo, useState } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Html } from '@react-three/drei'
import * as THREE from 'three'

function BifurcatedPaths({ degradation = 0.08 }) {
  const [hoveredA, setHoveredA] = useState(false)
  const [hoveredB, setHoveredB] = useState(false)

  const pointsA = useMemo(() => {
    const pts = []
    for (let i = 0; i <= 24; i++) {
      const t = i / 24
      pts.push(new THREE.Vector3(-2.6 + t * 5.2, 0.2 + Math.sin(t * 3.5) * 0.15, t * 0.3))
    }
    return pts
  }, [])

  const pointsB = useMemo(() => {
    const pts = []
    for (let i = 0; i <= 24; i++) {
      const t = i / 24
      const y = t < 0.4 ? 0.2 + Math.sin(t * 3.5) * 0.15 : 0.2 - (t - 0.4) * 2.2
      const z = t < 0.4 ? t * 0.3 : t * 0.3 + (t - 0.4) * 1.8
      pts.push(new THREE.Vector3(-2.6 + t * 5.2, y, z))
    }
    return pts
  }, [])

  const geomA = useMemo(() => new THREE.BufferGeometry().setFromPoints(pointsA), [pointsA])
  const geomB = useMemo(() => new THREE.BufferGeometry().setFromPoints(pointsB), [pointsB])

  return (
    <group>
      {/* Branch A: Baseline Without Update */}
      <line>
        <bufferGeometry attach="geometry" {...geomA} />
        <lineBasicMaterial attach="material" color="#10b981" linewidth={2} />
      </line>

      {/* Branch B: Candidate Trajectory */}
      <line>
        <bufferGeometry attach="geometry" {...geomB} />
        <lineBasicMaterial attach="material" color="#ef4444" linewidth={2} />
      </line>

      {/* Fork Point */}
      <mesh position={[-0.5, 0.2, 0.15]}>
        <sphereGeometry args={[0.15, 12, 12]} />
        <meshStandardMaterial color="#00e5ff" emissive="#0284c7" emissiveIntensity={0.8} />
      </mesh>

      {/* Interactive Tooltip on Baseline Branch */}
      <group
        position={[2.6, 0.4, 0.4]}
        onPointerOver={() => setHoveredA(true)}
        onPointerOut={() => setHoveredA(false)}
      >
        <mesh>
          <sphereGeometry args={[0.14, 12, 12]} />
          <meshStandardMaterial color="#10b981" emissive="#059669" emissiveIntensity={hoveredA ? 1.4 : 0.8} />
        </mesh>
        <Html position={[0, 0.35, 0]} center>
          <div style={{
            background: 'rgba(5, 15, 25, 0.95)',
            border: '1px solid #10b981',
            borderRadius: '4px',
            padding: '3px 8px',
            color: '#fff',
            fontSize: '8px',
            whiteSpace: 'nowrap',
          }}>
            <strong style={{ color: '#10b981' }}>BASELINE (\theta_-k)</strong>
            <div>Validation Acc: 89.4% (Stable)</div>
          </div>
        </Html>
      </group>

      {/* Interactive Tooltip on Candidate Degradation Branch */}
      <group
        position={[2.6, -1.1, 1.4]}
        onPointerOver={() => setHoveredB(true)}
        onPointerOut={() => setHoveredB(false)}
      >
        <mesh>
          <sphereGeometry args={[0.16, 12, 12]} />
          <meshStandardMaterial color="#ef4444" emissive="#b91c1c" emissiveIntensity={hoveredB ? 1.4 : 0.8} />
        </mesh>
        <Html position={[0, -0.35, 0]} center>
          <div style={{
            background: 'rgba(5, 15, 25, 0.95)',
            border: '1px solid #ef4444',
            borderRadius: '4px',
            padding: '3px 8px',
            color: '#fff',
            fontSize: '8px',
            whiteSpace: 'nowrap',
          }}>
            <strong style={{ color: '#ef4444' }}>CANDIDATE (\theta_+k)</strong>
            <div>LOO Degradation: -{(degradation * 100).toFixed(1)}% Acc</div>
          </div>
        </Html>
      </group>
    </group>
  )
}

export default function L4Counterfactual3D({ updates = [], height = '250px' }) {
  return (
    <div style={{
      width: '100%',
      height,
      position: 'relative',
      background: 'radial-gradient(ellipse at center, rgba(14, 28, 42, 0.95) 0%, rgba(4, 8, 12, 0.98) 85%)',
      borderRadius: '8px',
      overflow: 'hidden',
      border: '1px solid #143542'
    }}>
      <Canvas camera={{ position: [0, 2.5, 6], fov: 42 }}>
        <ambientLight intensity={0.7} />
        <pointLight position={[5, 8, 5]} intensity={1.2} />
        <OrbitControls enableZoom={false} enablePan={false} autoRotate autoRotateSpeed={0.6} />

        <BifurcatedPaths degradation={0.084} />

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
            L4 LEAVE-ONE-OUT (LOO) COUNTERFACTUAL SIMULATION & CAUSAL ATTRIBUTION
          </div>
        </Html>
      </Canvas>
    </div>
  )
}
