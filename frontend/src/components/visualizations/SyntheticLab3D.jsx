import React, { useRef, useMemo } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Html } from '@react-three/drei'
import * as THREE from 'three'

function GeneratorHub({ isGenerating = false }) {
  const meshRef = useRef()

  useFrame((state, delta) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += delta * (isGenerating ? 1.5 : 0.5)
      meshRef.current.rotation.z += delta * (isGenerating ? 0.8 : 0.2)
    }
  })

  return (
    <group position={[0, 0, 0]}>
      <mesh ref={meshRef}>
        <octahedronGeometry args={[0.9, 0]} />
        <meshStandardMaterial
          color="#38bdf8"
          emissive="#0284c7"
          emissiveIntensity={isGenerating ? 1.2 : 0.7}
          wireframe
        />
      </mesh>
      <mesh>
        <sphereGeometry args={[0.5, 16, 16]} />
        <meshStandardMaterial color="#00e5ff" emissive="#0284c7" emissiveIntensity={0.8} />
      </mesh>
      <Html position={[0, -1.3, 0]} center>
        <span style={{ fontSize: '8px', color: '#00e5ff', fontWeight: 700, letterSpacing: '0.05em', whiteSpace: 'nowrap' }}>
          DIRICHLET GENERATOR (\alpha = 0.5)
        </span>
      </Html>
    </group>
  )
}

function SyntheticShards({ count = 10 }) {
  const shards = useMemo(() => {
    const list = []
    for (let i = 0; i < count; i++) {
      const angle = (i / count) * Math.PI * 2
      const radius = 2.8 + (i % 3) * 0.4
      list.push({
        pos: [Math.cos(angle) * radius, Math.sin(i * 1.8) * 0.8, Math.sin(angle) * radius],
        samples: 200 + (i * 35) % 300,
        id: i,
      })
    }
    return list
  }, [count])

  return (
    <group>
      {shards.map((s) => (
        <group key={s.id} position={s.pos}>
          {/* Connection ray to hub */}
          <line>
            <bufferGeometry attach="geometry" {...new THREE.BufferGeometry().setFromPoints([
              new THREE.Vector3(0, 0, 0),
              new THREE.Vector3(...s.pos).negate()
            ])} />
            <lineBasicMaterial attach="material" color="#38bdf8" transparent opacity={0.2} />
          </line>

          <mesh>
            <dodecahedronGeometry args={[0.2, 0]} />
            <meshStandardMaterial color="#10b981" emissive="#059669" emissiveIntensity={0.8} />
          </mesh>

          <Html position={[0, 0.35, 0]} center>
            <div style={{
              background: 'rgba(5, 15, 22, 0.85)',
              border: '1px solid #10b981',
              borderRadius: '3px',
              padding: '1px 4px',
              fontSize: '7px',
              color: '#10b981',
              whiteSpace: 'nowrap',
            }}>
              SHARD-{s.id + 1} ({s.samples} smp)
            </div>
          </Html>
        </group>
      ))}
    </group>
  )
}

export default function SyntheticLab3D({ height = '250px' }) {
  return (
    <div style={{ width: '100%', height, position: 'relative', background: 'radial-gradient(ellipse at center, rgba(14, 28, 42, 0.95) 0%, rgba(4, 9, 14, 0.98) 85%)', borderRadius: '8px', overflow: 'hidden' }}>
      <Canvas camera={{ position: [0, 3.5, 6], fov: 42 }}>
        <ambientLight intensity={0.7} />
        <pointLight position={[5, 8, 5]} intensity={1.2} />
        <OrbitControls enableZoom={true} zoomSpeed={1.0} minDistance={2} maxDistance={35} enablePan={true} panSpeed={1.0} enableRotate={true} rotateSpeed={0.8} enableDamping={true} dampingFactor={0.05} autoRotate autoRotateSpeed={0.6} />

        <GeneratorHub />
        <SyntheticShards count={10} />
      </Canvas>
    </div>
  )
}
