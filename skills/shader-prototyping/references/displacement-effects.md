# Displacement Effects

Vertex displacement modifies vertex positions in the vertex shader to create dynamic surface deformations — ripples, waves, terrain, and mouse-driven distortions.

## Vertex Displacement Basics

The core idea: in the vertex shader, offset `position` (typically along the normal) before transforming to clip space. Three.js provides `position`, `normal`, and `uv` as default attributes.

```glsl
// Vertex shader — simple sine wave displacement
uniform float u_time;
uniform float u_amplitude;
uniform float u_frequency;

varying vec2 vUv;
varying float vDisplacement;

void main() {
  vUv = uv;

  // Displacement along the normal
  float dist = length(position.xy);
  float displacement = u_amplitude * sin(u_frequency * dist - u_time * 2.0);
  vec3 newPosition = position + normal * displacement;

  vDisplacement = displacement;
  gl_Position = projectionMatrix * modelViewMatrix * vec4(newPosition, 1.0);
}
```

## Ripple Wave Formula

The standard ripple emanates from a center point with radial symmetry:

```
float displacement = amplitude * sin(frequency * distance - u_time * speed)
```

Where:
- `distance` = distance from vertex to the ripple origin
- `amplitude` = peak height of the wave
- `frequency` = how tightly packed the wave crests are
- `speed` = how fast the wave propagates outward

Multiple ripples can be summed for complex interference patterns.

## Mouse-Driven Displacement

Pass normalized mouse coordinates as `u_mouse` (vec2, range 0..1 or -1..1) and compute per-vertex distance to the mouse position projected onto the geometry surface:

```glsl
uniform vec2 u_mouse;
uniform float u_amplitude;
uniform float u_radius;

void main() {
  vUv = uv;

  // Distance from this vertex's UV to the mouse position
  float dist = distance(uv, u_mouse);

  // Localized displacement — strong near mouse, zero far away
  float displacement = u_amplitude * smoothstep(u_radius, 0.0, dist);
  vec3 newPosition = position + normal * displacement;

  vDisplacement = displacement;
  gl_Position = projectionMatrix * modelViewMatrix * vec4(newPosition, 1.0);
}
```

## Damping and Decay

For localized effects that fall off with distance, multiply the displacement by an exponential decay:

```glsl
float displacement = amplitude * sin(frequency * dist - u_time * speed) * exp(-decay * dist);
```

- `decay` controls how quickly the effect fades — higher values produce tighter, more localized ripples
- Typical range: 1.0 to 5.0 depending on geometry scale
- Combine with `smoothstep` for a hard cutoff at a maximum radius

## Geometry Subdivision Requirements

Displacement only affects vertices. If the geometry has too few vertices, the effect is invisible or blocky.

```javascript
// PlaneGeometry(width, height, widthSegments, heightSegments)
new THREE.PlaneGeometry(10, 10, 1, 1);     // 4 vertices — useless for displacement
new THREE.PlaneGeometry(10, 10, 32, 32);   // 1,089 vertices — low quality ripple
new THREE.PlaneGeometry(10, 10, 64, 64);   // 4,225 vertices — example ripple starting point
new THREE.PlaneGeometry(10, 10, 128, 128); // 16,641 vertices — good quality
new THREE.PlaneGeometry(10, 10, 256, 256); // 66,049 vertices — high quality, heavy
```

Performance tradeoff: each doubling of segments quadruples the vertex count. Start at 64x64 and increase only if the visual quality demands it. On mobile, 32x32 or 48x48 may be the practical ceiling.

## Fragment Shader for Displaced Surfaces

Use the displacement value passed as a varying to add simple lighting or color variation:

```glsl
// Fragment shader — normal-based lighting with displacement coloring
varying vec2 vUv;
varying float vDisplacement;

void main() {
  // Base color shifts with displacement
  vec3 color = mix(vec3(0.1, 0.1, 0.3), vec3(0.3, 0.6, 1.0), vDisplacement * 2.0 + 0.5);

  // Simple directional light using screen-space derivatives
  vec3 dx = dFdx(vec3(vUv, vDisplacement));
  vec3 dy = dFdy(vec3(vUv, vDisplacement));
  vec3 normal = normalize(cross(dx, dy));
  float light = dot(normal, normalize(vec3(1.0, 1.0, 1.0)));

  gl_FragColor = vec4(color * (0.5 + 0.5 * light), 1.0);
}
```

## R3F Integration

Using `shaderMaterial` in React Three Fiber with custom vertex and fragment shaders:

```jsx
import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

const vertexShader = `/* vertex shader from above */`;
const fragmentShader = `/* fragment shader from above */`;

function RipplePlane() {
  const meshRef = useRef();
  const uniformsRef = useRef({
    u_time: { value: 0 },
    u_amplitude: { value: 0.3 },
    u_frequency: { value: 4.0 },
    u_mouse: { value: new THREE.Vector2(0.5, 0.5) },
    u_radius: { value: 0.3 },
  });

  useFrame((state) => {
    uniformsRef.current.u_time.value = state.clock.elapsedTime;
  });

  return (
    <mesh
      ref={meshRef}
      onPointerMove={(e) => {
        if (e.uv) {
          uniformsRef.current.u_mouse.value.copy(e.uv);
        }
      }}
    >
      <planeGeometry args={[10, 10, 128, 128]} />
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
- Store uniforms in a `useRef` so they persist across renders without causing re-renders
- Update `u_time` in `useFrame` for animation
- Use R3F's `onPointerMove` on the mesh to get UV coordinates for mouse-driven displacement
- The `planeGeometry` args include 128x128 segments for smooth ripple

## References

- [Three.js ShaderMaterial](https://threejs.org/docs/#api/en/materials/ShaderMaterial)
- [Three.js PlaneGeometry](https://threejs.org/docs/#api/en/geometries/PlaneGeometry)
- [Three.js BufferGeometry](https://threejs.org/docs/#api/en/core/BufferGeometry)
- [WebGL Fundamentals — Shaders and GLSL](https://webglfundamentals.org/webgl/lessons/webgl-shaders-and-glsl.html)
- [The Book of Shaders — Noise](https://thebookofshaders.com/11/)
- [React Three Fiber](https://r3f.docs.pmnd.rs/getting-started/introduction)
