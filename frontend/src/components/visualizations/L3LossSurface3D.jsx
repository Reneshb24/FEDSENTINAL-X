import React, { useRef, useMemo } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Html } from '@react-three/drei'
import * as THREE from 'three'

function LossLandscape() {
  const meshRef = useRef()

  const geom = useMemo(() => {
    const g = new THREE.PlaneGeometry(5, 5, 24, 24)
    const pos = g.attributes.position
    for (let i = 0; i < pos.count; i++) {
      const x = pos.getX(i)
      const y = pos.getY(i)
      // Paraboloid bowl: z = (x^2 + y^2) * 0.15
      const z = (x * x + y * y) * 0.12 - 0.6
      pos.setZ(i, z)
    }
    g.computeVertexNormals()
    return g
  }, [])

  return (
    <group rotation={[-Math.PI / 2, 0, 0]}>
      <mesh ref={meshRef} geometry={geom}>
        <meshStandardMaterial
          color="#0284c7"
          wireframe
          transparent
          opacity={0.4}
        />
      </mesh>
    </group>
  )
}

function TrajectoryParticles() {
  const p1Ref = useRef()
  const p2Ref = useRef()

  useFrame((state) => {
    const t = (state.clock.elapsedTime * 0.6) % 1
    if (p1Ref.current) {
      // Clean descent downhill
      const r = 2.0 * (1 - t)
      p1Ref.current.position.x = Math.cos(t * 2) * r
      p1Ref.current.position.z = Math.sin(t * 2) * r
      p1Ref.current.position.y = (r * r) * 0.12 - 0.5
    }
    if (p2Ref.current) {
      // Adversarial push uphill
      const r = 0.5 + t * 1.6
      p2Ref.current.position.x = -Math.cos(t * 1.5) * r
      p2Ref.current.position.z = -Math.sin(t * 1.5) * r
      p2Ref.current.position.y = (r * r) * 0.12 - 0.5
    }
  })

  return (
    <group>
      {/* Clean gradient descent particle */}
      <mesh ref={p1Ref}>
        <sphereGeometry args={[0.15, 12, 12]} />
        <meshStandardMaterial color="#10b981" emissive="#059669" emissiveIntensity={1.0} />
      </mesh>

      {/* Adversarial uphill particle */}
      <mesh ref={p2Ref}>
        <sphereGeometry args={[0.15, 12, 12]} />
        <meshStandardMaterial color="#ef4444" emissive="#b91c1c" emissiveIntensity={1.0} />
      </mesh>
    </group>
  )
}

export default function L3LossSurface3D({ height = '250px' }) {
  return (
    <div style={{ width: '100%', height, position: 'relative', background: 'radial-gradient(ellipse at center, rgba(14, 28, 42, 0.95) 0%, rgba(4, 8, 12, 0.98) 85%)', borderRadius: '8px', overflow: 'hidden' }}>
      <Canvas camera={{ position: [3.8, 3.2, 4.2], fov: 42 }}>
        <ambientLight intensity={0.7} />
        <pointLight position={[5, 8, 5]} intensity={1.2} />
        <OrbitControls enableZoom={false} enablePan={false} autoRotate autoRotateSpeed={0.8} />

        <LossLandscape />
        <TrajectoryParticles />

        <Html position={[0, -1.6, 0]} center>
          <div style={{
            background: 'rgba(5, 18, 26, 0.9)',
            border: '1px solid #00e5ff',
            borderRadius: '4px',
            padding: '2px 8px',
            color: '#00e5ff',
            fontSize: '9px',
            fontWeight: 700,
            whiteSpace: 'nowrap',
          }}>
            L3 SUBSAMPLING LOSS GRADIENT INFLUENCE FIELD
          </div>
        </Html>
      </Canvas>
    </div>
  )
}
