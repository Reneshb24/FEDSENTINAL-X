import React, { useEffect, useRef } from 'react';
import { Canvas, useThree } from '@react-three/fiber';
import { OrbitControls, Stats } from '@react-three/drei';
import { SceneController } from './SceneController';

/**
 * Core 3D Engine component.
 * Renders a <Canvas> and mounts the SceneController which drives the
 * visualisation based on backend state received via the WebSocketProvider.
 *
 * The component is deliberately minimal – it does not contain any animation
 * logic itself. All state updates are handled by the SceneController which
 * subscribes to the global Redux/Zustand store (or any state‑management layer
 * you prefer). This keeps the engine reusable across every page.
 */
export const Engine: React.FC = () => {
  return (
    <Canvas
      camera={{ position: [0, 5, 12], fov: 60 }}
      style={{ width: '100%', height: '100%' }}
    >
      <ambientLight intensity={0.7} />
      <directionalLight position={[5, 10, 5]} intensity={0.9} />
      <OrbitControls enablePan={true} enableZoom={true} />
      <Stats showPanel={0} />
      {/* The SceneController contains all domain‑specific 3D objects */}
      <SceneController />
    </Canvas>
  );
};
