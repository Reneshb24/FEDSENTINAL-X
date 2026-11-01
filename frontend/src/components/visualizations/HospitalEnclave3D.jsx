import React, { useRef, useMemo, useState } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Html } from '@react-three/drei'
import * as THREE from 'three'

function EnclaveCore({ jobStatus = 'IDLE', epoch = 0, loss = null }) {
  const coreRef = useRef()
  const ringRef = useRef()
  const [hovered, setHovered] = useState(false)

  const isTraining = jobStatus === 'TRAINING' || jobStatus === 'RUNNING'
  const isComplete = jobStatus === 'COMPLETED' || jobStatus === 'ACCEPTED'

  const color = isComplete ? '#10b981' : isTraining ? '#00e5ff' : '#64748b'
  const emissive = isComplete ? '#059669' : isTraining ? '#0284c7' : '#334155'

  useFrame((state, delta) => {
    if (coreRef.current) {
      coreRef.current.rotation.y += delta * (isTraining ? 1.5 : 0.4)
      coreRef.current.rotation.x += delta * (isTraining ? 0.8 : 0.2)
    }
    if (ringRef.current) {
      ringRef.current.rotation.z -= delta * (isTraining ? 1.2 : 0.3)
    }
  })

  return (
    <group position={[0, 0, 0]}>
      {/* Central Secure Enclave Compute Core */}
      <mesh
        ref={coreRef}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
        scale={hovered ? 1.3 : 1.0}
      >
        <octahedronGeometry args={[1.0, 0]} />
        <meshStandardMaterial
          color={color}
          emissive={emissive}
          emissiveIntensity={isTraining ? 1.4 : 0.8}
          roughness={0.2}
          wireframe={!isTraining && !isComplete}
        />
      </mesh>

      {/* Outer Enclave Boundary Shield */}
      <mesh ref={ringRef} rotation={[Math.PI / 2, 0, 0]}>
        <torusGeometry args={[1.6, 0.035, 16, 64]} />
        <meshBasicMaterial color={color} transparent opacity={0.6} />
      </mesh>

      <Html position={[0, -1.8, 0]} center>
        <div style={{
          background: 'rgba(5, 15, 25, 0.95)',
          border: `1px solid ${color}`,
          borderRadius: '4px',
          padding: '4px 10px',
          color: color,
          fontSize: '9px',
          fontWeight: 700,
          whiteSpace: 'nowrap',
          letterSpacing: '0.06em',
          boxShadow: `0 0 12px ${color}40`,
        }}>
          <div>ENCLAVE STATUS: {jobStatus}</div>
          {hovered && (
            <div style={{ fontSize: '8px', color: '#94a3b8', marginTop: 2, fontWeight: 500 }}>
              {isTraining ? `Epoch ${epoch} • Loss: ${loss ? loss.toFixed(4) : 'Computing'}` : 'Confidential Local Compute'}
            </div>
          )}
        </div>
      </Html>
    </group>
  )
}

function DataVault({ datasetName = 'MNIST Balanced', sampleCount = 1000 }) {
  const [hovered, setHovered] = useState(false)

  return (
    <group
      position={[-2.8, 0, 0]}
      onPointerOver={() => setHovered(true)}
      onPointerOut={() => setHovered(false)}
    >
      <mesh scale={hovered ? 1.2 : 1.0}>
        <boxGeometry args={[0.9, 0.9, 0.9]} />
        <meshStandardMaterial color="#38bdf8" emissive="#0284c7" emissiveIntensity={0.8} roughness={0.3} />
      </mesh>

      {/* Confidentiality Lock Ring */}
      <lineSegments>
        <edgesGeometry args={[new THREE.BoxGeometry(0.92, 0.92, 0.92)]} />
        <lineBasicMaterial color="#ffffff" transparent opacity={0.4} />
      </lineSegments>

      <Html position={[0, -0.9, 0]} center>
        <div style={{
          background: 'rgba(4, 15, 25, 0.92)',
          border: '1px solid #38bdf8',
          borderRadius: '3px',
          padding: '2px 6px',
          color: '#38bdf8',
          fontSize: '8px',
          fontWeight: 700,
          whiteSpace: 'nowrap',
        }}>
          LOCAL DATA VAULT
        </div>
      </Html>

      {hovered && (
        <Html position={[0, 0.9, 0]} center>
          <div style={{
            background: 'rgba(4, 15, 25, 0.96)',
            border: '1px solid #38bdf8',
            borderRadius: '4px',
            padding: '4px 8px',
            color: '#fff',
            fontSize: '9px',
            whiteSpace: 'nowrap',
            boxShadow: '0 0 10px rgba(56, 189, 248, 0.4)',
          }}>
            <strong style={{ color: '#38bdf8' }}>{datasetName}</strong>
            <div>Samples: {sampleCount.toLocaleString()} Scans</div>
            <div style={{ color: '#10b981', fontSize: '8px' }}>STRICTLY ISOLATED (0 BYTES EGRESS)</div>
          </div>
        </Html>
      )}
    </group>
  )
}

function EgressGate({ hash = null, isSubmitted = false }) {
  const [hovered, setHovered] = useState(false)
  const color = isSubmitted ? '#10b981' : '#f59e0b'

  return (
    <group
      position={[2.8, 0, 0]}
      onPointerOver={() => setHovered(true)}
      onPointerOut={() => setHovered(false)}
    >
      <mesh scale={hovered ? 1.2 : 1.0}>
        <cylinderGeometry args={[0.45, 0.45, 0.7, 16]} />
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.8} />
      </mesh>

      <Html position={[0, -0.9, 0]} center>
        <div style={{
          background: 'rgba(5, 18, 26, 0.92)',
          border: `1px solid ${color}`,
          borderRadius: '3px',
          padding: '2px 6px',
          color,
          fontSize: '8px',
          fontWeight: 700,
          whiteSpace: 'nowrap',
        }}>
          SAFETENSORS EGRESS GATE
        </div>
      </Html>

      {hovered && (
        <Html position={[0, 0.9, 0]} center>
          <div style={{
            background: 'rgba(5, 18, 26, 0.96)',
            border: `1px solid ${color}`,
            borderRadius: '4px',
            padding: '4px 8px',
            color: '#fff',
            fontSize: '9px',
            whiteSpace: 'nowrap',
            boxShadow: `0 0 10px ${color}60`,
          }}>
            <strong style={{ color }}>Zero-Pickle SafeTensors Egress</strong>
            <div>SHA-256: {hash ? hash.slice(0, 16) + '...' : 'Attested Digest'}</div>
            <div style={{ color: '#10b981', fontSize: '8px' }}>WEIGHT DELTA ONLY (NO RAW DATA)</div>
          </div>
        </Html>
      )}
    </group>
  )
}

function DataBus({ isTraining = false }) {
  const p1Ref = useRef()
  const p2Ref = useRef()

  useFrame((state) => {
    const t = (state.clock.elapsedTime * (isTraining ? 1.2 : 0.4)) % 1
    if (p1Ref.current) {
      // From Data Vault to Core
      p1Ref.current.position.x = -2.8 + t * 2.8
    }
    if (p2Ref.current) {
      // From Core to Egress Gate
      p2Ref.current.position.x = 0 + t * 2.8
    }
  })

  return (
    <group>
      {/* Vault to Core bus line */}
      <line>
        <bufferGeometry attach="geometry" {...new THREE.BufferGeometry().setFromPoints([
          new THREE.Vector3(-2.8, 0, 0),
          new THREE.Vector3(0, 0, 0)
        ])} />
        <lineBasicMaterial attach="material" color="#38bdf8" transparent opacity={0.4} />
      </line>

      {/* Core to Egress line */}
      <line>
        <bufferGeometry attach="geometry" {...new THREE.BufferGeometry().setFromPoints([
          new THREE.Vector3(0, 0, 0),
          new THREE.Vector3(2.8, 0, 0)
        ])} />
        <lineBasicMaterial attach="material" color="#10b981" transparent opacity={0.4} />
      </line>

      <mesh ref={p1Ref}>
        <sphereGeometry args={[0.08, 12, 12]} />
        <meshBasicMaterial color="#38bdf8" />
      </mesh>

      <mesh ref={p2Ref}>
        <sphereGeometry args={[0.08, 12, 12]} />
        <meshBasicMaterial color="#10b981" />
      </mesh>
    </group>
  )
}

export default function HospitalEnclave3D({
  jobStatus = 'IDLE',
  epoch = 0,
  loss = null,
  datasetName = 'MNIST Balanced',
  sampleCount = 1000,
  hash = null,
  height = '240px',
}) {
  const isTraining = jobStatus === 'TRAINING' || jobStatus === 'RUNNING'
  const isSubmitted = jobStatus === 'COMPLETED' || jobStatus === 'ACCEPTED' || jobStatus === 'SUBMITTED'

  return (
    <div style={{
      width: '100%',
      height,
      position: 'relative',
      background: 'radial-gradient(ellipse at center, rgba(8, 28, 38, 0.95) 0%, rgba(4, 8, 13, 0.98) 85%)',
      borderRadius: '8px',
      overflow: 'hidden',
      border: '1px solid #143542'
    }}>
      <Canvas camera={{ position: [0, 2, 6.2], fov: 42 }}>
        <ambientLight intensity={0.7} />
        <pointLight position={[5, 8, 5]} intensity={1.2} />
        <OrbitControls enableZoom={false} enablePan={false} autoRotate autoRotateSpeed={0.5} maxPolarAngle={Math.PI / 2.1} minPolarAngle={Math.PI / 3} />

        <DataVault datasetName={datasetName} sampleCount={sampleCount} />
        <EnclaveCore jobStatus={jobStatus} epoch={epoch} loss={loss} />
        <EgressGate hash={hash} isSubmitted={isSubmitted} />
        <DataBus isTraining={isTraining} />
      </Canvas>
    </div>
  )
}
