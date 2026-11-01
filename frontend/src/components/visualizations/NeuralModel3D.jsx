import React, { useState, useRef, useMemo, Suspense } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Html } from '@react-three/drei'
import * as THREE from 'three'
import { Layers3, Cpu, Sparkles, Binary } from 'lucide-react'

const CNN_LAYERS = [
  {
    name: 'Input Layer',
    type: 'Tensor',
    shape: '1 × 28 × 28',
    params: 0,
    color: '#64748b',
    depth: 0.2,
    size: 2.2,
    activation: 'Normalized [-1, 1]',
    desc: 'Preprocessed monochrome clinical scan tensor'
  },
  {
    name: 'Conv2D_1 + Pool',
    type: 'Convolutional',
    shape: '16 × 13 × 13',
    params: 160,
    color: '#38bdf8',
    depth: 0.5,
    size: 1.8,
    activation: 'ReLU + MaxPool(2x2)',
    desc: '16 filters (3×3 kernel) feature extraction'
  },
  {
    name: 'Conv2D_2 + Pool',
    type: 'Convolutional',
    shape: '32 × 5 × 5',
    params: 4640,
    color: '#6366f1',
    depth: 0.8,
    size: 1.3,
    activation: 'ReLU + MaxPool(2x2)',
    desc: '32 filters (3×3 kernel) hierarchical representation'
  },
  {
    name: 'Dense FC_1',
    type: 'Linear Projection',
    shape: '800 → 128',
    params: 102528,
    color: '#a855f7',
    depth: 1.0,
    size: 0.9,
    activation: 'ReLU + Dropout(0.25)',
    desc: 'Dense projection into 128-dimensional latent space'
  },
  {
    name: 'Output Logits',
    type: 'Classification Head',
    shape: '128 → 10',
    params: 1290,
    color: '#10b981',
    depth: 0.3,
    size: 0.6,
    activation: 'Softmax / Log-Softmax',
    desc: '10-class diagnostic category probability distribution'
  }
]

function LayerMesh({ layer, index, total, isSelected, onSelect }) {
  const meshRef = useRef()
  const [hovered, setHovered] = useState(false)

  // Position along X axis
  const xPos = (index - (total - 1) / 2) * 2.3

  useFrame((state, delta) => {
    if (meshRef.current) {
      if (hovered || isSelected) {
        meshRef.current.rotation.y += delta * 0.8
        meshRef.current.scale.setScalar(1.08 + Math.sin(state.clock.elapsedTime * 5) * 0.05)
      } else {
        meshRef.current.rotation.y += delta * 0.15
        meshRef.current.scale.setScalar(1.0)
      }
    }
  })

  return (
    <group position={[xPos, 0, 0]}>
      <mesh
        ref={meshRef}
        onClick={(e) => {
          e.stopPropagation()
          onSelect?.(layer)
        }}
        onPointerOver={(e) => {
          e.stopPropagation()
          setHovered(true)
        }}
        onPointerOut={() => setHovered(false)}
      >
        <boxGeometry args={[layer.depth, layer.size, layer.size]} />
        <meshStandardMaterial
          color={layer.color}
          emissive={layer.color}
          emissiveIntensity={hovered || isSelected ? 1.0 : 0.3}
          roughness={0.2}
          metalness={0.4}
          transparent
          opacity={0.88}
        />
      </mesh>

      {/* Wireframe border glow */}
      <mesh>
        <boxGeometry args={[layer.depth + 0.02, layer.size + 0.02, layer.size + 0.02]} />
        <meshBasicMaterial
          color={layer.color}
          wireframe
          transparent
          opacity={hovered || isSelected ? 0.9 : 0.4}
        />
      </mesh>

      {/* Hover Info Tooltip */}
      {(hovered || isSelected) && (
        <Html distanceFactor={11} position={[0, layer.size / 2 + 0.8, 0]} center>
          <div style={{
            background: 'rgba(15, 23, 42, 0.96)',
            border: `1px solid ${layer.color}`,
            padding: '10px 14px',
            borderRadius: '6px',
            color: '#f8fafc',
            fontFamily: 'Inter, system-ui, sans-serif',
            fontSize: '11px',
            minWidth: '180px',
            boxShadow: '0 10px 25px rgba(0,0,0,0.7)',
            pointerEvents: 'none',
            zIndex: 1000
          }}>
            <div style={{ fontWeight: 700, fontSize: '12px', color: layer.color }}>
              {layer.name}
            </div>
            <div style={{ color: '#94a3b8', fontSize: '10px', marginTop: '2px' }}>
              Type: {layer.type}
            </div>
            <div style={{ marginTop: '6px', fontSize: '10px', display: 'flex', flexDirection: 'column', gap: '3px' }}>
              <div>Tensor Shape: <strong style={{ color: '#38bdf8' }}>{layer.shape}</strong></div>
              <div>Parameters: <strong>{layer.params.toLocaleString()} weights</strong></div>
              <div>Activation: <span style={{ color: '#cbd5e1' }}>{layer.activation}</span></div>
            </div>
            <div style={{ marginTop: '6px', fontSize: '9px', color: '#64748b', borderTop: '1px solid #334155', paddingTop: '4px' }}>
              {layer.desc}
            </div>
          </div>
        </Html>
      )}
    </group>
  )
}

function SynapticFlow({ total }) {
  const points = useMemo(() => {
    const list = []
    for (let i = 0; i < total - 1; i++) {
      const x1 = (i - (total - 1) / 2) * 2.3
      const x2 = (i + 1 - (total - 1) / 2) * 2.3
      for (let j = 0; j < 6; j++) {
        const yOffset = (Math.random() - 0.5) * 1.2
        const zOffset = (Math.random() - 0.5) * 1.2
        list.push([new THREE.Vector3(x1, yOffset, zOffset), new THREE.Vector3(x2, yOffset * 0.7, zOffset * 0.7)])
      }
    }
    return list
  }, [total])

  return (
    <group>
      {points.map(([p1, p2], idx) => {
        const geom = new THREE.BufferGeometry().setFromPoints([p1, p2])
        return (
          <primitive
            key={idx}
            object={new THREE.Line(geom, new THREE.LineBasicMaterial({
              color: '#38bdf8',
              transparent: true,
              opacity: 0.18,
            }))}
          />
        )
      })}
    </group>
  )
}

function WebGLFallback({ selectedLayer, onSelect }) {
  return (
    <div style={{
      width: '100%',
      minHeight: '280px',
      background: 'radial-gradient(circle at center, #0f172a 0%, #020617 100%)',
      borderRadius: '8px',
      padding: '24px',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: '12px', flexWrap: 'wrap' }}>
        {CNN_LAYERS.map((layer, i) => {
          const isSel = selectedLayer?.name === layer.name
          return (
            <div
              key={i}
              onClick={() => onSelect?.(layer)}
              style={{
                flex: '1 1 120px',
                background: isSel ? 'rgba(56, 189, 248, 0.15)' : 'rgba(30, 41, 59, 0.6)',
                border: `1px solid ${isSel ? layer.color : '#334155'}`,
                borderRadius: '6px',
                padding: '12px',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
            >
              <div style={{ color: layer.color, fontWeight: 700, fontSize: '12px' }}>{layer.name}</div>
              <div style={{ fontSize: '11px', color: '#94a3b8', marginTop: '4px' }}>{layer.shape}</div>
              <div style={{ fontSize: '10px', color: '#64748b', marginTop: '2px' }}>{layer.params.toLocaleString()} params</div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default function NeuralModel3D({
  selectedLayer = null,
  onSelectLayer = null,
  height = '340px'
}) {
  const [hasWebGL, setHasWebGL] = useState(true)

  React.useEffect(() => {
    try {
      const canvas = document.createElement('canvas')
      const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl')
      if (!gl) setHasWebGL(false)
    } catch {
      setHasWebGL(false)
    }
  }, [])

  if (!hasWebGL) {
    return <WebGLFallback selectedLayer={selectedLayer} onSelect={onSelectLayer} />
  }

  return (
    <div style={{ width: '100%', height, background: 'radial-gradient(circle at center, #0a1120 0%, #020617 100%)', borderRadius: '8px', position: 'relative', overflow: 'hidden' }}>
      <div style={{ position: 'absolute', top: 12, left: 16, zIndex: 10, pointerEvents: 'none' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#38bdf8', fontSize: '12px', fontWeight: 600 }}>
          <Layers3 size={15} />
          <span>FEDSENTINEL-CNN NEURAL ARCHITECTURE (3D)</span>
        </div>
        <div style={{ color: '#64748b', fontSize: '10px' }}>
          Conv2D Feature Pyramids • Latent Projections • Diagnostic Class Logits
        </div>
      </div>

      <Canvas
        camera={{ position: [0, 2, 7.5], fov: 45 }}
        onCreated={({ gl }) => {
          gl.setClearColor(new THREE.Color('#030712'), 1)
        }}
      >
        <ambientLight intensity={0.8} />
        <pointLight position={[10, 10, 10]} intensity={1.0} />
        <pointLight position={[-10, -5, -5]} intensity={0.6} color="#6366f1" />

        <Suspense fallback={null}>
          <SynapticFlow total={CNN_LAYERS.length} />

          {CNN_LAYERS.map((layer, index) => (
            <LayerMesh
              key={layer.name}
              layer={layer}
              index={index}
              total={CNN_LAYERS.length}
              isSelected={selectedLayer?.name === layer.name}
              onSelect={onSelectLayer}
            />
          ))}
        </Suspense>

        <OrbitControls
          enablePan={false}
          maxDistance={14}
          minDistance={3}
          autoRotate
          autoRotateSpeed={0.3}
        />
      </Canvas>
    </div>
  )
}
