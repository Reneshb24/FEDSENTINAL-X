import React, { useRef, useMemo } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Html } from '@react-three/drei'
import * as THREE from 'three'

function CosineVectors() {
  const vectors = useMemo(() => {
    const list = []
    // 8 benign clustered tightly around [1, 1, 1] normalized
    for (let i = 0; i < 8; i++) {
      const spread = 0.35
      const v = new THREE.Vector3(
        1.0 + (Math.random() - 0.5) * spread,
        1.0 + (Math.random() - 0.5) * spread,
        1.0 + (Math.random() - 0.5) * spread
      ).normalize().multiplyScalar(2.2)
      list.push({ pos: [v.x, v.y, v.z], isAnomaly: false, id: `b-${i}` })
    }
    // 2 outlier vectors with divergent angular directions
    const out1 = new THREE.Vector3(-1.2, 0.2, 0.8).normalize().multiplyScalar(2.5)
    list.push({ pos: [out1.x, out1.y, out1.z], isAnomaly: true, id: 'out-1' })
    return list
  }, [])

  return (
    <group>
      {/* Origin Sphere */}
      <mesh position={[0, 0, 0]}>
        <sphereGeometry args={[0.2, 16, 16]} />
        <meshStandardMaterial color="#00e5ff" emissive="#0284c7" emissiveIntensity={0.8} />
      </mesh>

      {vectors.map((vec) => (
        <group key={vec.id}>
          {/* Ray line from origin */}
          <line>
            <bufferGeometry attach="geometry" {...new THREE.BufferGeometry().setFromPoints([
              new THREE.Vector3(0, 0, 0),
              new THREE.Vector3(...vec.pos)
            ])} />
            <lineBasicMaterial
              attach="material"
              color={vec.isAnomaly ? '#ef4444' : '#10b981'}
              transparent
              opacity={vec.isAnomaly ? 0.8 : 0.4}
            />
          </line>

          {/* Endpoint marker */}
          <mesh position={vec.pos}>
            <sphereGeometry args={[vec.isAnomaly ? 0.18 : 0.12, 12, 12]} />
            <meshStandardMaterial
              color={vec.isAnomaly ? '#ef4444' : '#10b981'}
              emissive={vec.isAnomaly ? '#b91c1c' : '#059669'}
              emissiveIntensity={1.0}
            />
          </mesh>
        </group>
      ))}
    </group>
  )
}

export default function L2CosineCluster3D({ height = '250px' }) {
  return (
    <div style={{ width: '100%', height, position: 'relative', background: 'radial-gradient(ellipse at center, rgba(14, 26, 36, 0.95) 0%, rgba(4, 8, 12, 0.98) 85%)', borderRadius: '8px', overflow: 'hidden' }}>
      <Canvas camera={{ position: [3.5, 3.5, 4.5], fov: 42 }}>
        <ambientLight intensity={0.7} />
        <pointLight position={[5, 8, 5]} intensity={1.2} />
        <OrbitControls enableZoom={false} enablePan={false} autoRotate autoRotateSpeed={0.8} />

        <CosineVectors />

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
          }}>
            L2 PAIRWISE COSINE SIMILARITY & SPATIAL CLUSTER
          </div>
        </Html>
      </Canvas>
    </div>
  )
}
