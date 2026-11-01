import React, { useState, useRef, useMemo } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Html } from '@react-three/drei'
import * as THREE from 'three'

function DefenseCore({ posture = 'PROTECTED', roundNumber = 1, activeCount = 0, quarantinedCount = 0 }) {
  const coreRef = useRef()
  const ring1Ref = useRef()
  const ring2Ref = useRef()
  const ring3Ref = useRef()
  const [hovered, setHovered] = useState(false)

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
      {/* Central Posture Crystal */}
      <mesh
        ref={coreRef}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
        scale={hovered ? 1.25 : 1.0}
      >
        <icosahedronGeometry args={[1.2, 1]} />
        <meshStandardMaterial
          color={color}
          emissive={emissiveColor}
          emissiveIntensity={0.9}
          roughness={0.2}
        />
      </mesh>

      {/* Wireframe outer aura */}
      <mesh>
        <icosahedronGeometry args={[1.45, 1]} />
        <meshBasicMaterial
          color={color}
          wireframe
          transparent
          opacity={0.35}
        />
      </mesh>

      {/* Concentric Rotating Shield Rings */}
      <mesh ref={ring1Ref}>
        <torusGeometry args={[2.0, 0.035, 16, 64]} />
        <meshBasicMaterial color={color} transparent opacity={0.7} />
      </mesh>

      <mesh ref={ring2Ref} rotation={[Math.PI / 3, 0, 0]}>
        <torusGeometry args={[2.5, 0.03, 16, 64]} />
        <meshBasicMaterial color="#00e5ff" transparent opacity={0.5} />
      </mesh>

      <mesh ref={ring3Ref} rotation={[-Math.PI / 4, 0, Math.PI / 6]}>
        <torusGeometry args={[3.0, 0.025, 16, 64]} />
        <meshBasicMaterial color="#38bdf8" transparent opacity={0.4} />
      </mesh>

      {/* Core Hover Tooltip / Status Badge */}
      <Html position={[0, -2.1, 0]} center>
        <div style={{
          background: 'rgba(5, 15, 25, 0.92)',
          border: `1px solid ${color}`,
          borderRadius: '4px',
          padding: '4px 10px',
          color: color,
          fontSize: '10px',
          fontWeight: 700,
          letterSpacing: '0.08em',
          whiteSpace: 'nowrap',
          boxShadow: `0 0 14px ${color}40`,
          cursor: 'pointer',
        }}>
          <div>FEDERATION CONTROL PLANE: {posture}</div>
          {hovered && (
            <div style={{ fontSize: '9px', color: '#94a3b8', marginTop: 2, fontWeight: 500 }}>
              Round R-{roundNumber} • {activeCount} Enclaves Online • {quarantinedCount} Quarantined
            </div>
          )}
        </div>
      </Html>
    </group>
  )
}

function HospitalSensors({ hospitals = [], incidents = [] }) {
  const incidentHospitalIds = useMemo(() => {
    return new Set(incidents.map(inc => inc.hospital_id || inc.hospitalId).filter(Boolean))
  }, [incidents])

  const nodes = useMemo(() => {
    const list = Array.isArray(hospitals) && hospitals.length > 0
      ? hospitals.slice(0, 16)
      : [
          { id: '1', code: 'MAYO-01', name: 'Mayo Clinic Enclave', status: 'ACTIVE', security_status: 'TRUSTED' },
          { id: '2', code: 'JHU-02', name: 'Johns Hopkins Medicine', status: 'ACTIVE', security_status: 'TRUSTED' },
          { id: '3', code: 'MASS-03', name: 'Mass General Enclave', status: 'ACTIVE', security_status: 'TRUSTED' },
          { id: '4', code: 'STAN-04', name: 'Stanford Healthcare', status: 'ACTIVE', security_status: 'REVIEW' },
          { id: '5', code: 'CLEV-05', name: 'Cleveland Clinic', status: 'QUARANTINED', security_status: 'QUARANTINED' },
        ]

    return list.map((h, i) => {
      const angle = (i / Math.max(list.length, 1)) * Math.PI * 2
      const radius = 3.8 + (i % 2) * 0.5
      const y = Math.sin(i * 1.4) * 0.9
      const isIncident = incidentHospitalIds.has(h.id) || String(h.status || '').toUpperCase() === 'QUARANTINED'

      return {
        hospital: h,
        position: [Math.cos(angle) * radius, y, Math.sin(angle) * radius],
        isIncident,
        id: h.id || i,
      }
    })
  }, [hospitals, incidentHospitalIds])

  return (
    <group>
      {nodes.map((pt) => (
        <SensorNode key={pt.id} pt={pt} />
      ))}
    </group>
  )
}

function SensorNode({ pt }) {
  const [hovered, setHovered] = useState(false)
  const color = pt.isIncident ? '#ef4444' : pt.hospital.security_status === 'REVIEW' ? '#f59e0b' : '#00e5ff'

  return (
    <group position={pt.position}>
      {/* Laser line to core */}
      <line>
        <bufferGeometry attach="geometry" {...new THREE.BufferGeometry().setFromPoints([
          new THREE.Vector3(0, 0, 0),
          new THREE.Vector3(...pt.position).negate().multiplyScalar(0.7)
        ])} />
        <lineBasicMaterial attach="material" color={color} transparent opacity={0.2} />
      </line>

      <mesh
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
        scale={hovered ? 1.5 : 1.0}
      >
        <sphereGeometry args={[pt.isIncident ? 0.2 : 0.14, 12, 12]} />
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={hovered ? 1.4 : 0.8}
        />
      </mesh>

      {hovered && (
        <Html position={[0, 0.4, 0]} center>
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
            <strong style={{ color }}>{pt.hospital.code || 'NODE'}</strong>
            <div>{pt.hospital.name || 'Hospital Node'}</div>
            <div style={{ color: pt.isIncident ? '#ef4444' : '#10b981', fontSize: '8px' }}>
              {pt.isIncident ? 'ALERT: ANOMALY FLAGGED' : 'TELEMETRY: VERIFIED HEALTHY'}
            </div>
          </div>
        </Html>
      )}
    </group>
  )
}

export default function DefenseShield3D({ data = null, posture = 'PROTECTED', height = '250px' }) {
  const hospitals = Array.isArray(data?.hospitals) ? data.hospitals : []
  const incidents = Array.isArray(data?.incidents) ? data.incidents : []
  const latestRound = data?.rounds?.[0]
  const roundNumber = latestRound?.round_number || 1
  const activeCount = hospitals.filter(h => String(h.status || '').toUpperCase() === 'ACTIVE').length
  const quarantinedCount = hospitals.filter(h => String(h.status || '').toUpperCase() === 'QUARANTINED').length

  const computedPosture = useMemo(() => {
    if (posture) return posture
    if (incidents.length > 0 || quarantinedCount > 0) return 'ALERT'
    return 'PROTECTED'
  }, [posture, incidents, quarantinedCount])

  return (
    <div style={{
      width: '100%',
      height,
      position: 'relative',
      background: 'radial-gradient(circle at center, rgba(14, 113, 122, 0.18) 0%, rgba(5, 12, 17, 0.98) 75%)',
      borderRadius: '8px',
      overflow: 'hidden',
      border: '1px solid #15333a'
    }}>
      <Canvas camera={{ position: [0, 2, 6.8], fov: 44 }}>
        <ambientLight intensity={0.6} />
        <pointLight position={[10, 10, 10]} intensity={1.2} />
        <pointLight position={[-10, -10, -10]} intensity={0.5} color="#00e5ff" />
        <OrbitControls
          enableZoom={false}
          enablePan={false}
          maxPolarAngle={Math.PI / 1.8}
          minPolarAngle={Math.PI / 2.5}
          autoRotate
          autoRotateSpeed={0.8}
        />
        <DefenseCore
          posture={computedPosture}
          roundNumber={roundNumber}
          activeCount={activeCount}
          quarantinedCount={quarantinedCount}
        />
        <HospitalSensors hospitals={hospitals} incidents={incidents} />
      </Canvas>
    </div>
  )
}
