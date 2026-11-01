import React, { useRef, useMemo, useState } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Html } from '@react-three/drei'
import * as THREE from 'three'

function OrbitRing({ radius, color = '#155c65', opacity = 0.35 }) {
  return (
    <mesh rotation={[Math.PI / 2, 0, 0]}>
      <ringGeometry args={[radius - 0.02, radius + 0.02, 64]} />
      <meshBasicMaterial color={color} side={THREE.DoubleSide} transparent opacity={opacity} />
    </mesh>
  )
}

function OrbitingSatellite({ hospital, orbitRadius, speed, initialAngle, onSelect, isSelected }) {
  const satRef = useRef()
  const [hovered, setHovered] = useState(false)

  const isQuarantined = String(hospital.status || '').toUpperCase() === 'QUARANTINED'
  const isSuspended = String(hospital.status || '').toUpperCase() === 'SUSPENDED'

  const color = useMemo(() => {
    if (isQuarantined) return '#ef4444'
    if (isSuspended) return '#eab308'
    if (hospital.security_status === 'TRUSTED') return '#10b981'
    return '#00e5ff'
  }, [isQuarantined, isSuspended, hospital.security_status])

  useFrame((state) => {
    const t = state.clock.elapsedTime * speed + initialAngle
    if (satRef.current) {
      satRef.current.position.x = Math.cos(t) * orbitRadius
      satRef.current.position.z = Math.sin(t) * orbitRadius
      satRef.current.position.y = Math.sin(t * 2) * 0.25
    }
  })

  return (
    <group ref={satRef}>
      <mesh
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
        onClick={() => onSelect && onSelect(hospital)}
        scale={isSelected ? 1.4 : hovered ? 1.25 : 1.0}
      >
        <octahedronGeometry args={[0.22, 0]} />
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={isSelected ? 1.2 : 0.6}
          roughness={0.2}
        />
      </mesh>

      {(hovered || isSelected) && (
        <Html distanceFactor={10} position={[0, 0.45, 0]} center>
          <div style={{
            background: 'rgba(5, 12, 18, 0.92)',
            border: `1px solid ${color}`,
            borderRadius: '4px',
            padding: '3px 6px',
            color: '#fff',
            fontSize: '9px',
            whiteSpace: 'nowrap',
            pointerEvents: 'none',
          }}>
            <strong style={{ color }}>{hospital.code || 'NODE'}</strong>
            <div style={{ fontSize: '8px', color: '#94a3b8' }}>{hospital.name}</div>
          </div>
        </Html>
      )}
    </group>
  )
}

export default function FederationOrbit3D({
  hospitals = [],
  selectedHospital = null,
  onSelectHospital = null,
  height = '280px',
}) {
  const orbitalTiers = useMemo(() => {
    const list = Array.isArray(hospitals) ? hospitals : []
    const inner = []
    const middle = []
    const outer = []

    list.forEach((h, idx) => {
      const st = String(h.status || '').toUpperCase()
      const sec = String(h.security_status || '').toUpperCase()
      if (st === 'ACTIVE' && sec === 'TRUSTED') {
        inner.push({ ...h, radius: 2.2, speed: 0.35, angle: (idx / Math.max(list.length, 1)) * Math.PI * 2 })
      } else if (st === 'ACTIVE') {
        middle.push({ ...h, radius: 3.4, speed: 0.22, angle: (idx / Math.max(list.length, 1)) * Math.PI * 2 })
      } else {
        outer.push({ ...h, radius: 4.5, speed: 0.12, angle: (idx / Math.max(list.length, 1)) * Math.PI * 2 })
      }
    })

    return { inner, middle, outer }
  }, [hospitals])

  return (
    <div style={{ width: '100%', height, position: 'relative', background: 'radial-gradient(ellipse at center, rgba(8, 28, 36, 0.9) 0%, rgba(4, 9, 13, 0.98) 80%)', borderRadius: '8px', overflow: 'hidden' }}>
      <Canvas camera={{ position: [0, 4.5, 7], fov: 42 }}>
        <ambientLight intensity={0.6} />
        <pointLight position={[0, 5, 0]} intensity={1.5} color="#00e5ff" />
        <OrbitControls enableZoom={false} enablePan={false} maxPolarAngle={Math.PI / 2.1} minPolarAngle={Math.PI / 4} autoRotate autoRotateSpeed={0.5} />

        {/* Central FedSentinel Hub */}
        <mesh position={[0, 0, 0]}>
          <sphereGeometry args={[0.6, 24, 24]} />
          <meshStandardMaterial color="#0284c7" emissive="#38bdf8" emissiveIntensity={0.8} />
        </mesh>

        {/* Concentric Orbital Rings */}
        <OrbitRing radius={2.2} color="#10b981" opacity={0.4} />
        <OrbitRing radius={3.4} color="#00e5ff" opacity={0.3} />
        <OrbitRing radius={4.5} color="#f59e0b" opacity={0.25} />

        {/* Satellites */}
        {orbitalTiers.inner.map((h) => (
          <OrbitingSatellite
            key={h.id}
            hospital={h}
            orbitRadius={h.radius}
            speed={h.speed}
            initialAngle={h.angle}
            isSelected={selectedHospital?.id === h.id}
            onSelect={onSelectHospital}
          />
        ))}

        {orbitalTiers.middle.map((h) => (
          <OrbitingSatellite
            key={h.id}
            hospital={h}
            orbitRadius={h.radius}
            speed={h.speed}
            initialAngle={h.angle}
            isSelected={selectedHospital?.id === h.id}
            onSelect={onSelectHospital}
          />
        ))}

        {orbitalTiers.outer.map((h) => (
          <OrbitingSatellite
            key={h.id}
            hospital={h}
            orbitRadius={h.radius}
            speed={h.speed}
            initialAngle={h.angle}
            isSelected={selectedHospital?.id === h.id}
            onSelect={onSelectHospital}
          />
        ))}
      </Canvas>
    </div>
  )
}
