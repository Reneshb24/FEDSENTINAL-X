import React, { useRef, useMemo, useState } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Html } from '@react-three/drei'
import * as THREE from 'three'

function LossLandscape() {
  const geom = useMemo(() => {
    const g = new THREE.PlaneGeometry(5, 5, 24, 24)
    const pos = g.attributes.position
    for (let i = 0; i < pos.count; i++) {
      const x = pos.getX(i)
      const y = pos.getY(i)
      const z = (x * x + y * y) * 0.12 - 0.6
      pos.setZ(i, z)
    }
    g.computeVertexNormals()
    return g
  }, [])

  return (
    <group rotation={[-Math.PI / 2, 0, 0]}>
      <mesh geometry={geom}>
        <meshStandardMaterial
          color="#0284c7"
          wireframe
          transparent
          opacity={0.35}
        />
      </mesh>
    </group>
  )
}

function ClientLossParticle({ client, index, total }) {
  const [hovered, setHovered] = useState(false)
  const pRef = useRef()

  const isAdversarial = client.lossDelta > 0
  const color = isAdversarial ? '#ef4444' : '#10b981'

  useFrame((state) => {
    const t = (state.clock.elapsedTime * 0.5 + index * 0.3) % 1
    if (pRef.current) {
      if (!isAdversarial) {
        // Converging downhill
        const r = (1.8 * (1 - t * 0.5))
        const angle = index * (Math.PI * 2 / Math.max(total, 1)) + t * 0.5
        pRef.current.position.x = Math.cos(angle) * r
        pRef.current.position.z = Math.sin(angle) * r
        pRef.current.position.y = (r * r) * 0.12 - 0.55
      } else {
        // Pushing uphill
        const r = (1.2 + t * 1.0)
        const angle = index * (Math.PI * 2 / Math.max(total, 1)) - t * 0.8
        pRef.current.position.x = Math.cos(angle) * r
        pRef.current.position.z = Math.sin(angle) * r
        pRef.current.position.y = (r * r) * 0.12 - 0.4
      }
    }
  })

  return (
    <group ref={pRef}>
      <mesh
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
        scale={hovered ? 1.5 : 1.0}
      >
        <sphereGeometry args={[0.15, 12, 12]} />
        <meshStandardMaterial
          color={color}
          emissive={isAdversarial ? '#b91c1c' : '#059669'}
          emissiveIntensity={hovered ? 1.4 : 0.8}
        />
      </mesh>

      {hovered && (
        <Html position={[0, 0.35, 0]} center>
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
            <strong style={{ color }}>{client.code}</strong>
            <div>Δ Loss: {client.lossDelta > 0 ? '+' : ''}{client.lossDelta.toFixed(4)}</div>
            <div style={{ color: isAdversarial ? '#ef4444' : '#10b981', fontSize: '8px' }}>
              {isAdversarial ? 'LOSS ELEVATION (ADVERSARIAL)' : 'CONVERGENT (OPTIMAL DESCENT)'}
            </div>
          </div>
        </Html>
      )}
    </group>
  )
}

export default function L3LossSurface3D({ updates = [], height = '250px' }) {
  const clients = useMemo(() => {
    const list = Array.isArray(updates) && updates.length > 0 ? updates : [
      { hospital_code: 'MAYO-01', lossDelta: -0.042 },
      { hospital_code: 'JHU-02', lossDelta: -0.038 },
      { hospital_code: 'MASS-03', lossDelta: -0.051 },
      { hospital_code: 'STAN-04', lossDelta: -0.029 },
      { hospital_code: 'CLEV-05', lossDelta: 0.185 }, // Poison uphill
      { hospital_code: 'UCLA-06', lossDelta: -0.046 },
    ]

    return list.map((u, i) => ({
      code: u.hospital_code || `NODE-${i + 1}`,
      lossDelta: Number(u.lossDelta ?? (u.evidence?.l4?.loss_delta ?? -0.04)),
      id: u.id || i,
    }))
  }, [updates])

  return (
    <div style={{
      width: '100%',
      height,
      position: 'relative',
      background: 'radial-gradient(ellipse at center, rgba(14, 28, 42, 0.95) 0%, rgba(4, 8, 12, 0.98) 85%)',
      borderRadius: '8px',
      overflow: 'hidden',
      border: '1px solid #153c48'
    }}>
      <Canvas camera={{ position: [3.8, 3.2, 4.2], fov: 42 }}>
        <ambientLight intensity={0.7} />
        <pointLight position={[5, 8, 5]} intensity={1.2} />
        <OrbitControls enableZoom={false} enablePan={false} autoRotate autoRotateSpeed={0.8} />

        <LossLandscape />

        {clients.map((c, i) => (
          <ClientLossParticle key={c.id} client={c} index={i} total={clients.length} />
        ))}

        <Html position={[0, -1.6, 0]} center>
          <div style={{
            background: 'rgba(5, 18, 26, 0.9)',
            border: '1px solid #00e5ff',
            borderRadius: '4px',
            padding: '3px 10px',
            color: '#00e5ff',
            fontSize: '9px',
            fontWeight: 700,
            whiteSpace: 'nowrap',
          }}>
            L3 SUBSAMPLING LOSS GRADIENT INFLUENCE MANIFOLD
          </div>
        </Html>
      </Canvas>
    </div>
  )
}
