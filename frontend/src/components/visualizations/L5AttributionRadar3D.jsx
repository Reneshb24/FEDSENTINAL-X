import React, { useRef, useMemo } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Html } from '@react-three/drei'
import * as THREE from 'three'

function RadarSphere() {
  const sphereRef = useRef()

  useFrame((state, delta) => {
    if (sphereRef.current) {
      sphereRef.current.rotation.y += delta * 0.4
    }
  })

  return (
    <group ref={sphereRef}>
      {/* Wireframe Holographic Globe */}
      <mesh>
        <sphereGeometry args={[2.0, 24, 24]} />
        <meshBasicMaterial color="#00e5ff" wireframe transparent opacity={0.25} />
      </mesh>

      {/* Forensic Signature Clusters */}
      <mesh position={[1.4, 0.8, 0.9]}>
        <sphereGeometry args={[0.18, 12, 12]} />
        <meshStandardMaterial color="#ef4444" emissive="#b91c1c" emissiveIntensity={0.9} />
      </mesh>

      <line>
        <bufferGeometry attach="geometry" {...new THREE.BufferGeometry().setFromPoints([
          new THREE.Vector3(0, 0, 0),
          new THREE.Vector3(1.4, 0.8, 0.9)
        ])} />
        <lineBasicMaterial attach="material" color="#ef4444" transparent opacity={0.6} />
      </line>

      <Html position={[1.5, 1.1, 0.9]} center>
        <span style={{ fontSize: '8px', color: '#ef4444', fontWeight: 700, whiteSpace: 'nowrap' }}>
          ATTRIBUTED: BACKDOOR_TRIGGER_X
        </span>
      </Html>
    </group>
  )
}

export default function L5AttributionRadar3D({ height = '250px' }) {
  return (
    <div style={{ width: '100%', height, position: 'relative', background: 'radial-gradient(ellipse at center, rgba(14, 26, 38, 0.95) 0%, rgba(4, 8, 12, 0.98) 85%)', borderRadius: '8px', overflow: 'hidden' }}>
      <Canvas camera={{ position: [0, 2, 5.5], fov: 42 }}>
        <ambientLight intensity={0.7} />
        <pointLight position={[5, 8, 5]} intensity={1.2} />
        <OrbitControls enableZoom={false} enablePan={false} autoRotate autoRotateSpeed={0.8} />

        <RadarSphere />

        <Html position={[0, -2.1, 0]} center>
          <div style={{
            background: 'rgba(5, 18, 26, 0.9)',
            border: '1px solid #ef4444',
            borderRadius: '4px',
            padding: '2px 8px',
            color: '#ef4444',
            fontSize: '9px',
            fontWeight: 700,
            whiteSpace: 'nowrap',
          }}>
            L5 FORENSIC ATTACK ATTRIBUTION & THREAT RADAR
          </div>
        </Html>
      </Canvas>
    </div>
  )
}
