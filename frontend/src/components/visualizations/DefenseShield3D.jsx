import React, { useState, useRef, useMemo } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Html } from '@react-three/drei'
import * as THREE from 'three'
import { Shield, ShieldAlert, ShieldCheck, Activity } from 'lucide-react'

function DefenseCore({ posture = 'PROTECTED' }) {
  const coreRef = useRef()
  const ring1Ref = useRef()
  const ring2Ref = useRef()
  const ring3Ref = useRef()

  const color = useMemo(() => {
    if (posture === 'ALERT') return '#ef4444'
    if (posture === 'GUARDED') return '#f59e0b'
    return '#10b981'
  }, [posture])

  const emissiveColor = useMemo(() => {
    if (posture === 'ALERT') return '#b91c1c'
    if (posture === 'GUARDED') return '#d97706'
    return '#059669'
  }, [posture])

  useFrame((state, delta) => {
    if (coreRef.current) {
      coreRef.current.rotation.y += delta * 0.4
      coreRef.current.rotation.x += delta * 0.2
    }
    if (ring1Ref.current) {
      ring1Ref.current.rotation.z += delta * 0.3
      ring1Ref.current.rotation.x += delta * 0.15
    }
    if (ring2Ref.current) {
      ring2Ref.current.rotation.y -= delta * 0.25
      ring2Ref.current.rotation.z -= delta * 0.2
    }
    if (ring3Ref.current) {
      ring3Ref.current.rotation.x -= delta * 0.2
      ring3Ref.current.rotation.y += delta * 0.35
    }
  })

  return (
    <group position={[0, 0, 0]}>
      {/* Central Posture Icosahedron */}
      <mesh ref={coreRef}>
        <icosahedronGeometry args={[1.3, 1]} />
        <meshStandardMaterial
          color={color}
          emissive={emissiveColor}
          emissiveIntensity={0.9}
          roughness={0.2}
          wireframe={false}
        />
      </mesh>

      {/* Wireframe outer aura */}
      <mesh>
        <icosahedronGeometry args={[1.5, 1]} />
        <meshBasicMaterial
          color={color}
          wireframe
          transparent
          opacity={0.4}
        />
      </mesh>

      {/* Concentric Rotating Shield Rings */}
      <mesh ref={ring1Ref}>
        <torusGeometry args={[2.2, 0.04, 16, 64]} />
        <meshBasicMaterial color={color} transparent opacity={0.7} />
      </mesh>

      <mesh ref={ring2Ref} rotation={[Math.PI / 3, 0, 0]}>
        <torusGeometry args={[2.7, 0.03, 16, 64]} />
        <meshBasicMaterial color="#00e5ff" transparent opacity={0.5} />
      </mesh>

      <mesh ref={ring3Ref} rotation={[-Math.PI / 4, 0, Math.PI / 6]}>
        <torusGeometry args={[3.2, 0.025, 16, 64]} />
        <meshBasicMaterial color="#38bdf8" transparent opacity={0.4} />
      </mesh>

      {/* Floating Status Label */}
      <Html position={[0, -2.2, 0]} center>
        <div style={{
          background: 'rgba(5, 15, 25, 0.85)',
          border: `1px solid ${color}`,
          borderRadius: '4px',
          padding: '2px 8px',
          color: color,
          fontSize: '10px',
          fontWeight: 700,
          letterSpacing: '0.08em',
          whiteSpace: 'nowrap',
          boxShadow: `0 0 12px ${color}40`,
        }}>
          DEFENSE STATUS: {posture}
        </div>
      </Html>
    </group>
  )
}

function ThreatSensors({ count = 8, posture }) {
  const points = useMemo(() => {
    const arr = []
    for (let i = 0; i < count; i++) {
      const angle = (i / count) * Math.PI * 2
      const radius = 4.2 + (i % 2) * 0.8
      const y = Math.sin(i * 1.5) * 1.2
      const isThreat = posture === 'ALERT' && i % 3 === 0
      arr.push({
        position: [Math.cos(angle) * radius, y, Math.sin(angle) * radius],
        isThreat,
        id: i,
      })
    }
    return arr
  }, [count, posture])

  return (
    <group>
      {points.map((pt) => (
        <group key={pt.id} position={pt.position}>
          <mesh>
            <sphereGeometry args={[pt.isThreat ? 0.22 : 0.14, 12, 12]} />
            <meshStandardMaterial
              color={pt.isThreat ? '#ef4444' : '#00e5ff'}
              emissive={pt.isThreat ? '#b91c1c' : '#0284c7'}
              emissiveIntensity={0.8}
            />
          </mesh>
        </group>
      ))}
    </group>
  )
}

export default function DefenseShield3D({ posture = 'PROTECTED', height = '240px' }) {
  return (
    <div style={{ width: '100%', height, position: 'relative', background: 'radial-gradient(circle at center, rgba(14, 113, 122, 0.15) 0%, rgba(5, 12, 17, 0.95) 75%)', borderRadius: '8px', overflow: 'hidden' }}>
      <Canvas camera={{ position: [0, 2, 7], fov: 45 }}>
        <ambientLight intensity={0.6} />
        <pointLight position={[10, 10, 10]} intensity={1.2} />
        <pointLight position={[-10, -10, -10]} intensity={0.4} color="#00e5ff" />
        <OrbitControls enableZoom={false} enablePan={false} maxPolarAngle={Math.PI / 1.8} minPolarAngle={Math.PI / 2.5} autoRotate autoRotateSpeed={0.8} />
        <DefenseCore posture={posture} />
        <ThreatSensors posture={posture} />
      </Canvas>
    </div>
  )
}
