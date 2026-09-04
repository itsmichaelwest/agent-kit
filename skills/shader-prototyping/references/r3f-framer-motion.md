# R3F + Framer Motion Integration

Combining React Three Fiber for 3D shader effects with Framer Motion for 2D UI animations — the standard pattern for marketing pages with interactive WebGL backgrounds.

## Canvas + Overlay Layering Pattern

The fundamental layout: an R3F Canvas renders the 3D shader effect as a background, and a Framer Motion div overlays 2D content (headings, CTAs, copy) on top.

```tsx
import { Canvas } from '@react-three/fiber';
import { motion } from 'framer-motion';
import { RipplePlane } from './RipplePlane';

function HeroSection() {
  return (
    <div style={{ position: 'relative', width: '100%', height: '100vh' }}>
      {/* 3D background layer */}
      <Canvas
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          zIndex: 0,
        }}
        dpr={[1, 2]}
        camera={{ position: [0, 0, 5], fov: 45 }}
      >
        <RipplePlane />
      </Canvas>

      {/* 2D overlay layer */}
      <motion.div
        style={{
          position: 'relative',
          zIndex: 1,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100%',
          padding: '2rem',
        }}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: 'easeOut' }}
      >
        <h1>Your Heading</h1>
        <p>Subtext goes here</p>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          Get Started
        </motion.button>
      </motion.div>
    </div>
  );
}
```

### CSS Layering Rules

- Canvas: `position: absolute`, `z-index: 0` (or lower)
- Overlay: `position: relative`, `z-index: 1` (or higher)
- Parent container: `position: relative` to establish stacking context
- Canvas fills the parent via `width: 100%; height: 100%`

## Pointer Event Forwarding

The Canvas element captures pointer events by default, which blocks clicks on the 2D overlay.

### Strategy 1: Disable Canvas Pointer Events

When the overlay needs full interactivity and the shader does not respond to mouse:

```tsx
<Canvas style={{ pointerEvents: 'none' }} />
```

### Strategy 2: Selective Forwarding

When both the shader and overlay need pointer events:

```tsx
<Canvas
  style={{ pointerEvents: 'none' }}
  // Re-enable pointer events on specific meshes via onPointerMove
/>
```

Or use CSS to make the overlay intercept events and manually forward mouse positions to the shader via shared state (React context or a store like zustand).

### Strategy 3: Overlay Passes Through

When only the shader needs interaction:

```tsx
<motion.div style={{ pointerEvents: 'none' }}>
  {/* Non-interactive overlay content */}
</motion.div>
```

## Motion-Wrapped Meshes with framer-motion-3d

> **Compatibility:** The [official integration guide](https://motion.dev/docs/react-three-fiber), checked on 2026-09-04, marks this integration deprecated, documents `framer-motion-3d`, and limits it to React 18. It does not document a `motion/react-three` replacement. Check installed versions and exports before using these examples. Preserve an existing compatible integration; select a supported approach for new work.

The documented `framer-motion-3d` integration provides motion components for R3F meshes:

```tsx
import { motion } from 'framer-motion-3d';

function AnimatedMesh() {
  return (
    <motion.mesh
      initial={{ scale: 0 }}
      animate={{ scale: 1 }}
      transition={{ type: 'spring', stiffness: 100, damping: 15 }}
    >
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial color="hotpink" />
    </motion.mesh>
  );
}
```

Supported animated properties: `position`, `rotation`, `scale`. These animate the Three.js object properties directly using Framer Motion's spring/tween engine.

## useFrame + Spring Bridging

The bridge pattern connects Framer Motion's 2D spring system to shader uniforms updated every frame in R3F.

### Pattern: useMotionValue to Shader Uniform

```tsx
import { useRef, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import { useMotionValue, useSpring } from 'framer-motion';

function BridgedShaderPlane() {
  const meshRef = useRef();
  const uniformsRef = useRef({
    u_time: { value: 0 },
    u_intensity: { value: 0 },
  });

  // Framer Motion spring
  const rawIntensity = useMotionValue(0);
  const springIntensity = useSpring(rawIntensity, {
    stiffness: 100,
    damping: 20,
  });

  useFrame((state) => {
    uniformsRef.current.u_time.value = state.clock.elapsedTime;
    // Bridge: read the spring's current value and push to uniform
    uniformsRef.current.u_intensity.value = springIntensity.get();
  });

  return (
    <mesh
      ref={meshRef}
      onPointerEnter={() => rawIntensity.set(1)}
      onPointerLeave={() => rawIntensity.set(0)}
    >
      <planeGeometry args={[10, 10, 64, 64]} />
      <shaderMaterial
        vertexShader={vertexShader}
        fragmentShader={fragmentShader}
        uniforms={uniformsRef.current}
      />
    </mesh>
  );
}
```

Key points:
- `useMotionValue` + `useSpring` create the spring in Framer Motion's system
- `useFrame` reads `.get()` every frame and writes to the uniform
- The spring animates smoothly without causing React re-renders
- Pointer events on the mesh trigger the spring target changes

### Pattern: @react-spring/three for Pure 3D Springs

When you do not need Framer Motion 2D at all, `@react-spring/three` integrates springs directly:

```tsx
import { useSpring, animated } from '@react-spring/three';

function SpringMesh() {
  const [springs, api] = useSpring(() => ({
    scale: [1, 1, 1],
    config: { mass: 1, tension: 170, friction: 26 },
  }));

  return (
    <animated.mesh
      scale={springs.scale}
      onPointerEnter={() => api.start({ scale: [1.2, 1.2, 1.2] })}
      onPointerLeave={() => api.start({ scale: [1, 1, 1] })}
    >
      <sphereGeometry args={[1, 32, 32]} />
      <meshStandardMaterial color="royalblue" />
    </animated.mesh>
  );
}
```

## Complete Example: Displacement Background + Animated Overlay

```tsx
import { Canvas } from '@react-three/fiber';
import { motion } from 'framer-motion';
import { RipplePlane } from './RipplePlane';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.15, delayChildren: 0.3 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.6 } },
};

export function MarketingHero() {
  return (
    <section style={{ position: 'relative', height: '100vh', overflow: 'hidden' }}>
      <Canvas
        style={{ position: 'absolute', inset: 0, zIndex: 0 }}
        dpr={[1, 1.5]}
        camera={{ position: [0, 0, 5] }}
        gl={{ antialias: true, alpha: true }}
      >
        <RipplePlane />
      </Canvas>

      <motion.div
        style={{
          position: 'relative',
          zIndex: 1,
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          textAlign: 'center',
          color: '#fff',
        }}
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <motion.h1 variants={itemVariants} style={{ fontSize: '3rem' }}>
          Immersive Experience
        </motion.h1>
        <motion.p variants={itemVariants} style={{ fontSize: '1.25rem', maxWidth: '40ch' }}>
          A shader-driven hero section with layered 2D animations.
        </motion.p>
        <motion.button
          variants={itemVariants}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          style={{
            marginTop: '2rem',
            padding: '0.75rem 2rem',
            fontSize: '1rem',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer',
          }}
        >
          Learn More
        </motion.button>
      </motion.div>
    </section>
  );
}
```

## References

- [React Three Fiber](https://r3f.docs.pmnd.rs/getting-started/introduction)
- [Motion for React Three Fiber](https://motion.dev/docs/react-three-fiber)
- [Motion docs — useMotionValue](https://motion.dev/docs/react-motion-value)
- [Motion docs — useSpring](https://motion.dev/docs/react-use-spring)
- [@react-spring/three](https://react-spring.dev/docs/guides/react-three-fiber)
- [@react-three/drei](https://drei.docs.pmnd.rs/)
