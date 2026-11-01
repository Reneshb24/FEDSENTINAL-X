import React, { useState, useRef, useMemo, Suspense } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Html } from '@react-three/drei'
import * as THREE from 'three'
import { Shield, Activity, AlertTriangle, Layers, Info } from 'lucide-react'

function CentralHub() {
  const meshRef = useRef()
  const ringRef = useRef()

  useFrame((state, delta) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += delta * 0.4
      meshRef.current.rotation.x += delta * 0.2
    }
    if (ringRef.current) {
      ringRef.current.rotation.z -= delta * 0.2
    }
  })

  return (
    <group position={[0, 0, 0]}>
      <mesh ref={meshRef}>
        <octahedronGeometry args={[1.2, 0]} />
        <meshStandardMaterial
          color="#38bdf8"
          emissive="#0284c7"
          emissiveIntensity={0.8}
          wireframe
        />
      </mesh>
      <mesh>
        <sphereGeometry args={[0.7, 16, 16]} />
        <meshStandardMaterial
          color="#0284c7"
          emissive="#38bdf8"
          emissiveIntensity={0.5}
          roughness={0.2}
        />
      </mesh>
      {/* Outer pulsing ring */}
      <mesh ref={ringRef} rotation={[Math.PI / 2, 0, 0]}>
        <ringGeometry args={[1.6, 1.75, 32]} />
        <meshBasicMaterial color="#38bdf8" side={THREE.DoubleSide} transparent opacity={0.6} />
      </mesh>
    </group>
  )
}

function HospitalNode({ hospital, position, isSelected, onSelect }) {
  const [hovered, setHovered] = useState(false)
  const meshRef = useRef()

  useFrame((state, delta) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += delta * 0.5
      if (hovered || isSelected) {
        meshRef.current.scale.setScalar(1.2 + Math.sin(state.clock.elapsedTime * 4) * 0.1)
      } else {
        meshRef.current.scale.setScalar(1.0)
      }
    }
  })

  const isQuarantined = hospital.security_status === 'QUARANTINED' || hospital.status === 'SUSPENDED'
  const isReview = hospital.security_status === 'REVIEW' || hospital.status === 'PENDING'
  const nodeColor = isQuarantined ? '#ef4444' : isReview ? '#f59e0b' : '#10b981'
  const emissiveColor = isQuarantined ? '#b91c1c' : isReview ? '#d97706' : '#059669'

  // Connection line points from center to node
  const linePoints = useMemo(() => {
    return [new THREE.Vector3(0, 0, 0), new THREE.Vector3(...position)]
  }, [position])

  const lineGeometry = useMemo(() => {
    return new THREE.BufferGeometry().setFromPoints(linePoints)
  }, [linePoints])

  return (
    <group position={position}>
      {/* Beam to central hub */}
      <primitive object={new THREE.Line(lineGeometry, new THREE.LineBasicMaterial({
        color: nodeColor,
        transparent: true,
        opacity: isSelected ? 0.9 : hovered ? 0.6 : 0.25,
        linewidth: isSelected ? 2 : 1
      }))} position={[-position[0], -position[1], -position[2]]} />

      <mesh
        ref={meshRef}
        onClick={(e) => {
          e.stopPropagation()
          onSelect?.(hospital)
        }}
        onPointerOver={(e) => {
          e.stopPropagation()
          setHovered(true)
        }}
        onPointerOut={() => setHovered(false)}
      >
        <dodecahedronGeometry args={[0.5, 0]} />
        <meshStandardMaterial
          color={nodeColor}
          emissive={emissiveColor}
          emissiveIntensity={hovered || isSelected ? 1.2 : 0.6}
          roughness={0.3}
        />
      </mesh>

      {/* Orbit Halo */}
      <mesh rotation={[Math.PI / 4, 0, 0]}>
        <ringGeometry args={[0.7, 0.8, 16]} />
        <meshBasicMaterial
          color={nodeColor}
          side={THREE.DoubleSide}
          transparent
          opacity={hovered || isSelected ? 0.8 : 0.3}
        />
      </mesh>

      {/* Hover Info Tooltip */}
      {(hovered || isSelected) && (
        <Html distanceFactor={12} position={[0, 1.1, 0]} center>
          <div style={{
            background: 'rgba(10, 17, 30, 0.95)',
            border: `1px solid ${nodeColor}`,
            padding: '8px 12px',
            borderRadius: '6px',
            color: '#f8fafc',
            fontFamily: 'Inter, system-ui, sans-serif',
            fontSize: '11px',
            lineHeight: 1.4,
            whiteSpace: 'nowrap',
            boxShadow: '0 8px 24px rgba(0,0,0,0.6)',
            pointerEvents: 'none',
            zIndex: 1000
          }}>
            <div style={{ fontWeight: 700, fontSize: '12px', color: nodeColor }}>
              {hospital.name || hospital.code}
            </div>
            <div style={{ color: '#94a3b8', fontSize: '10px' }}>
              Code: {hospital.code} | Status: {hospital.status}
            </div>
            <div style={{ display: 'flex', gap: '8px', marginTop: '4px', fontSize: '10px' }}>
              <span>Security: <strong style={{ color: nodeColor }}>{hospital.security_status || 'TRUSTED'}</strong></span>
              {hospital.trust_score !== undefined && (
                <span>Trust: <strong>{(hospital.trust_score * 100).toFixed(0)}%</strong></span>
              )}
            </div>
          </div>
        </Html>
      )}
    </group>
  )
}

function OrbitalGrid() {
  return (
    <group rotation={[Math.PI / 2, 0, 0]}>
      {[3.5, 6.0, 8.5].map((radius, i) => (
        <mesh key={i}>
          <ringGeometry args={[radius - 0.02, radius + 0.02, 64]} />
          <meshBasicMaterial color="#334155" transparent opacity={0.3} side={THREE.DoubleSide} />
        </mesh>
      ))}
    </group>
  )
}

function WebGLFallback({ hospitals, selectedHospital, onSelect }) {
  return (
    <div style={{
      width: '100%',
      height: '100%',
      minHeight: '340px',
      background: 'radial-gradient(circle at center, #0f172a 0%, #020617 100%)',
      borderRadius: '8px',
      position: 'relative',
      overflow: 'hidden',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '20px'
    }}>
      <svg width="100%" height="100%" viewBox="-150 -150 300 300" style={{ maxWidth: '400px', maxHeight: '400px' }}>
        <circle cx="0" cy="0" r="40" fill="none" stroke="#334155" strokeDasharray="3 3" />
        <circle cx="0" cy="0" r="85" fill="none" stroke="#334155" strokeDasharray="4 4" />
        <circle cx="0" cy="0" r="130" fill="none" stroke="#334155" strokeDasharray="5 5" />
        
        {/* Central aggregator */}
        <circle cx="0" cy="0" r="14" fill="#0284c7" stroke="#38bdf8" strokeWidth="2" />
        <text x="0" y="4" textAnchor="middle" fill="#ffffff" fontSize="9" fontWeight="bold">FED</text>

        {/* Nodes */}
        {hospitals.map((h, i) => {
          const angle = (i / Math.max(hospitals.length, 1)) * 2 * Math.PI
          const radius = 60 + (i % 3) * 35
          const cx = Math.cos(angle) * radius
          const cy = Math.sin(angle) * radius
          const isSelected = selectedHospital?.id === h.id
          const color = h.security_status === 'QUARANTINED' ? '#ef4444' : h.security_status === 'REVIEW' ? '#f59e0b' : '#10b981'

          return (
            <g key={h.id || i} onClick={() => onSelect?.(h)} style={{ cursor: 'pointer' }}>
              <line x1="0" y1="0" x2={cx} y2={cy} stroke={color} strokeWidth={isSelected ? "2" : "1"} opacity={isSelected ? 0.9 : 0.4} />
              <circle cx={cx} cy={cy} r={isSelected ? 10 : 7} fill={color} stroke="#0f172a" strokeWidth="2" />
              <text x={cx} y={cy + 18} textAnchor="middle" fill="#cbd5e1" fontSize="8" fontWeight="600">{h.code}</text>
            </g>
          )
        })}
      </svg>
      <div style={{ position: 'absolute', bottom: 10, right: 12, fontSize: '11px', color: '#64748b' }}>
        2D Vector Topology Active
      </div>
    </div>
  )
}

export default function HospitalNetwork3D({
  hospitals = [],
  selectedHospital = null,
  onSelectHospital = null,
  height = '360px'
}) {
  const [hasWebGL, setHasWebGL] = useState(true)

  // Verify WebGL availability
  React.useEffect(() => {
    try {
      const canvas = document.createElement('canvas')
      const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl')
      if (!gl) setHasWebGL(false)
    } catch {
      setHasWebGL(false)
    }
  }, [])

  // Position hospitals symmetrically on orbital shells
  const positionedHospitals = useMemo(() => {
    if (!hospitals || hospitals.length === 0) return []
    return hospitals.map((h, i) => {
      const total = hospitals.length
      const angle = (i / total) * Math.PI * 2
      const radius = 3.8 + ((i % 2) * 2.2)
      const x = Math.cos(angle) * radius
      const z = Math.sin(angle) * radius
      const y = Math.sin(angle * 2) * 0.8
      return { hospital: h, position: [x, y, z] }
    })
  }, [hospitals])

  if (!hasWebGL) {
    return <WebGLFallback hospitals={hospitals} selectedHospital={selectedHospital} onSelect={onSelectHospital} />
  }

  return (
    <div style={{ width: '100%', height, background: 'radial-gradient(circle at center, #0a1120 0%, #020617 100%)', borderRadius: '8px', position: 'relative', overflow: 'hidden' }}>
      <div style={{ position: 'absolute', top: 12, left: 16, zIndex: 10, pointerEvents: 'none' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#38bdf8', fontSize: '12px', fontWeight: 600 }}>
          <Activity size={15} />
          <span>3D FEDERATION TOPOLOGY RADAR</span>
        </div>
        <div style={{ color: '#64748b', fontSize: '10px' }}>
          Interactive orbital mesh • Orbit, zoom & click to inspect enclave node
        </div>
      </div>

      <Canvas
        camera={{ position: [0, 6, 10], fov: 45 }}
        onCreated={({ gl }) => {
          gl.setClearColor(new THREE.Color('#030712'), 1)
        }}
      >
        <ambientLight intensity={0.7} />
        <pointLight position={[10, 10, 10]} intensity={1.2} />
        <pointLight position={[-10, -5, -10]} intensity={0.5} color="#38bdf8" />

        <Suspense fallback={null}>
          <CentralHub />
          <OrbitalGrid />

          {positionedHospitals.map(({ hospital, position }) => (
            <HospitalNode
              key={hospital.id || hospital.code}
              hospital={hospital}
              position={position}
              isSelected={selectedHospital?.id === hospital.id}
              onSelect={onSelectHospital}
            />
          ))}
        </Suspense>

        <OrbitControls
          enablePan={false}
          maxDistance={18}
          minDistance={4}
          autoRotate
          autoRotateSpeed={0.5}
        />
      </Canvas>
    </div>
  )
}
