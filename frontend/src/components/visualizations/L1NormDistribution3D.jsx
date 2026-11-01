import React, { useRef, useMemo, useState } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Html } from '@react-three/drei'
import * as THREE from 'three'

function HistogramBar({ bar, index, total }) {
  const [hovered, setHovered] = useState(false)
  const meshRef = useRef()

  useFrame((state, delta) => {
    if (meshRef.current && hovered) {
      meshRef.current.scale.set(1.2, 1.0, 1.2)
    } else if (meshRef.current) {
      meshRef.current.scale.set(1.0, 1.0, 1.0)
    }
  })

  const color = bar.isClipped ? '#ef4444' : '#10b981'

  return (
    <group position={[bar.x, bar.height / 2, bar.z]}>
      <mesh
        ref={meshRef}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
      >
        <cylinderGeometry args={[0.16, 0.16, bar.height, 16]} />
        <meshStandardMaterial
          color={color}
          emissive={bar.isClipped ? '#b91c1c' : '#059669'}
          emissiveIntensity={hovered ? 1.2 : 0.7}
        />
      </mesh>

      {hovered && (
        <Html position={[0, bar.height / 2 + 0.35, 0]} center>
          <div style={{
            background: 'rgba(5, 15, 25, 0.95)',
            border: `1px solid ${color}`,
            borderRadius: '4px',
            padding: '4px 8px',
            color: '#fff',
            fontSize: '9px',
            whiteSpace: 'nowrap',
            boxShadow: `0 0 10px ${color}60`,
            pointerEvents: 'none',
          }}>
            <strong style={{ color }}>{bar.code}</strong>
            <div>Norm ||ΔW||₂: {bar.norm.toFixed(3)}</div>
            <div style={{ color: bar.isClipped ? '#ef4444' : '#10b981', fontSize: '8px' }}>
              {bar.isClipped ? 'EXCEEDS CLIPPING BOUND (> 5.0)' : 'WITHIN STATISTICAL BOUNDS'}
            </div>
          </div>
        </Html>
      )}
    </group>
  )
}

function ClippingCeiling() {
  return (
    <group position={[0, 1.8, 0]}>
      <mesh rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[1.6, 2.6, 32]} />
        <meshBasicMaterial color="#ef4444" transparent opacity={0.25} side={THREE.DoubleSide} />
      </mesh>
      <Html position={[2.8, 0, 0]} center>
        <span style={{ fontSize: '8px', color: '#ef4444', fontWeight: 700, whiteSpace: 'nowrap' }}>
          CLIPPING CEILING (R_MAX = 5.0)
        </span>
      </Html>
    </group>
  )
}

export default function L1NormDistribution3D({ updates = [], height = '250px' }) {
  const bars = useMemo(() => {
    const list = Array.isArray(updates) && updates.length > 0 ? updates : [
      { hospital_code: 'MAYO-01', norm: 1.84 },
      { hospital_code: 'JHU-02', norm: 2.12 },
      { hospital_code: 'MASS-03', norm: 1.65 },
      { hospital_code: 'STAN-04', norm: 2.45 },
      { hospital_code: 'CLEV-05', norm: 6.82 }, // Outlier
      { hospital_code: 'UCLA-06', norm: 1.95 },
      { hospital_code: 'NYU-07', norm: 2.05 },
      { hospital_code: 'DUKE-08', norm: 1.78 },
    ]

    const count = list.length
    return list.map((u, i) => {
      const angle = (i / count) * Math.PI * 2
      const radius = 2.1
      const norm = Number(u.norm ?? (u.evidence ? 1.8 : 2.0))
      const isClipped = norm > 5.0
      // Scale visual height: norm 5.0 maps to height 1.8
      const visualHeight = Math.min(2.5, Math.max(0.4, (norm / 5.0) * 1.8))

      return {
        code: u.hospital_code || `NODE-${i + 1}`,
        norm,
        height: visualHeight,
        isClipped,
        x: Math.cos(angle) * radius,
        z: Math.sin(angle) * radius,
        id: u.id || i,
      }
    })
  }, [updates])

  return (
    <div style={{
      width: '100%',
      height,
      position: 'relative',
      background: 'radial-gradient(ellipse at center, rgba(10, 24, 30, 0.95) 0%, rgba(4, 8, 12, 0.98) 85%)',
      borderRadius: '8px',
      overflow: 'hidden',
      border: '1px solid #15373e'
    }}>
      <Canvas camera={{ position: [4, 3.5, 5], fov: 42 }}>
        <ambientLight intensity={0.7} />
        <pointLight position={[5, 8, 5]} intensity={1.2} />
        <OrbitControls enableZoom={false} enablePan={false} autoRotate autoRotateSpeed={0.8} maxPolarAngle={Math.PI / 2.2} minPolarAngle={Math.PI / 3.5} />

        {bars.map((bar, i) => (
          <HistogramBar key={bar.id} bar={bar} index={i} total={bars.length} />
        ))}

        <ClippingCeiling />
        <gridHelper args={[6, 12, '#17333a', '#0d2228']} position={[0, 0, 0]} />

        <Html position={[0, -0.6, 0]} center>
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
            L1 GRADIENT NORM INSPECTOR: {bars.length} CLIENTS EVALUATED
          </div>
        </Html>
      </Canvas>
    </div>
  )
}
