import React, { useRef, useMemo } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Html } from '@react-three/drei'
import * as THREE from 'three'

function ScanningLaser() {
  const laserRef = useRef()

  useFrame((state) => {
    if (laserRef.current) {
      laserRef.current.position.y = Math.sin(state.clock.elapsedTime * 2.5) * 1.5
    }
  })

  return (
    <group ref={laserRef}>
      <mesh rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[4.5, 4.5]} />
        <meshBasicMaterial color="#00e5ff" transparent opacity={0.18} side={THREE.DoubleSide} />
      </mesh>
      <lineSegments>
        <edgesGeometry args={[new THREE.PlaneGeometry(4.5, 4.5)]} />
        <lineBasicMaterial color="#00e5ff" transparent opacity={0.6} />
      </lineSegments>
    </group>
  )
}

function TensorVoxelGrid() {
  const voxels = useMemo(() => {
    const list = []
    const dim = 3
    for (let x = -1; x <= 1; x++) {
      for (let y = -1; y <= 1; y++) {
        for (let z = -1; z <= 1; z++) {
          list.push({ pos: [x * 1.1, y * 0.9, z * 1.1], id: `${x}-${y}-${z}` })
        }
      }
    }
    return list
  }, [])

  return (
    <group>
      {voxels.map((v) => (
        <group key={v.id} position={v.pos}>
          <mesh>
            <boxGeometry args={[0.55, 0.45, 0.55]} />
            <meshStandardMaterial
              color="#10b981"
              emissive="#059669"
              emissiveIntensity={0.6}
              roughness={0.2}
              transparent
              opacity={0.85}
            />
          </mesh>
          <lineSegments>
            <edgesGeometry args={[new THREE.BoxGeometry(0.56, 0.46, 0.56)]} />
            <lineBasicMaterial color="#34d399" transparent opacity={0.4} />
          </lineSegments>
        </group>
      ))}
    </group>
  )
}

export default function L0TensorScanner3D({ height = '250px' }) {
  return (
    <div style={{ width: '100%', height, position: 'relative', background: 'radial-gradient(ellipse at center, rgba(6, 26, 32, 0.95) 0%, rgba(3, 8, 12, 0.98) 85%)', borderRadius: '8px', overflow: 'hidden' }}>
      <Canvas camera={{ position: [4, 3, 5], fov: 40 }}>
        <ambientLight intensity={0.7} />
        <pointLight position={[5, 8, 5]} intensity={1.2} color="#00e5ff" />
        <OrbitControls enableZoom={false} enablePan={false} autoRotate autoRotateSpeed={0.8} maxPolarAngle={Math.PI / 2.2} minPolarAngle={Math.PI / 3.5} />

        <TensorVoxelGrid />
        <ScanningLaser />

        <Html position={[0, -2.0, 0]} center>
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
            L0 VOLUMETRIC SCAN: FLOAT32 & SAFETENSORS ATTESTED
          </div>
        </Html>
      </Canvas>
    </div>
  )
}
