import React, { useRef, useMemo, useState } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Html } from '@react-three/drei'
import * as THREE from 'three'

function AggregationCore() {
  const coreRef = useRef()
  const ringRef = useRef()

  useFrame((state, delta) => {
    if (coreRef.current) {
      coreRef.current.rotation.y += delta * 0.8
      coreRef.current.rotation.x += delta * 0.4
    }
    if (ringRef.current) {
      ringRef.current.rotation.z -= delta * 0.5
    }
  })

  return (
    <group position={[0, 0, 0]}>
      {/* Central Global Model Synthesis Core */}
      <mesh ref={coreRef}>
        <dodecahedronGeometry args={[0.9, 0]} />
        <meshStandardMaterial
          color="#10b981"
          emissive="#059669"
          emissiveIntensity={1.0}
          roughness={0.1}
        />
      </mesh>

      {/* Inner Energy Field */}
      <mesh>
        <sphereGeometry args={[1.2, 16, 16]} />
        <meshBasicMaterial color="#34d399" wireframe transparent opacity={0.35} />
      </mesh>

      {/* Aggregation Fusion Ring */}
      <mesh ref={ringRef} rotation={[Math.PI / 2, 0, 0]}>
        <torusGeometry args={[1.6, 0.04, 16, 64]} />
        <meshBasicMaterial color="#00e5ff" transparent opacity={0.7} />
      </mesh>

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
          letterSpacing: '0.06em',
        }}>
          FEDAVG + SHIELD FUSION
        </div>
      </Html>
    </group>
  )
}

function IngressTensorStream({ isQuarantined = false, angle, delay = 0 }) {
  const meshRef = useRef()
  const radius = 3.6

  useFrame((state) => {
    const t = (state.clock.elapsedTime * 0.7 + delay) % 1
    if (meshRef.current) {
      if (!isQuarantined) {
        // Stream inward to core
        const r = radius * (1 - t)
        meshRef.current.position.x = Math.cos(angle) * r
        meshRef.current.position.z = Math.sin(angle) * r
        meshRef.current.position.y = Math.sin(t * Math.PI) * 0.4
        meshRef.current.scale.setScalar(0.12 + (1 - t) * 0.1)
      } else {
        // Deflect away into quarantine cell
        const r = radius * (0.5 + t * 0.6)
        const defAngle = angle + t * 1.2
        meshRef.current.position.x = Math.cos(defAngle) * r + 1.2 * t
        meshRef.current.position.z = Math.sin(defAngle) * r - 1.2 * t
        meshRef.current.position.y = Math.sin(t * 4) * 0.5 + 0.8 * t
        meshRef.current.scale.setScalar(0.18)
      }
    }
  })

  return (
    <mesh ref={meshRef}>
      <sphereGeometry args={[1, 12, 12]} />
      <meshStandardMaterial
        color={isQuarantined ? '#ef4444' : '#00e5ff'}
        emissive={isQuarantined ? '#b91c1c' : '#0284c7'}
        emissiveIntensity={1.0}
      />
    </mesh>
  )
}

function QuarantineCell() {
  return (
    <group position={[3.6, 1.2, -2.5]}>
      <mesh>
        <boxGeometry args={[1.5, 1.5, 1.5]} />
        <meshBasicMaterial color="#ef4444" wireframe transparent opacity={0.4} />
      </mesh>
      <Html position={[0, -1.1, 0]} center>
        <span style={{ fontSize: '8px', color: '#ef4444', fontWeight: 700, letterSpacing: '0.05em' }}>
          QUARANTINE VAULT
        </span>
      </Html>
    </group>
  )
}

export default function SafeAggregationVortex3D({ height = '260px' }) {
  const streams = useMemo(() => {
    return [
      { angle: 0, delay: 0, isQuarantined: false },
      { angle: Math.PI * 0.4, delay: 0.2, isQuarantined: false },
      { angle: Math.PI * 0.8, delay: 0.5, isQuarantined: false },
      { angle: Math.PI * 1.2, delay: 0.7, isQuarantined: false },
      { angle: Math.PI * 1.6, delay: 0.35, isQuarantined: true }, // Outlier deflected
    ]
  }, [])

  return (
    <div style={{ width: '100%', height, position: 'relative', background: 'radial-gradient(ellipse at center, rgba(8, 30, 24, 0.92) 0%, rgba(4, 9, 14, 0.98) 85%)', borderRadius: '8px', overflow: 'hidden' }}>
      <Canvas camera={{ position: [0, 4.5, 7], fov: 42 }}>
        <ambientLight intensity={0.6} />
        <pointLight position={[5, 8, 5]} intensity={1.5} color="#34d399" />
        <pointLight position={[-5, -4, -5]} intensity={0.8} color="#00e5ff" />
        <OrbitControls enableZoom={false} enablePan={false} autoRotate autoRotateSpeed={0.5} maxPolarAngle={Math.PI / 2.1} minPolarAngle={Math.PI / 4} />

        <AggregationCore />
        <QuarantineCell />

        {streams.map((s, idx) => (
          <IngressTensorStream
            key={idx}
            angle={s.angle}
            delay={s.delay}
            isQuarantined={s.isQuarantined}
          />
        ))}
      </Canvas>
    </div>
  )
}
