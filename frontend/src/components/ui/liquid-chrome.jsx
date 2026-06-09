import { useEffect, useRef } from "react";
import { Renderer, Program, Mesh, Triangle } from "ogl";

const vert = /* glsl */`
  attribute vec2 uv;
  attribute vec2 position;
  varying vec2 vUv;
  void main() {
    vUv = uv;
    gl_Position = vec4(position, 0.0, 1.0);
  }
`;

const frag = /* glsl */`
  precision highp float;

  uniform float uTime;
  uniform vec3  uColor1;   /* stop 0 — WC blue  */
  uniform vec3  uColor2;   /* stop 0.5 — WC green */
  uniform vec3  uColor3;   /* stop 1 — WC red  */
  uniform float uSpeed;
  uniform float uAmplitude;
  uniform vec2  uMouse;

  varying vec2 vUv;

  float hash(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
  }

  float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    return mix(
      mix(hash(i),                 hash(i + vec2(1.0, 0.0)), f.x),
      mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), f.x),
      f.y
    );
  }

  void main() {
    float t = uTime * uSpeed;

    float n1 = noise(vUv * 3.0  + vec2( t * 0.40,  t * 0.30));
    float n2 = noise(vUv * 6.0  - vec2( t * 0.30,  t * 0.50));
    float n3 = noise(vUv * 12.0 + vec2( t * 0.20, -t * 0.40));
    float n  = n1 * 0.50 + n2 * 0.30 + n3 * 0.20;

    float bands  = sin((vUv.y + n * uAmplitude * 3.0) * 10.0 + t * 0.5) * 0.5 + 0.5;
    bands       += sin((vUv.x + n * uAmplitude       ) *  7.0 - t * 0.3) * 0.25;
    float v = clamp(bands * 0.5 + 0.25, 0.0, 1.0);

    /* Three-stop WC colour ramp: blue → green → red */
    vec3 ramp;
    if (v < 0.5) {
      ramp = mix(uColor1, uColor2, v * 2.0);
    } else {
      ramp = mix(uColor2, uColor3, (v - 0.5) * 2.0);
    }

    /* Chrome specular shimmer */
    ramp += vec3(pow(clamp(n3, 0.0, 1.0), 4.0) * 0.28);

    gl_FragColor = vec4(ramp, 1.0);
  }
`;

/* colors: array of three normalised RGB triples [r,g,b] — stop0, stop0.5, stop1 */
export default function LiquidChrome({
  colors     = [[0.1, 0.1, 0.1], [0.1, 0.4, 0.1], [0.5, 0.05, 0.05]],
  speed      = 1.0,
  amplitude  = 0.3,
  interactive = true,
}) {
  const containerRef = useRef(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const renderer = new Renderer({
      alpha: true,
      dpr: Math.min(window.devicePixelRatio, 2),
    });
    const gl = renderer.gl;
    gl.clearColor(colors[0][0], colors[0][1], colors[0][2], 1);
    Object.assign(gl.canvas.style, { width: "100%", height: "100%", display: "block" });
    container.appendChild(gl.canvas);

    const geometry = new Triangle(gl);
    const program  = new Program(gl, {
      vertex:   vert,
      fragment: frag,
      uniforms: {
        uTime:      { value: 0 },
        uColor1:    { value: colors[0] },
        uColor2:    { value: colors[1] },
        uColor3:    { value: colors[2] },
        uSpeed:     { value: speed },
        uAmplitude: { value: amplitude },
        uMouse:     { value: [0.5, 0.5] },
      },
    });
    const mesh = new Mesh(gl, { geometry, program });

    // Resize to fill the container at all times
    const ro = new ResizeObserver(() =>
      renderer.setSize(container.offsetWidth, container.offsetHeight)
    );
    ro.observe(container);
    renderer.setSize(container.offsetWidth, container.offsetHeight);

    const onMouseMove = (e) => {
      if (!interactive) return;
      const r = container.getBoundingClientRect();
      program.uniforms.uMouse.value = [
        (e.clientX - r.left) / r.width,
        1 - (e.clientY - r.top) / r.height,
      ];
    };
    if (interactive) container.addEventListener("mousemove", onMouseMove);

    let raf;
    const tick = (t) => {
      raf = requestAnimationFrame(tick);
      program.uniforms.uTime.value = t / 1000;
      renderer.render({ scene: mesh });
    };
    raf = requestAnimationFrame(tick);

    return () => {
      cancelAnimationFrame(raf);
      ro.disconnect();
      if (interactive) container.removeEventListener("mousemove", onMouseMove);
      if (container.contains(gl.canvas)) container.removeChild(gl.canvas);
      gl.getExtension("WEBGL_lose_context")?.loseContext();
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  return <div ref={containerRef} style={{ width: "100%", height: "100%" }} />;
}
