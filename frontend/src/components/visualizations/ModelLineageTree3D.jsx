import React, { useRef, useMemo, useState } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Html } from '@react-three/drei'
import * as THREE from 'three'

function VersionBlock({ version, position, isLatest, onSelect }) {
  const meshRef = useRef()
  const [hovered, setHovered] = useState(false)

  useFrame((state, delta) => {
    if (meshRef.current) {
      if (isLatest) {
        meshRef.current.rotation.y += delta * 0.4
      }
      if (hovered) {
        meshRef.current.scale.setScalar(1.2 + Math.sin(state.clock.elapsedTime * 6) * 0.08)
      } else {
        meshRef.current.scale.setScalar(1.0)
      }
    }
  })

  const color = isLatest ? '#10b981' : '#00e5ff'

  return (
    <group position={position}>
      <mesh
        ref={meshRef}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
        onClick={() => onSelect && onSelect(version)}
      >
        <boxGeometry args={[0.7, 0.7, 0.7]} />
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={isLatest ? 0.9 : 0.5}
          roughness={0.2}
        />
      </mesh>

      {/* Frame / Bevel */}
      <lineSegments>
        <edgesGeometry args={[new THREE.BoxGeometry(0.72, 0.72, 0.72)]} />
        <lineBasicMaterial color="#ffffff" transparent opacity={0.3} />
      </lineSegments>

      <Html position={[0, -0.7, 0]} center>
        <div style={{
          background: 'rgba(5, 12, 18, 0.9)',
          border: `1px solid ${color}`,
          borderRadius: '3px',
          padding: '2px 6px',
          color: '#fff',
          fontSize: '8px',
          whiteSpace: 'nowrap',
          pointerEvents: 'none',
        }}>
          <strong>{version.tag || `V${version.version_number}`}</strong>
          <span style={{ marginLeft: 4, color: '#94a3b8' }}>
            {version.accuracy ? `${(version.accuracy * 100).toFixed(1)}%` : 'Active'}
          </span>
        </div>
      </Html>
    </group>
  )
}

function HashLink({ start, end, active = true }) {
  const lineRef = useRef()

  useFrame((state) => {
    if (lineRef.current) {
      lineRef.current.material.opacity = 0.4 + Math.sin(state.clock.elapsedTime * 4) * 0.2
    }
  })

  const points = useMemo(() => [new THREE.Vector3(...start), new THREE.Vector3(...end)], [start, end])
  const geom = useMemo(() => new THREE.BufferGeometry().setFromPoints(points), [points])

  return (
    <line ref={lineRef}>
      <bufferGeometry attach="geometry" {...geom} />
      <lineBasicMaterial attach="material" color={active ? '#00e5ff' : '#64748b'} transparent opacity={0.5} />
    </line>
  )
}

export default function ModelLineageTree3D({ versions = [], height = '260px' }) {
  const versionList = useMemo(() => {
    if (Array.isArray(versions) && versions.length > 0) return versions
    return [
      { version_number: 1, tag: 'V1 (Init)', accuracy: 0.78, hash: 'sha256:7f83b1' },
      { version_number: 2, tag: 'V2 (FedAvg)', accuracy: 0.83, hash: 'sha256:9a41c2' },
      { version_number: 3, tag: 'V3 (Shield)', accuracy: 0.87, hash: 'sha256:3d8e50' },
      { version_number: 4, tag: 'V4 (Attested)', accuracy: 0.89, hash: 'sha256:bb014f' },
      { version_number: 5, tag: 'V5 (Committed)', accuracy: 0.91, hash: 'sha256:e6822a' },
    ]
  }, [versions])

  const nodes = useMemo(() => {
    const total = versionList.length
    const spacing = 1.6
    const startX = -((total - 1) * spacing) / 2
    return versionList.map((v, i) => ({
      ...v,
      pos: [startX + i * spacing, Math.sin(i * 0.8) * 0.4, (i % 2 === 0 ? 0.3 : -0.3)],
      isLatest: i === total - 1,
    }))
  }, [versionList])

  return (
    <div style={{ width: '100%', height, position: 'relative', background: 'radial-gradient(ellipse at center, rgba(14, 28, 42, 0.95) 0%, rgba(4, 9, 14, 0.98) 85%)', borderRadius: '8px', overflow: 'hidden' }}>
      <Canvas camera={{ position: [0, 2.5, 6], fov: 42 }}>
        <ambientLight intensity={0.6} />
        <pointLight position={[5, 6, 6]} intensity={1.2} />
        <OrbitControls enableZoom={true} zoomSpeed={1.0} minDistance={2} maxDistance={35} enablePan={true} panSpeed={1.0} enableRotate={true} rotateSpeed={0.8} enableDamping={true} dampingFactor={0.05} autoRotate autoRotateSpeed={0.6} />

        {/* Cryptographic Hash Chains */}
        {nodes.map((node, i) => {
          if (i === 0) return null
          const prev = nodes[i - 1]
          return <HashLink key={`link-${i}`} start={prev.pos} end={node.pos} active={node.isLatest} />
        })}

        {/* Version Checkpoint Blocks */}
        {nodes.map((node, i) => (
          <VersionBlock key={node.version_number || i} version={node} position={node.pos} isLatest={node.isLatest} />
        ))}
      </Canvas>
    </div>
  )
}
