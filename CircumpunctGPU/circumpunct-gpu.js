// ================================================================
// CircumpunctGPU: A GPU pipeline compiler that takes recursive
// field-boundary primitives and turns them into compute and render
// passes, choosing point, edge, surface, or volume expressions
// from one shared representation.
//
// Not a wrapper around Three.js. Not a visualization.
// The scene representation and pass compiler that sits on WebGPU.
// ================================================================

// ============================================================
// FRAMEWORK CONSTANTS (derived, not parameters)
// ============================================================
const PHI = (1 + Math.sqrt(5)) / 2;
const PHI_INV = 1 / PHI;
const T = 3;
const W = 2 * T + 1;           // 7
const V = 4 * T + 1;           // 13
const R = T * T - 2;           // 7
const P = T + 1;               // 4
const G = T * (T + 1);         // 12
const S = Math.pow(T + 1, T);  // 64
const E_AP = V / (V - 1);              // 13/12
const E_FI = W * (W + 1) / (T * V);    // 56/39
const E_BO = T * W;                     // 21
const LAM_C = W / T;                    // 7/3
const LAM_E = (W + 1) / V;             // 8/13
const MEDIATOR = Math.pow(T, T) / 2;   // 13.5
const FOV_RAD = 2 * Math.atan((V - 1) / V);
const NEAR = 1 / E_BO;                 // 1/21
const FAR = (V - 1) / V * 40;          // ~36.9

// CircNode byte layout: 64 bytes per node
// position: vec4f (xyz = pos, w = scale)          offset 0
// state:    vec4f (x=balance, y=phase, z=d, w=vis) offset 16
// hierarchy: vec4u (parent, child_start, count, flags) offset 32
// derived:  vec4f (repr, error, conv_w, emer_w)    offset 48
const CIRC_NODE_SIZE = 64;
const MAX_NODES = 4096;

// ============================================================
// WGSL: SHARED CONSTANTS AND STRUCTS
// ============================================================
const WGSL_PREAMBLE = /* wgsl */`

// Framework constants
const PHI: f32 = 1.6180339887;
const PHI_INV: f32 = 0.6180339887;
const PI: f32 = 3.14159265359;
const TAU: f32 = 6.28318530718;
const Tc: f32 = 3.0;
const Wc: f32 = 7.0;
const Vc: f32 = 13.0;
const E_AP: f32 = 1.0833333;
const E_FI: f32 = 1.4358974;
const E_BO: f32 = 21.0;
const LAM_C: f32 = 2.3333333;
const LAM_E: f32 = 0.6153846;
const MEDIATOR: f32 = 13.5;

struct CircNode {
  position: vec4f,
  state: vec4f,
  hierarchy: vec4u,
  derived: vec4f,
};

struct FrameUniforms {
  time: f32,
  dt: f32,
  pump_speed: f32,
  node_count: u32,
  cam_pos: vec4f,
  cam_fwd: vec4f,
  cam_up: vec4f,
  cam_right: vec4f,
  proj: mat4x4f,
  view: mat4x4f,
};
`;

// ============================================================
// WGSL: PUMP CYCLE COMPUTE SHADER
// Phi(t+dt) = emerge . i . converge [ Phi(t) ]
// ============================================================
const WGSL_PUMP = WGSL_PREAMBLE + /* wgsl */`

@group(0) @binding(0) var<storage, read_write> nodes: array<CircNode>;
@group(0) @binding(1) var<uniform> frame: FrameUniforms;

@compute @workgroup_size(64)
fn pump(@builtin(global_invocation_id) id: vec3u) {
  let idx = id.x;
  if (idx >= frame.node_count) { return; }

  var node = nodes[idx];
  let dt = frame.dt;
  let speed = frame.pump_speed;

  // Advance pump phase: 0..1 cycling through the four strokes
  let phase = fract(node.state.y + dt * speed * 0.2);
  node.state.y = phase;

  // Convergence/emergence weights from pump phase
  let conv = max(0.0, cos(phase * TAU));
  let emer = max(0.0, -cos(phase * TAU));
  node.derived.z = conv;
  node.derived.w = emer;

  let scale = node.position.w;
  let balance = node.state.x;

  // ⊛ CONVERGENCE: pull toward parent
  let parentIdx = node.hierarchy.x;
  if (parentIdx != 0xFFFFFFFFu) {
    let parent = nodes[parentIdx];
    let toParent = parent.position.xyz - node.position.xyz;
    let dist = length(toParent);
    if (dist > 0.001) {
      // Convergence strength shaped by V/(V-1) = aperture operator
      let pull = conv * dt * E_AP * 0.5 * scale;
      let dir = toParent / dist;
      node.position = vec4f(
        node.position.xyz + dir * pull,
        node.position.w
      );
    }
  }

  // i: ROTATION (the 90-degree phase turn)
  // Modulate the phase of child nodes relative to parent
  // The i-turn mixes convergence and emergence channels
  let iTurn = sin(phase * TAU);
  // (stored for render shader to use for local rotation)

  // ✹ EMERGENCE: scale breathes with pump
  let breathe = 1.0 + 0.015 * (conv - emer);
  node.position.w = scale * mix(1.0, breathe, speed * 0.5);

  // Balance drift: if unbalanced, gently restore toward 0.5
  let balDrift = (0.5 - balance) * dt * 0.1;
  node.state.x = clamp(balance + balDrift, 0.01, 0.99);

  nodes[idx] = node;
}
`;

// ============================================================
// WGSL: LOD / VISIBILITY / REPRESENTATION COMPUTE SHADER
// Chooses dimensional expression per node based on
// projected size, dim_depth, and parent visibility.
// Writes visible instance data for the render pass.
// ============================================================
const WGSL_LOD = WGSL_PREAMBLE + /* wgsl */`

struct DrawInstance {
  pos_scale: vec4f,
  state: vec4f,
  color: vec4f,
};

struct IndirectArgs {
  vertex_count: u32,
  instance_count: atomic<u32>,
  first_vertex: u32,
  first_instance: u32,
};

@group(0) @binding(0) var<storage, read> nodes: array<CircNode>;
@group(0) @binding(1) var<uniform> frame: FrameUniforms;
@group(0) @binding(2) var<storage, read_write> instances: array<DrawInstance>;
@group(0) @binding(3) var<storage, read_write> indirect: IndirectArgs;

@compute @workgroup_size(64)
fn evaluate(@builtin(global_invocation_id) id: vec3u) {
  let idx = id.x;
  if (idx >= frame.node_count) { return; }

  let node = nodes[idx];
  let pos = node.position.xyz;
  let scale = node.position.w;
  let d = node.state.z;
  let balance = node.state.x;
  let phase = node.state.y;
  let conv = node.derived.z;
  let emer = node.derived.w;

  // Projected size: screen-space error metric
  let toNode = pos - frame.cam_pos.xyz;
  let dist = length(toNode);
  let projected = scale / max(dist, 0.01);

  // Visibility: distance culling + parent visibility
  var vis = smoothstep(40.0, 30.0, dist);
  let parentIdx = node.hierarchy.x;
  if (parentIdx != 0xFFFFFFFFu) {
    vis *= nodes[parentIdx].state.w;
  }

  // Skip invisible nodes
  if (vis < 0.01 || projected < 0.002) { return; }

  // Representation mode from projected size and dim_depth
  // The dimensional ladder IS the LOD system
  var repr: u32 = 0u;  // 0D: point
  if (projected > 0.008) { repr = 1u; }  // 1D: line/edge
  if (projected > 0.03)  { repr = 2u; }  // 2D: surface
  if (projected > 0.12)  { repr = 3u; }  // 3D: volume/SDF

  // Can't render higher dimension than d allows
  let maxRepr = u32(floor(d));
  repr = min(repr, maxRepr);

  // Color by component and state
  let colAperture = vec3f(0.91, 0.54, 0.69);
  let colField = vec3f(0.30, 0.72, 0.63);
  let colBoundary = vec3f(0.30, 0.63, 0.78);
  let colGold = vec3f(0.78, 0.72, 0.47);

  // Blend by dimensional depth
  let t1 = smoothstep(0.0, 1.0, d);
  let t2 = smoothstep(1.0, 2.0, d);
  let t3 = smoothstep(2.0, 3.0, d);
  var col = mix(colAperture, colField, t1);
  col = mix(col, colBoundary, t2);
  col = mix(col, colGold, t3 * 0.3);

  // Pump pulse
  col *= 0.8 + 0.2 * cos(phase * TAU);
  // Convergence warmth
  col += colAperture * conv * 0.15;
  // Emergence coolness
  col += colBoundary * emer * 0.1;

  // Write visible instance
  let slot = atomicAdd(&indirect.instance_count, 1u);
  instances[slot].pos_scale = vec4f(pos, scale);
  instances[slot].state = vec4f(balance, phase, d, f32(repr));
  instances[slot].color = vec4f(col * vis, vis);
}
`;

// ============================================================
// WGSL: RENDER VERTEX SHADER
// Billboard quads positioned per instance.
// The three W-V operators applied as the transform:
//   aperture (V/(V-1)), field (W(W+1)/(TV)), boundary (TW)
// ============================================================
const WGSL_VERTEX = WGSL_PREAMBLE + /* wgsl */`

struct DrawInstance {
  pos_scale: vec4f,
  state: vec4f,
  color: vec4f,
};

struct VSOut {
  @builtin(position) pos: vec4f,
  @location(0) uv: vec2f,
  @location(1) color: vec4f,
  @location(2) state: vec4f,
};

@group(0) @binding(0) var<uniform> frame: FrameUniforms;
@group(0) @binding(1) var<storage, read> instances: array<DrawInstance>;

// Quad vertices: 6 vertices, 2 triangles
const QUAD_POS = array<vec2f, 6>(
  vec2f(-1, -1), vec2f(1, -1), vec2f(-1, 1),
  vec2f(-1, 1),  vec2f(1, -1), vec2f(1, 1),
);

@vertex
fn vs_main(
  @builtin(vertex_index) vid: u32,
  @builtin(instance_index) iid: u32,
) -> VSOut {
  let inst = instances[iid];
  let qp = QUAD_POS[vid];

  let worldPos = inst.pos_scale.xyz;
  let scale = inst.pos_scale.w;
  let repr = u32(inst.state.w);
  let phase = inst.state.y;
  let balance = inst.state.x;

  // Billboard size depends on representation mode
  // 0D point: tiny, 1D line: elongated, 2D surface: disk-sized, 3D: full scale
  var billboardScale: f32;
  switch repr {
    case 0u: { billboardScale = scale * 0.15; }
    case 1u: { billboardScale = scale * 0.4; }
    case 2u: { billboardScale = scale * 0.8; }
    default: { billboardScale = scale * 1.2; }
  }

  // ================================================
  // THE THREE W-V OPERATORS AS TRANSFORM
  // ================================================

  // Stage 1: APERTURE V/(V-1) = 13/12
  // Convergence toward the viewer axis
  let convDir = normalize(frame.cam_pos.xyz - worldPos);
  let apStretch = E_AP;
  // Stretch the billboard slightly along convergence direction
  // (applied via the billboard offset below)

  // Stage 2: FIELD W(W+1)/(TV) = 56/39
  // i-turn: rotate the billboard by pump phase
  let iTurn = sin(phase * TAU) * 0.15;
  let cosI = cos(iTurn);
  let sinI = sin(iTurn);
  let rotUV = vec2f(
    qp.x * cosI - qp.y * sinI,
    qp.x * sinI + qp.y * cosI
  );

  // Stage 3: BOUNDARY TW = 21
  // Commit to screen. The projection does this.

  // Billboard in view space
  let right = frame.cam_right.xyz;
  let up = frame.cam_up.xyz;

  // Apply aperture stretch along convergence axis
  let stretchedRight = right * apStretch;

  let offset = (stretchedRight * rotUV.x + up * rotUV.y) * billboardScale;
  let finalPos = worldPos + offset;

  // Project with framework-derived matrices
  let viewPos = frame.view * vec4f(finalPos, 1.0);
  let clipPos = frame.proj * viewPos;

  var out: VSOut;
  out.pos = clipPos;
  out.uv = qp * 0.5 + 0.5;
  out.color = inst.color;
  out.state = inst.state;
  return out;
}
`;

// ============================================================
// WGSL: RENDER FRAGMENT SHADER
// Evaluates the circumpunct at each pixel.
// Representation mode determines what's drawn:
//   0D: glowing point
//   1D: line/worldline
//   2D: field disk
//   3D: full circumpunct SDF (aperture + field + boundary)
// ============================================================
const WGSL_FRAGMENT = /* wgsl */`

const PI: f32 = 3.14159265359;
const TAU: f32 = 6.28318530718;
const PHI: f32 = 1.6180339887;

struct FSOut {
  @location(0) color: vec4f,
};

@fragment
fn fs_main(
  @location(0) uv: vec2f,
  @location(1) color: vec4f,
  @location(2) state: vec4f,
) -> FSOut {
  let balance = state.x;
  let phase = state.y;
  let d = state.z;
  let repr = u32(state.w);

  // UV centered: -1..1
  let p = uv * 2.0 - 1.0;
  let r = length(p);
  let angle = atan2(p.y, p.x);

  var col = color.rgb;
  var alpha = color.a;

  switch repr {
    // ----------------------------------------
    // 0D: APERTURE (point sprite)
    // Glowing dot, Gaussian falloff
    // ----------------------------------------
    case 0u: {
      let glow = exp(-r * r * 8.0);
      col *= glow * 1.5;
      alpha *= glow;
    }

    // ----------------------------------------
    // 1D: WORLDLINE (line)
    // Vertical line through center, thin
    // ----------------------------------------
    case 1u: {
      let lineWidth = 0.08 + 0.04 * sin(phase * TAU);
      let lineDist = abs(p.x);
      let lineAlpha = smoothstep(lineWidth, lineWidth * 0.3, lineDist);
      // Point at center
      let pointGlow = exp(-r * r * 12.0) * 0.6;
      col *= lineAlpha + pointGlow;
      alpha *= max(lineAlpha, pointGlow);
    }

    // ----------------------------------------
    // 2D: FIELD (disk / surface)
    // Flat disk with balance shaping the density
    // Plus aperture dot at center
    // ----------------------------------------
    case 2u: {
      // Disk edge
      let diskR = 0.7 + balance * 0.2;
      let diskAlpha = smoothstep(diskR, diskR - 0.15, r);
      // Radial density shaped by balance
      let density = mix(
        1.0 - r * 0.5,
        exp(-r * r * 2.0),
        balance
      );
      // Aperture glow at center
      let apGlow = exp(-r * r * 16.0) * 0.5;
      // Concentric rings (field structure)
      let rings = 0.8 + 0.2 * sin(r * 12.0 - phase * TAU * 2.0);

      col *= (density * rings * diskAlpha + apGlow);
      alpha *= max(diskAlpha * density * 0.7, apGlow);
    }

    // ----------------------------------------
    // 3D: FULL CIRCUMPUNCT (SDF)
    // Aperture + field + boundary torus
    // The complete expression
    // ----------------------------------------
    default: {
      // Aperture: bright center
      let apR = 0.08;
      let apGlow = exp(-r * r * 20.0);

      // Field: disk region
      let fieldR = 0.5 + balance * 0.2;
      let fieldAlpha = smoothstep(fieldR, fieldR - 0.12, r);
      let fieldDensity = mix(1.0 - r * 0.7, exp(-r * r * 3.0), balance);
      let fieldRings = 0.85 + 0.15 * sin(r * 16.0 - phase * TAU * 3.0);

      // Boundary: torus ring
      let boundR = 0.82;
      let boundWidth = 0.06;
      let torusDist = abs(r - boundR);
      let boundAlpha = smoothstep(boundWidth, boundWidth * 0.2, torusDist);

      // Pump cycle: convergence brightens center, emergence brightens boundary
      let conv = max(0.0, cos(phase * TAU));
      let emer = max(0.0, -cos(phase * TAU));

      let centerCol = col * 1.3 + vec3f(0.2, 0.1, 0.05) * conv;
      let edgeCol = col * 0.8 + vec3f(0.05, 0.1, 0.2) * emer;

      // Compose layers
      var final_col = edgeCol * boundAlpha * 0.7;
      final_col += col * fieldAlpha * fieldDensity * fieldRings * 0.5;
      final_col += centerCol * apGlow * 1.5;

      col = final_col;
      alpha *= max(max(apGlow * 0.8, fieldAlpha * fieldDensity * 0.5), boundAlpha * 0.6);
    }
  }

  // Soft edge
  alpha *= smoothstep(1.0, 0.85, r);

  return FSOut(vec4f(col, alpha));
}
`;

// ============================================================
// CircumpunctGPU CLASS
// ============================================================
class CircumpunctGPU {
  constructor() {
    this.device = null;
    this.context = null;
    this.format = null;

    // Pipelines
    this.pumpPipeline = null;
    this.lodPipeline = null;
    this.renderPipeline = null;

    // Buffers
    this.nodeBuffer = null;
    this.instanceBuffer = null;
    this.indirectBuffer = null;
    this.frameUniformBuffer = null;

    // Bind groups
    this.pumpBindGroup = null;
    this.lodBindGroup = null;
    this.renderBindGroup = null;

    // State
    this.nodeCount = 0;
    this.nodes = []; // CPU-side node data for initialization
    this.time = 0;
    this.pumpSpeed = 1.0;

    // Camera
    this.camDist = 6.0;
    this.camTheta = 0.5;
    this.camPhi = 0.4;
    this.camTargetTheta = 0.5;
    this.camTargetPhi = 0.4;
  }

  // --------------------------------------------------------
  // INIT: set up WebGPU device, pipelines, buffers
  // --------------------------------------------------------
  async init(canvas) {
    if (!navigator.gpu) {
      throw new Error('WebGPU not supported');
    }
    const adapter = await navigator.gpu.requestAdapter();
    if (!adapter) {
      throw new Error('No WebGPU adapter found');
    }
    this.device = await adapter.requestDevice();
    this.context = canvas.getContext('webgpu');
    this.format = navigator.gpu.getPreferredCanvasFormat();
    this.canvas = canvas;

    this.context.configure({
      device: this.device,
      format: this.format,
      alphaMode: 'premultiplied',
    });

    this._createBuffers();
    this._createPipelines();

    return this;
  }

  // --------------------------------------------------------
  // CREATE BUFFERS
  // --------------------------------------------------------
  _createBuffers() {
    const dev = this.device;

    // CircNode buffer (read/write for pump, read for LOD)
    this.nodeBuffer = dev.createBuffer({
      size: MAX_NODES * CIRC_NODE_SIZE,
      usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST,
    });

    // Instance buffer (written by LOD compute, read by render)
    // DrawInstance: 3 * vec4f = 48 bytes
    this.instanceBuffer = dev.createBuffer({
      size: MAX_NODES * 48,
      usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST,
    });

    // Indirect draw args (written by LOD compute, read by drawIndirect)
    // 4 * u32 = 16 bytes
    this.indirectBuffer = dev.createBuffer({
      size: 16,
      usage: GPUBufferUsage.STORAGE | GPUBufferUsage.INDIRECT | GPUBufferUsage.COPY_DST,
    });

    // Frame uniforms
    // FrameUniforms: time(4) + dt(4) + pump_speed(4) + node_count(4)
    //   + cam_pos(16) + cam_fwd(16) + cam_up(16) + cam_right(16)
    //   + proj(64) + view(64) = 208 bytes, round to 256
    this.frameUniformBuffer = dev.createBuffer({
      size: 256,
      usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST,
    });

    // Depth texture
    this._createDepthTexture();
  }

  _createDepthTexture() {
    if (this.depthTexture) this.depthTexture.destroy();
    this.depthTexture = this.device.createTexture({
      size: [this.canvas.width, this.canvas.height],
      format: 'depth24plus',
      usage: GPUTextureUsage.RENDER_ATTACHMENT,
    });
  }

  // --------------------------------------------------------
  // CREATE PIPELINES
  // --------------------------------------------------------
  _createPipelines() {
    const dev = this.device;

    // --- PUMP COMPUTE PIPELINE ---
    const pumpModule = dev.createShaderModule({ code: WGSL_PUMP });
    const pumpBGL = dev.createBindGroupLayout({
      entries: [
        { binding: 0, visibility: GPUShaderStage.COMPUTE,
          buffer: { type: 'storage' } },
        { binding: 1, visibility: GPUShaderStage.COMPUTE,
          buffer: { type: 'uniform' } },
      ]
    });
    this.pumpPipeline = dev.createComputePipeline({
      layout: dev.createPipelineLayout({ bindGroupLayouts: [pumpBGL] }),
      compute: { module: pumpModule, entryPoint: 'pump' },
    });
    this.pumpBindGroup = dev.createBindGroup({
      layout: pumpBGL,
      entries: [
        { binding: 0, resource: { buffer: this.nodeBuffer } },
        { binding: 1, resource: { buffer: this.frameUniformBuffer } },
      ]
    });

    // --- LOD COMPUTE PIPELINE ---
    const lodModule = dev.createShaderModule({ code: WGSL_LOD });
    const lodBGL = dev.createBindGroupLayout({
      entries: [
        { binding: 0, visibility: GPUShaderStage.COMPUTE,
          buffer: { type: 'read-only-storage' } },
        { binding: 1, visibility: GPUShaderStage.COMPUTE,
          buffer: { type: 'uniform' } },
        { binding: 2, visibility: GPUShaderStage.COMPUTE,
          buffer: { type: 'storage' } },
        { binding: 3, visibility: GPUShaderStage.COMPUTE,
          buffer: { type: 'storage' } },
      ]
    });
    this.lodPipeline = dev.createComputePipeline({
      layout: dev.createPipelineLayout({ bindGroupLayouts: [lodBGL] }),
      compute: { module: lodModule, entryPoint: 'evaluate' },
    });
    this.lodBindGroup = dev.createBindGroup({
      layout: lodBGL,
      entries: [
        { binding: 0, resource: { buffer: this.nodeBuffer } },
        { binding: 1, resource: { buffer: this.frameUniformBuffer } },
        { binding: 2, resource: { buffer: this.instanceBuffer } },
        { binding: 3, resource: { buffer: this.indirectBuffer } },
      ]
    });

    // --- RENDER PIPELINE ---
    const vertModule = dev.createShaderModule({ code: WGSL_VERTEX });
    const fragModule = dev.createShaderModule({ code: WGSL_FRAGMENT });
    const renderBGL = dev.createBindGroupLayout({
      entries: [
        { binding: 0, visibility: GPUShaderStage.VERTEX,
          buffer: { type: 'uniform' } },
        { binding: 1, visibility: GPUShaderStage.VERTEX,
          buffer: { type: 'read-only-storage' } },
      ]
    });
    this.renderPipeline = dev.createRenderPipeline({
      layout: dev.createPipelineLayout({ bindGroupLayouts: [renderBGL] }),
      vertex: {
        module: vertModule,
        entryPoint: 'vs_main',
      },
      fragment: {
        module: fragModule,
        entryPoint: 'fs_main',
        targets: [{
          format: this.format,
          blend: {
            color: {
              srcFactor: 'src-alpha',
              dstFactor: 'one',
              operation: 'add',
            },
            alpha: {
              srcFactor: 'one',
              dstFactor: 'one',
              operation: 'add',
            },
          },
        }],
      },
      primitive: {
        topology: 'triangle-list',
      },
      depthStencil: {
        format: 'depth24plus',
        depthWriteEnabled: false,  // additive blending, no depth write
        depthCompare: 'less',
      },
    });
    this.renderBindGroup = dev.createBindGroup({
      layout: renderBGL,
      entries: [
        { binding: 0, resource: { buffer: this.frameUniformBuffer } },
        { binding: 1, resource: { buffer: this.instanceBuffer } },
      ]
    });
  }

  // --------------------------------------------------------
  // SCENE API: create circumpunct nodes
  // --------------------------------------------------------

  // Create a single node. Returns its index.
  createNode({ position = [0, 0, 0], scale = 1.0, balance = 0.5,
                phase = 0, dimDepth = 1.5, parent = 0xFFFFFFFF } = {}) {
    const idx = this.nodeCount++;
    this.nodes.push({
      position, scale, balance, phase, dimDepth, parent,
      childStart: 0, childCount: 0, flags: 1,
    });
    return idx;
  }

  // Build a fractal tree: one root with T children per level, nesting depth levels.
  // Returns the root index.
  buildTree({ position = [0, 0, 0], scale = 1.5, balance = 0.5,
              depth = 4, phase = 0 } = {}) {
    const rootIdx = this.createNode({
      position, scale, balance, phase, dimDepth: 3.0, parent: 0xFFFFFFFF
    });

    const buildLevel = (parentIdx, parentPos, parentScale, level) => {
      if (level >= depth) return;

      const childScale = parentScale * PHI_INV;
      const orbitR = parentScale * 0.5;
      const childStart = this.nodeCount;
      let childCount = 0;

      for (let c = 0; c < T; c++) {
        const angle = (c / T) * Math.PI * 2;
        const cx = parentPos[0] + Math.cos(angle) * orbitR;
        const cy = parentPos[1];
        const cz = parentPos[2] + Math.sin(angle) * orbitR;

        // Deeper nodes start at lower dimensional depth
        const d = Math.max(0, 3.0 - level * 0.5);
        // Phase offset: children are phase-shifted by 1/T
        const childPhase = (phase + c / T) % 1.0;

        const childIdx = this.createNode({
          position: [cx, cy, cz],
          scale: childScale,
          balance,
          phase: childPhase,
          dimDepth: d,
          parent: parentIdx,
        });
        childCount++;

        buildLevel(childIdx, [cx, cy, cz], childScale, level + 1);
      }

      // Update parent's child info
      this.nodes[parentIdx].childStart = childStart;
      this.nodes[parentIdx].childCount = childCount;
    };

    buildLevel(rootIdx, position, scale, 0);
    return rootIdx;
  }

  // Upload all nodes to GPU
  uploadNodes() {
    const data = new ArrayBuffer(this.nodeCount * CIRC_NODE_SIZE);
    const f32 = new Float32Array(data);
    const u32 = new Uint32Array(data);

    for (let i = 0; i < this.nodeCount; i++) {
      const n = this.nodes[i];
      const off = i * 16; // 64 bytes / 4 bytes per float = 16 floats

      // position: vec4f
      f32[off + 0] = n.position[0];
      f32[off + 1] = n.position[1];
      f32[off + 2] = n.position[2];
      f32[off + 3] = n.scale;

      // state: vec4f
      f32[off + 4] = n.balance;
      f32[off + 5] = n.phase;
      f32[off + 6] = n.dimDepth;
      f32[off + 7] = 1.0; // visibility (initial)

      // hierarchy: vec4u
      u32[off + 8] = n.parent;
      u32[off + 9] = n.childStart;
      u32[off + 10] = n.childCount;
      u32[off + 11] = n.flags;

      // derived: vec4f (zeroed, compute will fill)
      f32[off + 12] = 0;
      f32[off + 13] = 0;
      f32[off + 14] = 0;
      f32[off + 15] = 0;
    }

    this.device.queue.writeBuffer(this.nodeBuffer, 0, data, 0, this.nodeCount * CIRC_NODE_SIZE);
  }

  // --------------------------------------------------------
  // FRAME: the pump cycle IS the frame
  // --------------------------------------------------------
  pump(dt) {
    this.time += dt;

    // Update camera
    this.camTheta += (this.camTargetTheta - this.camTheta) * 0.06;
    this.camPhi += (this.camTargetPhi - this.camPhi) * 0.06;

    const cx = this.camDist * Math.cos(this.camPhi) * Math.sin(this.camTheta);
    const cy = this.camDist * Math.sin(this.camPhi);
    const cz = this.camDist * Math.cos(this.camPhi) * Math.cos(this.camTheta);

    // View matrix (lookAt)
    const eye = [cx, cy, cz];
    const target = [0, 0, 0];
    const up = [0, 1, 0];
    const viewMat = lookAt(eye, target, up);

    // Projection matrix (framework FOV)
    const aspect = this.canvas.width / this.canvas.height;
    const projMat = perspective(FOV_RAD, aspect, NEAR, FAR);

    // Camera basis vectors
    const fwd = normalize(sub(target, eye));
    const right = normalize(cross(fwd, up));
    const camUp = cross(right, fwd);

    // Write frame uniforms
    const buf = new ArrayBuffer(256);
    const f = new Float32Array(buf);
    const u = new Uint32Array(buf);

    f[0] = this.time;
    f[1] = dt;
    f[2] = this.pumpSpeed;
    u[3] = this.nodeCount;

    // cam_pos (offset 16)
    f[4] = cx; f[5] = cy; f[6] = cz; f[7] = 0;
    // cam_fwd (offset 32)
    f[8] = fwd[0]; f[9] = fwd[1]; f[10] = fwd[2]; f[11] = 0;
    // cam_up (offset 48)
    f[12] = camUp[0]; f[13] = camUp[1]; f[14] = camUp[2]; f[15] = 0;
    // cam_right (offset 64)
    f[16] = right[0]; f[17] = right[1]; f[18] = right[2]; f[19] = 0;

    // proj matrix (offset 80, 16 floats)
    for (let i = 0; i < 16; i++) f[20 + i] = projMat[i];
    // view matrix (offset 144, 16 floats)
    for (let i = 0; i < 16; i++) f[36 + i] = viewMat[i];

    this.device.queue.writeBuffer(this.frameUniformBuffer, 0, buf);

    // Reset indirect draw args: vertex_count=6, instance_count=0
    const indirectReset = new Uint32Array([6, 0, 0, 0]);
    this.device.queue.writeBuffer(this.indirectBuffer, 0, indirectReset);

    // === RECORD COMMAND BUFFER ===
    const encoder = this.device.createCommandEncoder();

    // COMPUTE PASS 1: Pump cycle (⊛ → i → ✹)
    const pumpPass = encoder.beginComputePass();
    pumpPass.setPipeline(this.pumpPipeline);
    pumpPass.setBindGroup(0, this.pumpBindGroup);
    pumpPass.dispatchWorkgroups(Math.ceil(this.nodeCount / 64));
    pumpPass.end();

    // COMPUTE PASS 2: LOD evaluation, visibility, repr selection
    const lodPass = encoder.beginComputePass();
    lodPass.setPipeline(this.lodPipeline);
    lodPass.setBindGroup(0, this.lodBindGroup);
    lodPass.dispatchWorkgroups(Math.ceil(this.nodeCount / 64));
    lodPass.end();

    // RENDER PASS: consume computed instances
    const textureView = this.context.getCurrentTexture().createView();
    const renderPass = encoder.beginRenderPass({
      colorAttachments: [{
        view: textureView,
        clearValue: { r: 0.02, g: 0.015, b: 0.01, a: 1 },
        loadOp: 'clear',
        storeOp: 'store',
      }],
      depthStencilAttachment: {
        view: this.depthTexture.createView(),
        depthClearValue: 1.0,
        depthLoadOp: 'clear',
        depthStoreOp: 'store',
      },
    });
    renderPass.setPipeline(this.renderPipeline);
    renderPass.setBindGroup(0, this.renderBindGroup);
    renderPass.drawIndirect(this.indirectBuffer, 0);
    renderPass.end();

    // Submit
    this.device.queue.submit([encoder.finish()]);
  }

  // --------------------------------------------------------
  // RESIZE
  // --------------------------------------------------------
  resize(width, height) {
    this.canvas.width = width;
    this.canvas.height = height;
    this._createDepthTexture();
  }

  // --------------------------------------------------------
  // DESTROY
  // --------------------------------------------------------
  destroy() {
    if (this.nodeBuffer) this.nodeBuffer.destroy();
    if (this.instanceBuffer) this.instanceBuffer.destroy();
    if (this.indirectBuffer) this.indirectBuffer.destroy();
    if (this.frameUniformBuffer) this.frameUniformBuffer.destroy();
    if (this.depthTexture) this.depthTexture.destroy();
  }
}

// ============================================================
// MATH UTILITIES (minimal, no dependencies)
// ============================================================
function normalize(v) {
  const l = Math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2]);
  return l > 0 ? [v[0]/l, v[1]/l, v[2]/l] : [0, 0, 0];
}
function sub(a, b) { return [a[0]-b[0], a[1]-b[1], a[2]-b[2]]; }
function cross(a, b) {
  return [
    a[1]*b[2] - a[2]*b[1],
    a[2]*b[0] - a[0]*b[2],
    a[0]*b[1] - a[1]*b[0]
  ];
}
function dot(a, b) { return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]; }

function lookAt(eye, target, up) {
  const z = normalize(sub(eye, target));
  const x = normalize(cross(up, z));
  const y = cross(z, x);
  return new Float32Array([
    x[0], y[0], z[0], 0,
    x[1], y[1], z[1], 0,
    x[2], y[2], z[2], 0,
    -dot(x, eye), -dot(y, eye), -dot(z, eye), 1,
  ]);
}

function perspective(fovRad, aspect, near, far) {
  const f = 1.0 / Math.tan(fovRad / 2);
  const nf = 1 / (near - far);
  return new Float32Array([
    f / aspect, 0, 0, 0,
    0, f, 0, 0,
    0, 0, far * nf, -1,
    0, 0, far * near * nf, 0,
  ]);
}

// ============================================================
// EXPORT
// ============================================================
if (typeof window !== 'undefined') {
  window.CircumpunctGPU = CircumpunctGPU;
}
if (typeof module !== 'undefined') {
  module.exports = { CircumpunctGPU };
}
