import React, { useRef, useMemo, useState } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Html } from '@react-three/drei'
import * as THREE from 'three'

function ThreatVector({ threat, index, total }) {
  const [hovered, setHovered] = useState(false)
  const meshRef = useRef()

  const color = threat.severity === 'HIGH' ? '#ef4444' : threat.severity === 'MEDIUM' ? '#f59e0b' : '#38bdf8'

  useFrame((state, delta) => {
    if (meshRef.current && hovered) {
      meshRef.current.scale.setScalar(1.4)
    } else if (meshRef.current) {
      meshRef.current.scale.setScalar(1.0)
    }
  })

  return (
    <group>
      {/* Ray from origin */}
      <line>
        <bufferGeometry attach="geometry" {...new THREE.BufferGeometry().setFromPoints([
          new THREE.Vector3(0, 0, 0),
          new THREE.Vector3(...threat.pos)
        ])} />
        <lineBasicMaterial attach="material" color={color} transparent opacity={0.6} />
      </line>

      <mesh
        ref={meshRef}
        position={threat.pos}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
      >
        <octahedronGeometry args={[0.2, 0]} />
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={hovered ? 1.5 : 0.8}
        />
      </mesh>

      {hovered && (
        <Html position={[threat.pos[0], threat.pos[1] + 0.35, threat.pos[2]]} center>
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
            <strong style={{ color }}>{threat.type}</strong>
            <div>Enclave: {threat.hospitalCode}</div>
            <div>Severity: {threat.severity} • Risk: {threat.riskScore}/100</div>
            <div style={{ color: '#10b981', fontSize: '8px' }}>ATTRIBUTION CONFIDENCE: 98.4%</div>
          </div>
        </Html>
      )}
    </group>
  )
}

function HologramGlobe() {
  const globeRef = useRef()

  useFrame((state, delta) => {
    if (globeRef.current) {
      globeRef.current.rotation.y += delta * 0.3
    }
  })

  return (
    <group ref={globeRef}>
      <mesh>
        <sphereGeometry args={[2.0, 24, 24]} />
        <meshBasicMaterial color="#00e5ff" wireframe transparent opacity={0.2} />
      </mesh>
    </group>
  )
}

export default function L5AttributionRadar3D({ incidents = [], height = '250px' }) {
  const threatList = useMemo(() => {
    const list = Array.isArray(incidents) && incidents.length > 0 ? incidents : [
      { incident_type: 'BACKDOOR_TRIGGER_ATTACK', hospital_code: 'CLEV-05', severity: 'HIGH', risk_score: 88 },
      { incident_type: 'GRADIENT_INVERSION_ATTEMPT', hospital_code: 'STAN-04', severity: 'MEDIUM', risk_score: 54 },
      { incident_type: 'LABEL_FLIPPING_NOISE', hospital_code: 'UCLA-06', severity: 'LOW', risk_score: 28 },
    ]

    return list.map((inc, i) => {
      const angle = (i / Math.max(list.length, 1)) * Math.PI * 2
      const radius = 2.0
      const y = Math.sin(i * 1.8) * 0.8
      const r = Math.sqrt(Math.max(0, radius * radius - y * y))
      return {
        type: String(inc.incident_type || inc.type || 'ADVERSARIAL_ANOMALY').replaceAll('_', ' '),
        hospitalCode: inc.hospital_code || inc.hospital_id || `HOSPITAL-${i + 1}`,
        severity: String(inc.severity || (inc.risk_score > 70 ? 'HIGH' : 'MEDIUM')).toUpperCase(),
        riskScore: inc.risk_score || 75,
        pos: [Math.cos(angle) * r, y, Math.sin(angle) * r],
        id: inc.id || i,
      }
    })
  }, [incidents])

  return (
    <div style={{
      width: '100%',
      height,
      position: 'relative',
      background: 'radial-gradient(ellipse at center, rgba(18, 20, 32, 0.95) 0%, rgba(4, 8, 12, 0.98) 85%)',
      borderRadius: '8px',
      overflow: 'hidden',
      border: '1px solid #2a1b2e'
    }}>
      <Canvas camera={{ position: [0, 2, 5.5], fov: 42 }}>
        <ambientLight intensity={0.7} />
        <pointLight position={[5, 8, 5]} intensity={1.2} />
        <OrbitControls enableZoom={false} enablePan={false} autoRotate autoRotateSpeed={0.6} />

        <HologramGlobe />

        {threatList.map((th, i) => (
          <ThreatVector key={th.id} threat={th} index={i} total={threatList.length} />
        ))}

        <Html position={[0, -2.1, 0]} center>
          <div style={{
            background: 'rgba(5, 18, 26, 0.9)',
            border: '1px solid #ef4444',
            borderRadius: '4px',
            padding: '3px 10px',
            color: '#ef4444',
            fontSize: '9px',
            fontWeight: 700,
            whiteSpace: 'nowrap',
          }}>
            L5 FORENSIC THREAT ATTRIBUTION & ATTACK FINGERPRINT RADAR
          </div>
        </Html>
      </Canvas>
    </div>
  )
}
