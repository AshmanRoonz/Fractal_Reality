// TEST 1: EXTENDED PATH LENGTH SIMULATION
// Fractal Reality Framework - Worldline Fractal Dimension Analysis
// Tests: D ≈ 1.5 prediction across different spacetime metrics

// Metric definitions
const METRICS = {
  flat: {
    name: "Flat (Minkowski)",
    g_tt: (r) => -1.0,
    g_rr: (r) => 1.0
  },
  weak: {
    name: "Weak Gravitational Field",
    g_tt: (r) => -(1 - 5/r),  // rs = 5 in natural units
    g_rr: (r) => 1/(1 - 5/r)
  },
  neutron: {
    name: "Neutron Star Surface",
    g_tt: (r) => -(1 - 15/r),  // rs = 15
    g_rr: (r) => 1/(1 - 15/r)
  },
  horizon: {
    name: "Near Black Hole Horizon",
    g_tt: (r) => -(1 - 25/r),  // rs = 25, closer to horizon
    g_rr: (r) => 1/(1 - 25/r)
  }
};

// Simulation parameters
const CONFIG = {
  iterations: 10000,
  gridSize: 200,
  periodicBoundary: true,
  centerPosition: 100,
  stepSize: 1.0
};

// Box-counting algorithm for fractal dimension
function calculateFractalDimension(path, scales) {
  const results = [];
  
  for (const epsilon of scales) {
    // Count boxes needed to cover path at scale epsilon
    const boxes = new Set();
    
    for (const [x, t] of path) {
      const boxX = Math.floor(x / epsilon);
      const boxT = Math.floor(t / epsilon);
      boxes.add(`${boxX},${boxT}`);
    }
    
    results.push({
      epsilon: epsilon,
      count: boxes.size,
      logEpsilon: Math.log(1/epsilon),
      logCount: Math.log(boxes.size)
    });
  }
  
  // Linear regression: log(N) vs log(1/ε)
  const n = results.length;
  const sumX = results.reduce((s, r) => s + r.logEpsilon, 0);
  const sumY = results.reduce((s, r) => s + r.logCount, 0);
  const sumXY = results.reduce((s, r) => s + r.logEpsilon * r.logCount, 0);
  const sumX2 = results.reduce((s, r) => s + r.logEpsilon * r.logEpsilon, 0);
  
  const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
  const intercept = (sumY - slope * sumX) / n;
  
  // R² calculation
  const meanY = sumY / n;
  const ssTotal = results.reduce((s, r) => s + Math.pow(r.logCount - meanY, 2), 0);
  const ssResidual = results.reduce((s, r) => {
    const predicted = slope * r.logEpsilon + intercept;
    return s + Math.pow(r.logCount - predicted, 2);
  }, 0);
  const rSquared = 1 - (ssResidual / ssTotal);
  
  return { dimension: slope, rSquared, results };
}

// Random walk with metric-dependent validation
function runSimulation(metricType) {
  const metric = METRICS[metricType];
  const path = [];
  let position = CONFIG.centerPosition;
  let textureAccumulated = 0;
  let validations = 0;
  
  for (let step = 0; step < CONFIG.iterations; step++) {
    // Calculate distance from "gravitational source"
    const r = Math.abs(position - CONFIG.centerPosition) + 20;
    const g_tt = metric.g_tt(r);
    
    // Validation rate depends on metric
    const validationProb = Math.sqrt(Math.abs(g_tt));
    
    if (Math.random() < validationProb) {
      validations++;
      
      // Random walk step
      const dx = (Math.random() - 0.5) * 2 * CONFIG.stepSize;
      position += dx;
      
      // Periodic boundary conditions
      if (CONFIG.periodicBoundary) {
        if (position < 0) position += CONFIG.gridSize;
        if (position >= CONFIG.gridSize) position -= CONFIG.gridSize;
      }
      
      // Accumulate texture
      textureAccumulated += validationProb;
      
      // Record path point
      path.push([position, step]);
    }
  }
  
  return {
    path,
    textureAccumulated,
    validations,
    pathLength: path.length
  };
}

// Main execution
function runTest1() {
  console.log("=".repeat(80));
  console.log("TEST 1: EXTENDED PATH LENGTH - FRACTAL DIMENSION ANALYSIS");
  console.log("=".repeat(80));
  console.log(`\nIterations: ${CONFIG.iterations}`);
  console.log(`Grid size: ${CONFIG.gridSize}`);
  console.log(`Periodic boundaries: ${CONFIG.periodicBoundary}\n`);
  
  // Box-counting scales (15 logarithmically-spaced)
  const scales = [];
  for (let i = 0; i < 15; i++) {
    scales.push(Math.pow(2, i + 1));
  }
  
  const results = {};
  
  for (const metricType of Object.keys(METRICS)) {
    console.log(`\n${"=".repeat(60)}`);
    console.log(`METRIC: ${METRICS[metricType].name}`);
    console.log("=".repeat(60));
    
    const sim = runSimulation(metricType);
    const fractal = calculateFractalDimension(sim.path, scales);
    
    results[metricType] = {
      ...sim,
      fractalDimension: fractal.dimension,
      rSquared: fractal.rSquared
    };
    
    console.log(`\nSimulation Results:`);
    console.log(`  Validations: ${sim.validations}`);
    console.log(`  Path length: ${sim.pathLength}`);
    console.log(`  Texture accumulated: ${sim.textureAccumulated.toFixed(2)}`);
    console.log(`\nFractal Analysis:`);
    console.log(`  Measured dimension D = ${fractal.dimension.toFixed(4)}`);
    console.log(`  R² fit quality = ${fractal.rSquared.toFixed(6)}`);
    console.log(`  (Expected D ≈ 1.5 in flat spacetime)`);
  }
  
  // Summary table
  console.log("\n" + "=".repeat(80));
  console.log("SUMMARY TABLE");
  console.log("=".repeat(80));
  console.log("\n| Metric      | Iterations | Measured D | Texture  | Path Length |");
  console.log("|-------------|------------|------------|----------|-------------|");
  
  for (const [type, data] of Object.entries(results)) {
    console.log(`| ${METRICS[type].name.padEnd(11)} | ${CONFIG.iterations.toString().padEnd(10)} | ${data.fractalDimension.toFixed(4).padEnd(10)} | ${data.textureAccumulated.toFixed(2).padEnd(8)} | ${data.pathLength.toString().padEnd(11)} |`);
  }
  
  console.log("\n" + "=".repeat(80));
  console.log("TEST 1 COMPLETE");
  console.log("=".repeat(80));
  
  return results;
}

// Export for Node.js or run directly
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { runTest1, METRICS, CONFIG };
} else {
  // Browser execution
  const results = runTest1();
  console.log("\nResults object available as 'results' in console");
}
