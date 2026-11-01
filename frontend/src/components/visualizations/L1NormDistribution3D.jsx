import React, { useRef, useMemo } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Html } from '@react-three/drei'
import * as THREE from 'three'

function HistogramBars() {
  const bars = useMemo(() => {
    const list = []
    const count = 12
    for (let i = 0; i < count; i++) {
      const angle = (i / count) * Math.PI * 2
      const radius = 2.0
      // Norm heights: mostly normal around 1.2, one outlier clipped
      const isOutlier = i === 4
      const height = isOutlier ? 2.4 : 0.8 + Math.sin(i * 1.5) * 0.4
      list.push({
        x: Math.cos(angle) * radius,
        z: Math.sin(angle) * radius,
        height,
        isOutlier,
        id: i,
      })
    }
    return list
  }, [])

  return (
    <group>
      {bars.map((b) => (
        <group key={b.id} position={[b.x, b.height / 2, b.z]}>
          <mesh>
            <cylinderGeometry args={[0.15, 0.15, b.height, 16]} />
            <meshStandardMaterial
              color={b.isOutlier ? '#ef4444' : '#10b981'}
              emissive={b.isOutlier ? '#b91c1c' : '#059669'}
              emissiveIntensity={0.8}
            />
          </mesh>
        </group>
      ))}
    </group>
  )
}

function ClippingCeiling() {
  return (
    <group position={[0, 1.8, 0]}>
      <mesh rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[1.5, 2.5, 32]} />
        <meshBasicMaterial color="#ef4444" transparent opacity={0.3} side={THREE.DoubleSide} />
      </mesh>
      <Html position={[2.7, 0, 0]} center>
        <span style={{ fontSize: '8px', color: '#ef4444', fontWeight: 700, whiteSpace: 'nowrap' }}>
          CLIPPING CEILING (R_MAX = 5.0)
        </span>
      </Html>
    </group>
  )
}

export default function L1NormDistribution3D({ height = '250px' }) {
  return (
    <div style={{ width: '100%', height, position: 'relative', background: 'radial-gradient(ellipse at center, rgba(10, 24, 30, 0.95) 0%, rgba(4, 8, 12, 0.98) 85%)', borderRadius: '8px', overflow: 'hidden' }}>
      <Canvas camera={{ position: [4, 3.5, 5], fov: 42 }}>
        <ambientLight intensity={0.7} />
        <pointLight position={[5, 8, 5]} intensity={1.2} />
        <OrbitControls enableZoom={false} enablePan={false} autoRotate autoRotateSpeed={0.8} maxPolarAngle={Math.PI / 2.2} minPolarAngle={Math.PI / 3.5} />

        <HistogramBars />
        <ClippingCeiling />

        {/* Base Grid */}
        <gridHelper args={[6, 12, '#17333a', '#0d2228']} position={[0, 0, 0]} />

        <Html position={[0, -0.6, 0]} center>
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
            L1 GRADIENT NORM INSPECTION & STATISTICAL BOUNDS
          </div>
        </Html>
      </Canvas>
    </div>
  )
}
