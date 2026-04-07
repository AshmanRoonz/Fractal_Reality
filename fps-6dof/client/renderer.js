/**
 * LSS (Last Ship Sailing) - Rendering System
 * Ported from single-player game to multiplayer client
 * Self-contained module; attaches to window.LSS_RENDERER
 * Requires: THREE.js r128 loaded via CDN
 */

window.LSS_RENDERER = (function() {
  'use strict';

  // ============================================================================
  // SECTION 1: SDF PRIMITIVE FUNCTIONS
  // ============================================================================

  function sdSphere(px, py, pz, cx, cy, cz, r) {
    const dx = px - cx, dy = py - cy, dz = pz - cz;
    return Math.sqrt(dx*dx + dy*dy + dz*dz) - r;
  }

  function sdCylinder(px, py, pz, ax, ay, az, bx, by, bz, r) {
    const bax = bx - ax, bay = by - ay, baz = bz - az;
    const pax = px - ax, pay = py - ay, paz = pz - az;
    const baLen2 = bax*bax + bay*bay + baz*baz;
    if (baLen2 < 0.001) return sdSphere(px, py, pz, ax, ay, az, r);
    const t = Math.max(0, Math.min(1, (pax*bax + pay*bay + paz*baz) / baLen2));
    const cx2 = ax + bax*t, cy2 = ay + bay*t, cz2 = az + baz*t;
    const dx = px - cx2, dy = py - cy2, dz = pz - cz2;
    const perpDist = Math.sqrt(dx*dx + dy*dy + dz*dz);
    const baLen = Math.sqrt(baLen2);
    const axialFromMid = Math.abs(t - 0.5) * baLen;
    const halfLen = baLen * 0.5;
    const dAxial = axialFromMid - halfLen;
    const dPerp = perpDist - r;
    if (dPerp > 0 && dAxial > 0) return Math.sqrt(dPerp*dPerp + dAxial*dAxial);
    return Math.max(dPerp, dAxial);
  }

  function sdfSmin(a, b, k) {
    if (k <= 0.001) return Math.min(a, b);
    const h = Math.max(0, Math.min(1, 0.5 + 0.5*(b - a) / k));
    return b*(1 - h) + a*h - k*h*(1 - h);
  }

  // ============================================================================
  // SECTION 2: MARCHING CUBES LOOKUP TABLES
  // ============================================================================

  const mcEdgeTable = new Uint16Array([0x0, 0x109, 0x203, 0x30a, 0x406, 0x50f, 0x605, 0x70c, 0x80c, 0x905, 0xa0f, 0xb06, 0xc0a, 0xd03, 0xe09, 0xf00, 0x190, 0x99, 0x393, 0x29a, 0x596, 0x49f, 0x795, 0x69c, 0x99c, 0x895, 0xb9f, 0xa96, 0xd9a, 0xc93, 0xf99, 0xe90, 0x230, 0x339, 0x33, 0x13a, 0x636, 0x73f, 0x435, 0x53c, 0xa3c, 0xb35, 0x83f, 0x936, 0xe3a, 0xf33, 0xc39, 0xd30, 0x3a0, 0x2a9, 0x1a3, 0xaa, 0x7a6, 0x6af, 0x5a5, 0x4ac, 0xbac, 0xaa5, 0x9af, 0x8a6, 0xfaa, 0xea3, 0xda9, 0xca0, 0x460, 0x569, 0x663, 0x76a, 0x66, 0x16f, 0x265, 0x36c, 0xc6c, 0xd65, 0xe6f, 0xf66, 0x86a, 0x963, 0xa69, 0xb60, 0x5f0, 0x4f9, 0x7f3, 0x6fa, 0x1f6, 0xff, 0x3f5, 0x2fc, 0xdfc, 0xcf5, 0xfff, 0xef6, 0x9fa, 0x8f3, 0xbf9, 0xaf0, 0x650, 0x759, 0x453, 0x55a, 0x256, 0x35f, 0x55, 0x15c, 0xe5c, 0xf55, 0xc5f, 0xd56, 0xa5a, 0xb53, 0x859, 0x950, 0x7c0, 0x6c9, 0x5c3, 0x4ca, 0x3c6, 0x2cf, 0x1c5, 0xcc, 0xfcc, 0xec5, 0xdcf, 0xcc6, 0xbca, 0xac3, 0x9c9, 0x8c0, 0x8c0, 0x9c9, 0xac3, 0xbca, 0xcc6, 0xdcf, 0xec5, 0xfcc, 0xcc, 0x1c5, 0x2cf, 0x3c6, 0x4ca, 0x5c3, 0x6c9, 0x7c0, 0x950, 0x859, 0xb53, 0xa5a, 0xd56, 0xc5f, 0xf55, 0xe5c, 0x15c, 0x55, 0x35f, 0x256, 0x55a, 0x453, 0x759, 0x650, 0xaf0, 0xbf9, 0x8f3, 0x9fa, 0xef6, 0xfff, 0xcf5, 0xdfc, 0x2fc, 0x3f5, 0xff, 0x1f6, 0x6fa, 0x7f3, 0x4f9, 0x5f0, 0xb60, 0xa69, 0x963, 0x86a, 0xf66, 0xe6f, 0xd65, 0xc6c, 0x36c, 0x265, 0x16f, 0x66, 0x76a, 0x663, 0x569, 0x460, 0xca0, 0xda9, 0xea3, 0xfaa, 0x8a6, 0x9af, 0xaa5, 0xbac, 0x4ac, 0x5a5, 0x6af, 0x7a6, 0xaa, 0x1a3, 0x2a9, 0x3a0, 0xd30, 0xc39, 0xf33, 0xe3a, 0x936, 0x83f, 0xb35, 0xa3c, 0x53c, 0x435, 0x73f, 0x636, 0x13a, 0x33, 0x339, 0x230, 0xe90, 0xf99, 0xc93, 0xd9a, 0xa96, 0xb9f, 0x895, 0x99c, 0x69c, 0x795, 0x49f, 0x596, 0x29a, 0x393, 0x99, 0x190, 0xf00, 0xe09, 0xd03, 0xc0a, 0xb06, 0xa0f, 0x905, 0x80c, 0x70c, 0x605, 0x50f, 0x406, 0x30a, 0x203, 0x109, 0x0]);

  const mcTriTable = [
    [-1], [0, 8, 3, -1], [0, 1, 9, -1], [1, 8, 3, 9, 8, 1, -1], [1, 2, 10, -1], [0, 8, 3, 1, 2, 10, -1], [9, 2, 10, 0, 2, 9, -1], [2, 8, 3, 2, 10, 8, 10, 9, 8, -1], [3, 11, 2, -1], [0, 11, 2, 8, 11, 0, -1], [1, 9, 0, 2, 3, 11, -1], [1, 11, 2, 1, 9, 11, 9, 8, 11, -1], [3, 10, 1, 11, 10, 3, -1], [0, 10, 1, 0, 8, 10, 8, 11, 10, -1], [3, 9, 0, 3, 11, 9, 11, 10, 9, -1], [9, 8, 10, 10, 8, 11, -1], [4, 7, 8, -1], [4, 3, 0, 7, 3, 4, -1], [0, 1, 9, 8, 4, 7, -1], [4, 1, 9, 4, 7, 1, 7, 3, 1, -1], [1, 2, 10, 8, 4, 7, -1], [3, 4, 7, 3, 0, 4, 1, 2, 10, -1], [9, 2, 10, 9, 0, 2, 8, 4, 7, -1], [2, 10, 9, 2, 9, 7, 2, 7, 3, 7, 9, 4, -1], [8, 4, 7, 3, 11, 2, -1], [11, 4, 7, 11, 2, 4, 2, 0, 4, -1], [9, 0, 1, 8, 4, 7, 2, 3, 11, -1], [4, 7, 11, 9, 4, 11, 9, 11, 2, 9, 2, 1, -1], [3, 10, 1, 3, 11, 10, 7, 8, 4, -1], [1, 11, 10, 1, 4, 11, 1, 0, 4, 7, 11, 4, -1], [4, 7, 8, 9, 0, 11, 9, 11, 10, 11, 0, 3, -1], [4, 7, 11, 4, 11, 9, 9, 11, 10, -1], [9, 5, 4, -1], [9, 5, 4, 0, 8, 3, -1], [0, 5, 4, 1, 5, 0, -1], [8, 5, 4, 8, 3, 5, 3, 1, 5, -1], [1, 2, 10, 9, 5, 4, -1], [3, 0, 8, 1, 2, 10, 4, 9, 5, -1], [5, 2, 10, 5, 4, 2, 4, 0, 2, -1], [2, 10, 5, 3, 2, 5, 3, 5, 4, 3, 4, 8, -1], [9, 5, 4, 2, 3, 11, -1], [0, 11, 2, 0, 8, 11, 4, 9, 5, -1], [0, 5, 4, 0, 1, 5, 2, 3, 11, -1], [2, 1, 5, 2, 5, 8, 2, 8, 11, 4, 8, 5, -1], [10, 3, 11, 10, 1, 3, 9, 5, 4, -1], [4, 9, 5, 0, 8, 1, 8, 10, 1, 8, 11, 10, -1], [5, 4, 0, 5, 0, 11, 5, 11, 10, 11, 0, 3, -1], [5, 4, 8, 5, 8, 10, 10, 8, 11, -1], [9, 7, 8, 5, 7, 9, -1], [9, 3, 0, 9, 5, 3, 5, 7, 3, -1], [0, 7, 8, 0, 1, 7, 1, 5, 7, -1], [1, 5, 3, 3, 5, 7, -1], [9, 7, 8, 9, 5, 7, 10, 1, 2, -1], [10, 1, 0, 10, 0, 7, 10, 7, 5, 7, 0, 3, -1], [8, 0, 2, 8, 2, 5, 8, 5, 7, 10, 5, 2, -1], [2, 10, 5, 2, 5, 3, 3, 5, 7, -1], [7, 9, 5, 7, 8, 9, 3, 11, 2, -1], [9, 5, 7, 9, 7, 2, 9, 2, 0, 2, 7, 11, -1], [2, 3, 11, 0, 1, 8, 1, 7, 8, 1, 5, 7, -1], [11, 2, 1, 11, 1, 7, 7, 1, 5, -1], [9, 5, 8, 8, 5, 7, 10, 1, 3, 10, 3, 11, -1], [5, 7, 0, 5, 0, 9, 7, 11, 0, 1, 0, 10, 11, 10, 0, -1], [11, 10, 0, 11, 0, 3, 10, 5, 0, 8, 0, 7, 5, 7, 0, -1], [11, 10, 5, 7, 11, 5, -1], [10, 6, 5, -1], [0, 8, 3, 5, 10, 6, -1], [9, 0, 1, 5, 10, 6, -1], [1, 8, 3, 1, 9, 8, 5, 10, 6, -1], [1, 6, 5, 2, 6, 1, -1], [1, 6, 5, 1, 2, 6, 3, 0, 8, -1], [9, 6, 5, 9, 0, 6, 0, 2, 6, -1], [5, 9, 8, 5, 8, 2, 5, 2, 6, 3, 2, 8, -1], [2, 3, 11, 10, 6, 5, -1], [11, 0, 8, 11, 2, 0, 10, 6, 5, -1], [0, 1, 9, 2, 3, 11, 5, 10, 6, -1], [5, 10, 6, 1, 9, 2, 9, 11, 2, 9, 8, 11, -1], [6, 3, 11, 6, 5, 3, 5, 1, 3, -1], [0, 8, 11, 0, 11, 5, 0, 5, 1, 5, 11, 6, -1], [3, 11, 6, 0, 3, 6, 0, 6, 5, 0, 5, 9, -1], [6, 5, 9, 6, 9, 11, 11, 9, 8, -1], [5, 10, 6, 4, 7, 8, -1], [4, 3, 0, 4, 7, 3, 6, 5, 10, -1], [1, 9, 0, 5, 10, 6, 8, 4, 7, -1], [10, 6, 5, 1, 9, 7, 1, 7, 3, 7, 9, 4, -1], [6, 1, 2, 6, 5, 1, 4, 7, 8, -1], [1, 2, 5, 5, 2, 6, 3, 0, 4, 3, 4, 7, -1], [8, 4, 7, 9, 0, 5, 0, 6, 5, 0, 2, 6, -1], [7, 3, 9, 7, 9, 4, 3, 2, 9, 5, 9, 6, 2, 6, 9, -1], [3, 11, 2, 7, 8, 4, 10, 6, 5, -1], [5, 10, 6, 4, 7, 2, 4, 2, 0, 2, 7, 11, -1], [0, 1, 9, 4, 7, 8, 2, 3, 11, 5, 10, 6, -1], [9, 2, 1, 9, 11, 2, 9, 4, 11, 7, 11, 4, 5, 10, 6, -1], [8, 4, 7, 3, 11, 5, 3, 5, 1, 5, 11, 6, -1], [5, 1, 11, 5, 11, 6, 1, 0, 11, 7, 11, 4, 0, 4, 11, -1], [0, 5, 9, 0, 6, 5, 0, 3, 6, 11, 6, 3, 8, 4, 7, -1], [6, 5, 9, 6, 9, 11, 4, 7, 9, 7, 11, 9, -1], [10, 4, 9, 6, 4, 10, -1], [4, 10, 6, 4, 9, 10, 0, 8, 3, -1], [10, 0, 1, 10, 6, 0, 6, 4, 0, -1], [8, 3, 1, 8, 1, 6, 8, 6, 4, 6, 1, 10, -1], [1, 4, 9, 1, 2, 4, 2, 6, 4, -1], [3, 0, 8, 1, 2, 9, 2, 4, 9, 2, 6, 4, -1], [0, 2, 4, 4, 2, 6, -1], [8, 3, 2, 8, 2, 4, 4, 2, 6, -1], [10, 4, 9, 10, 6, 4, 11, 2, 3, -1], [0, 8, 2, 2, 8, 11, 4, 9, 10, 4, 10, 6, -1], [3, 11, 2, 0, 1, 6, 0, 6, 4, 6, 1, 10, -1], [6, 4, 1, 6, 1, 10, 4, 8, 1, 2, 1, 11, 8, 11, 1, -1], [9, 6, 4, 9, 3, 6, 9, 1, 3, 11, 6, 3, -1], [8, 11, 1, 8, 1, 0, 11, 6, 1, 9, 1, 4, 6, 4, 1, -1], [3, 11, 6, 3, 6, 0, 0, 6, 4, -1], [6, 4, 8, 11, 6, 8, -1], [7, 10, 6, 7, 8, 10, 8, 9, 10, -1], [0, 7, 3, 0, 10, 7, 0, 9, 10, 6, 7, 10, -1], [10, 6, 7, 1, 10, 7, 1, 7, 8, 1, 8, 0, -1], [10, 6, 7, 10, 7, 1, 1, 7, 3, -1], [1, 2, 6, 1, 6, 8, 1, 8, 9, 8, 6, 7, -1], [2, 6, 9, 2, 9, 1, 6, 7, 9, 0, 9, 3, 7, 3, 9, -1], [7, 8, 0, 7, 0, 6, 6, 0, 2, -1], [7, 3, 2, 6, 7, 2, -1], [2, 3, 11, 10, 6, 8, 10, 8, 9, 8, 6, 7, -1], [2, 0, 7, 2, 7, 11, 0, 9, 7, 6, 7, 10, 9, 10, 7, -1], [1, 8, 0, 1, 7, 8, 1, 10, 7, 6, 7, 10, 2, 3, 11, -1], [11, 2, 1, 11, 1, 7, 10, 6, 1, 6, 7, 1, -1], [8, 9, 6, 8, 6, 7, 9, 1, 6, 11, 6, 3, 1, 3, 6, -1], [0, 9, 1, 11, 6, 7, -1], [7, 8, 0, 7, 0, 6, 3, 11, 0, 11, 6, 0, -1], [7, 11, 6, -1], [7, 6, 11, -1], [3, 0, 8, 11, 7, 6, -1], [0, 1, 9, 11, 7, 6, -1], [8, 1, 9, 8, 3, 1, 11, 7, 6, -1], [10, 1, 2, 6, 11, 7, -1], [1, 2, 10, 3, 0, 8, 6, 11, 7, -1], [2, 9, 0, 2, 10, 9, 6, 11, 7, -1], [6, 11, 7, 2, 10, 3, 10, 8, 3, 10, 9, 8, -1], [7, 2, 3, 6, 2, 7, -1], [7, 0, 8, 7, 6, 0, 6, 2, 0, -1], [2, 7, 6, 2, 3, 7, 0, 1, 9, -1], [1, 6, 2, 1, 8, 6, 1, 9, 8, 8, 7, 6, -1], [10, 7, 6, 10, 1, 7, 1, 3, 7, -1], [10, 7, 6, 1, 7, 10, 1, 8, 7, 1, 0, 8, -1], [0, 3, 7, 0, 7, 10, 0, 10, 9, 6, 10, 7, -1], [7, 6, 10, 7, 10, 8, 8, 10, 9, -1], [6, 8, 4, 11, 8, 6, -1], [3, 6, 11, 3, 0, 6, 0, 4, 6, -1], [8, 6, 11, 8, 4, 6, 9, 0, 1, -1], [9, 4, 6, 9, 6, 3, 9, 3, 1, 11, 3, 6, -1], [6, 8, 4, 6, 11, 8, 2, 10, 1, -1], [1, 2, 10, 3, 0, 11, 0, 6, 11, 0, 4, 6, -1], [4, 11, 8, 4, 6, 11, 0, 2, 9, 2, 10, 9, -1], [10, 9, 3, 10, 3, 2, 9, 4, 3, 11, 3, 6, 4, 6, 3, -1], [8, 2, 3, 8, 4, 2, 4, 6, 2, -1], [0, 4, 2, 4, 6, 2, -1], [1, 9, 0, 2, 3, 4, 2, 4, 6, 4, 3, 8, -1], [1, 9, 4, 1, 4, 2, 2, 4, 6, -1], [8, 1, 3, 8, 6, 1, 8, 4, 6, 6, 10, 1, -1], [10, 1, 0, 10, 0, 6, 6, 0, 4, -1], [4, 6, 3, 4, 3, 8, 6, 10, 3, 0, 3, 9, 10, 9, 3, -1], [10, 9, 4, 6, 10, 4, -1], [4, 9, 5, 7, 6, 11, -1], [0, 8, 3, 4, 9, 5, 11, 7, 6, -1], [5, 0, 1, 5, 4, 0, 7, 6, 11, -1], [11, 7, 6, 8, 3, 4, 3, 5, 4, 3, 1, 5, -1], [9, 5, 4, 10, 1, 2, 7, 6, 11, -1], [6, 11, 7, 1, 2, 10, 0, 8, 3, 4, 9, 5, -1], [7, 6, 11, 5, 4, 10, 4, 2, 10, 4, 0, 2, -1], [3, 4, 8, 3, 5, 4, 3, 2, 5, 10, 5, 2, 11, 7, 6, -1], [7, 2, 3, 7, 6, 2, 5, 4, 9, -1], [9, 5, 4, 0, 8, 6, 0, 6, 2, 6, 8, 7, -1], [3, 6, 2, 3, 7, 6, 1, 5, 0, 5, 4, 0, -1], [6, 2, 8, 6, 8, 7, 2, 1, 8, 4, 8, 5, 1, 5, 8, -1], [9, 5, 4, 10, 1, 6, 1, 7, 6, 1, 3, 7, -1], [1, 6, 10, 1, 7, 6, 1, 0, 7, 8, 7, 0, 9, 5, 4, -1], [4, 0, 10, 4, 10, 5, 0, 3, 10, 6, 10, 7, 3, 7, 10, -1], [7, 6, 10, 7, 10, 8, 5, 4, 10, 4, 8, 10, -1], [6, 9, 5, 6, 11, 9, 11, 8, 9, -1], [3, 6, 11, 0, 6, 3, 0, 5, 6, 0, 9, 5, -1], [0, 11, 8, 0, 5, 11, 0, 1, 5, 5, 6, 11, -1], [6, 11, 3, 6, 3, 5, 5, 3, 1, -1], [1, 2, 10, 9, 5, 11, 9, 11, 8, 11, 5, 6, -1], [0, 11, 3, 0, 6, 11, 0, 9, 6, 5, 6, 9, 1, 2, 10, -1], [11, 8, 5, 11, 5, 6, 8, 0, 5, 10, 5, 2, 0, 2, 5, -1], [6, 11, 3, 6, 3, 5, 2, 10, 3, 10, 5, 3, -1], [5, 8, 9, 5, 2, 8, 5, 6, 2, 3, 8, 2, -1], [9, 5, 6, 9, 6, 0, 0, 6, 2, -1], [1, 5, 8, 1, 8, 0, 5, 6, 8, 3, 8, 2, 6, 2, 8, -1], [1, 5, 6, 2, 1, 6, -1], [1, 3, 6, 1, 6, 10, 3, 8, 6, 5, 6, 9, 8, 9, 6, -1], [10, 1, 0, 10, 0, 6, 9, 5, 0, 5, 6, 0, -1], [0, 3, 8, 5, 6, 10, -1], [10, 5, 6, -1], [11, 5, 10, 7, 5, 11, -1], [11, 5, 10, 11, 7, 5, 8, 3, 0, -1], [5, 11, 7, 5, 10, 11, 1, 9, 0, -1], [10, 7, 5, 10, 11, 7, 9, 8, 1, 8, 3, 1, -1], [11, 1, 2, 11, 7, 1, 7, 5, 1, -1], [0, 8, 3, 1, 2, 7, 1, 7, 5, 7, 2, 11, -1], [9, 7, 5, 9, 2, 7, 9, 0, 2, 2, 11, 7, -1], [7, 5, 2, 7, 2, 11, 5, 9, 2, 3, 2, 8, 9, 8, 2, -1], [2, 5, 10, 2, 3, 5, 3, 7, 5, -1], [8, 2, 0, 8, 5, 2, 8, 7, 5, 10, 2, 5, -1], [9, 0, 1, 5, 10, 3, 5, 3, 7, 3, 10, 2, -1], [9, 8, 2, 9, 2, 1, 8, 7, 2, 10, 2, 5, 7, 5, 2, -1], [1, 3, 5, 3, 7, 5, -1], [0, 8, 7, 0, 7, 1, 1, 7, 5, -1], [9, 0, 3, 9, 3, 5, 5, 3, 7, -1], [9, 8, 7, 5, 9, 7, -1], [5, 8, 4, 5, 10, 8, 10, 11, 8, -1], [5, 0, 4, 5, 11, 0, 5, 10, 11, 11, 3, 0, -1], [0, 1, 9, 8, 4, 10, 8, 10, 11, 10, 4, 5, -1], [10, 11, 4, 10, 4, 5, 11, 3, 4, 9, 4, 1, 3, 1, 4, -1], [2, 5, 1, 2, 8, 5, 2, 11, 8, 4, 5, 8, -1], [0, 4, 11, 0, 11, 3, 4, 5, 11, 2, 11, 1, 5, 1, 11, -1], [0, 2, 5, 0, 5, 9, 2, 11, 5, 4, 5, 8, 11, 8, 5, -1], [9, 4, 5, 2, 11, 3, -1], [2, 5, 10, 3, 5, 2, 3, 4, 5, 3, 8, 4, -1], [5, 10, 2, 5, 2, 4, 4, 2, 0, -1], [3, 10, 2, 3, 5, 10, 3, 8, 5, 4, 5, 8, 0, 1, 9, -1], [5, 10, 2, 5, 2, 4, 1, 9, 2, 9, 4, 2, -1], [8, 4, 5, 8, 5, 3, 3, 5, 1, -1], [0, 4, 5, 1, 0, 5, -1], [8, 4, 5, 8, 5, 3, 9, 0, 5, 0, 3, 5, -1], [9, 4, 5, -1], [4, 11, 7, 4, 9, 11, 9, 10, 11, -1], [0, 8, 3, 4, 9, 7, 9, 11, 7, 9, 10, 11, -1], [1, 10, 11, 1, 11, 4, 1, 4, 0, 7, 4, 11, -1], [3, 1, 4, 3, 4, 8, 1, 10, 4, 7, 4, 11, 10, 11, 4, -1], [4, 11, 7, 9, 11, 4, 9, 2, 11, 9, 1, 2, -1], [9, 7, 4, 9, 11, 7, 9, 1, 11, 2, 11, 1, 0, 8, 3, -1], [11, 7, 4, 11, 4, 2, 2, 4, 0, -1], [11, 7, 4, 11, 4, 2, 8, 3, 4, 3, 2, 4, -1], [2, 9, 10, 2, 7, 9, 2, 3, 7, 7, 4, 9, -1], [9, 10, 7, 9, 7, 4, 10, 2, 7, 8, 7, 0, 2, 0, 7, -1], [3, 7, 10, 3, 10, 2, 7, 4, 10, 1, 10, 0, 4, 0, 10, -1], [1, 10, 2, 8, 7, 4, -1], [4, 9, 1, 4, 1, 7, 7, 1, 3, -1], [4, 9, 1, 4, 1, 7, 0, 8, 1, 8, 7, 1, -1], [4, 0, 3, 7, 4, 3, -1], [4, 8, 7, -1], [9, 10, 8, 10, 11, 8, -1], [3, 0, 9, 3, 9, 11, 11, 9, 10, -1], [0, 1, 10, 0, 10, 8, 8, 10, 11, -1], [3, 1, 10, 11, 3, 10, -1], [1, 2, 11, 1, 11, 9, 9, 11, 8, -1], [3, 0, 9, 3, 9, 11, 1, 2, 9, 2, 11, 9, -1], [0, 2, 11, 8, 0, 11, -1], [3, 2, 11, -1], [2, 3, 8, 2, 8, 10, 10, 8, 9, -1], [9, 10, 2, 0, 9, 2, -1], [2, 3, 8, 2, 8, 10, 0, 1, 8, 1, 10, 8, -1], [1, 10, 2, -1], [1, 3, 8, 9, 1, 8, -1], [0, 9, 1, -1], [0, 3, 8, -1], [-1]
  ];

  const mcEdgeVerts = [
    [0, 1], [1, 2], [2, 3], [3, 0],
    [4, 5], [5, 6], [6, 7], [7, 4],
    [0, 4], [1, 5], [2, 6], [3, 7]
  ];

  // ============================================================================
  // SECTION 3: WALL SHADER SOURCES
  // ============================================================================

  const sdfVertSrc = [
    'varying vec3 vWorldPos;',
    'varying vec3 vNormal;',
    'varying float vAO;',
    'void main() {',
    '  vec4 wp = modelMatrix * vec4(position, 1.0);',
    '  vWorldPos = wp.xyz;',
    '  vNormal = normalize((modelMatrix * vec4(normal, 0.0)).xyz);',
    '  vec3 upVec = vec3(0.0, 1.0, 0.0);',
    '  float normalUpDot = dot(vNormal, upVec);',
    '  float aoFromNormal = 0.85 + normalUpDot * 0.15;',
    '  vAO = clamp(aoFromNormal, 0.7, 1.0);',
    '  gl_Position = projectionMatrix * viewMatrix * wp;',
    '}'
  ].join('\n');

  const sdfFragSrc = [
    'uniform float time;',
    'varying vec3 vWorldPos;',
    'varying vec3 vNormal;',
    'varying float vAO;',
    'uniform vec3 roomCenters[8];',
    'uniform vec3 roomColorsU[8];',
    'uniform float roomRadii[8];',
    'uniform int roomCount;',
    '',
    'float hash(vec2 p) {',
    '  return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);',
    '}',
    'float hash3(vec3 p) {',
    '  return fract(sin(dot(p, vec3(127.1, 311.7, 74.7))) * 43758.5453);',
    '}',
    'float noise(vec2 p) {',
    '  vec2 i = floor(p), f = fract(p);',
    '  f = f * f * (3.0 - 2.0 * f);',
    '  return mix(mix(hash(i), hash(i+vec2(1,0)), f.x), mix(hash(i+vec2(0,1)), hash(i+vec2(1,1)), f.x), f.y);',
    '}',
    'float branches(vec3 wp) {',
    '  float pattern = 0.0;',
    '  float scale = 0.002;',
    '  float weight = 0.7;',
    '  vec2 p = vec2(wp.x + wp.z * 0.7, wp.y);',
    '  for (int i = 0; i < 6; i++) {',
    '    vec2 g = p * scale;',
    '    float n = noise(g * 2.5 + float(i) * 1.3);',
    '    float n2 = noise(g * 4.0 + float(i) * 2.7);',
    '    g.x += sin(g.y * 1.5 + n * 4.0) * 0.4;',
    '    g.y += cos(g.x * 0.8 + n2 * 2.0) * 0.15;',
    '    vec2 f = abs(fract(g) - 0.5);',
    '    float vein = 1.0 - smoothstep(0.0, 0.09, f.x);',
    '    float branch = 1.0 - smoothstep(0.0, 0.14, f.x + f.y * 0.4);',
    '    float cross1 = 1.0 - smoothstep(0.0, 0.10, f.y);',
    '    pattern += (vein * 0.45 + branch * 0.35 + cross1 * 0.2) * weight;',
    '    p = vec2(p.y * 0.7 + p.x * 0.7, -p.x * 0.5 + p.y * 0.85 + n * 40.0);',
    '    scale *= 1.9;',
    '    weight *= 0.50;',
    '  }',
    '  return clamp(pattern, 0.0, 1.0);',
    '}',
    'float panelGrid(vec3 wp) {',
    '  vec3 gridPos = floor(wp / 400.0) * 400.0;',
    '  vec3 localPos = mod(wp, 400.0);',
    '  float gridX = abs(fract(localPos.x / 400.0 + 0.5) - 0.5) < 0.015 ? 1.0 : 0.0;',
    '  float gridY = abs(fract(localPos.y / 400.0 + 0.5) - 0.5) < 0.012 ? 1.0 : 0.0;',
    '  float gridZ = abs(fract(localPos.z / 400.0 + 0.5) - 0.5) < 0.015 ? 1.0 : 0.0;',
    '  return max(gridX, max(gridY, gridZ));',
    '}',
    'float greebles(vec3 wp, float fade) {',
    '  vec3 gp = wp * 0.05;',
    '  float h1 = hash3(floor(gp));',
    '  float h2 = hash3(floor(gp * 3.7) + 0.1);',
    '  float detail = sin(gp.x * 8.0) * sin(gp.y * 7.0) * sin(gp.z * 6.0);',
    '  detail = abs(detail) * 0.5 + 0.5;',
    '  float greeble = detail * 0.3 + (h2 * 0.3);',
    '  return greeble * fade;',
    '}',
    'void main() {',
    '  vec3 base = vec3(0.06, 0.08, 0.12);',
    '  float minD = 99999.0;',
    '  for (int i = 0; i < 8; i++) {',
    '    if (i >= roomCount) break;',
    '    float d = length(vWorldPos - roomCenters[i]);',
    '    if (d < minD) { minD = d; base = roomColorsU[i]; }',
    '  }',
    '  float yNorm = clamp((vWorldPos.y + 2000.0) / 4000.0, 0.0, 1.0);',
    '  float gradientDark = 0.6 + yNorm * 0.4;',
    '  vec3 brightBase = base * 2.5 + vec3(0.03, 0.04, 0.06);',
    '  vec3 gradBase = brightBase * gradientDark;',
    '  float branchPattern = branches(vWorldPos);',
    '  float branchStrength = 0.7 + (1.0 - yNorm) * 0.3;',
    '  branchPattern *= branchStrength;',
    '  float branchPulse = 0.95 + 0.05 * sin(time * 0.3);',
    '  vec3 glow1 = base * 10.0 + vec3(0.05, 0.08, 0.15);',
    '  vec3 glow2 = base * 18.0 + vec3(0.10, 0.15, 0.25);',
    '  vec3 c = gradBase;',
    '  c = mix(c, glow1, branchPattern * 0.6 * branchPulse);',
    '  c = mix(c, glow2, smoothstep(0.25, 0.65, branchPattern) * 0.8 * branchPulse);',
    '  c += (base * 8.0 + vec3(0.04, 0.06, 0.12)) * smoothstep(0.5, 0.9, branchPattern) * branchPulse;',
    '  vec3 vd = normalize(cameraPosition - vWorldPos);',
    '  float diff = max(dot(vNormal, vd), 0.0) * 0.4 + 0.6;',
    '  float fresnelFactor = pow(1.0 - abs(dot(vNormal, vd)), 3.0);',
    '  vec3 rimGlow = vec3(0.1, 0.15, 0.25) * fresnelFactor * 0.6;',
    '  c += rimGlow;',
    '  c *= diff;',
    '  float panelStrength = panelGrid(vWorldPos) * 0.08;',
    '  c *= (1.0 - panelStrength);',
    '  float greebleDistance = 1.0 - clamp(length(cameraPosition - vWorldPos) / 3000.0, 0.0, 1.0);',
    '  float greebleDetail = greebles(vWorldPos, greebleDistance);',
    '  c = mix(c, c * (1.0 - greebleDetail * 0.25), greebleDistance);',
    '  c *= vAO;',
    '  gl_FragColor = vec4(c, 1.0);',
    '}'
  ].join('\n');

  // ============================================================================
  // SECTION 4: MARCHING CUBES GENERATION (SYNCHRONOUS)
  // ============================================================================

  function generateMarchingCubesMesh(bounds, gridRes, levelSpheres, levelCylinders) {
    const nx = gridRes, ny = gridRes, nz = gridRes;
    const dx = (bounds.maxX - bounds.minX) / nx;
    const dy = (bounds.maxY - bounds.minY) / ny;
    const dz = (bounds.maxZ - bounds.minZ) / nz;

    const vals = new Float32Array((nx + 1) * (ny + 1) * (nz + 1));
    const gi = (i, j, k) => i + (nx + 1) * (j + (ny + 1) * k);

    // Evaluate SDF at all grid points
    for (let k = 0; k <= nz; k++) {
      for (let j = 0; j <= ny; j++) {
        for (let i = 0; i <= nx; i++) {
          const x = bounds.minX + i * dx;
          const y = bounds.minY + j * dy;
          const z = bounds.minZ + k * dz;
          vals[gi(i, j, k)] = worldSDF(x, y, z, levelSpheres, levelCylinders);
        }
      }
    }

    // Interpolate point along edge
    function mcInterp(i1, j1, k1, i2, j2, k2) {
      const v1 = vals[gi(i1, j1, k1)], v2 = vals[gi(i2, j2, k2)];
      if (Math.abs(v1) < 0.00001) return [bounds.minX + i1*dx, bounds.minY + j1*dy, bounds.minZ + k1*dz];
      if (Math.abs(v2) < 0.00001) return [bounds.minX + i2*dx, bounds.minY + j2*dy, bounds.minZ + k2*dz];
      if (Math.abs(v1 - v2) < 0.00001) return [bounds.minX + i1*dx, bounds.minY + j1*dy, bounds.minZ + k1*dz];
      const t = v1 / (v1 - v2);
      return [
        bounds.minX + (i1 + t*(i2 - i1)) * dx,
        bounds.minY + (j1 + t*(j2 - j1)) * dy,
        bounds.minZ + (k1 + t*(k2 - k1)) * dz
      ];
    }

    const positions = [];

    // Process each cube
    for (let k = 0; k < nz; k++) {
      for (let j = 0; j < ny; j++) {
        for (let i = 0; i < nx; i++) {
          const v = [
            vals[gi(i, j, k)],
            vals[gi(i+1, j, k)],
            vals[gi(i+1, j+1, k)],
            vals[gi(i, j+1, k)],
            vals[gi(i, j, k+1)],
            vals[gi(i+1, j, k+1)],
            vals[gi(i+1, j+1, k+1)],
            vals[gi(i, j+1, k+1)]
          ];

          let cubeIdx = 0;
          for (let c = 0; c < 8; c++) if (v[c] < 0) cubeIdx |= (1 << c);

          if (mcEdgeTable[cubeIdx] === 0) continue;

          const ci = [i, i+1, i+1, i, i, i+1, i+1, i];
          const cj = [j, j, j+1, j+1, j, j, j+1, j+1];
          const ck = [k, k, k, k, k+1, k+1, k+1, k+1];
          const ev = new Array(12);

          for (let e = 0; e < 12; e++) {
            if (mcEdgeTable[cubeIdx] & (1 << e)) {
              const [a, b] = mcEdgeVerts[e];
              ev[e] = mcInterp(ci[a], cj[a], ck[a], ci[b], cj[b], ck[b]);
            }
          }

          const tris = mcTriTable[cubeIdx];
          for (let t = 0; t < tris.length; t += 3) {
            if (tris[t] === -1) break;
            const a = ev[tris[t]], b = ev[tris[t+1]], c = ev[tris[t+2]];
            if (a && b && c) {
              positions.push(
                a[0], a[1], a[2],
                c[0], c[1], c[2],
                b[0], b[1], b[2]
              );
            }
          }
        }
      }
    }

    return new Float32Array(positions);
  }

  // Evaluate world SDF
  function worldSDF(px, py, pz, levelSpheres, levelCylinders) {
    const sk = 45;

    let d = 99999;
    if (levelSpheres) {
      for (const s of levelSpheres) {
        d = sdfSmin(d, sdSphere(px, py, pz, s.cx, s.cy, s.cz, s.r), sk);
      }
    }

    if (levelCylinders) {
      for (const c of levelCylinders) {
        const cd = sdCylinder(px, py, pz, c.ax, c.ay, c.az, c.bx, c.by, c.bz, c.r);
        d = sdfSmin(d, cd, sk);
      }
    }

    return d;
  }

  // ============================================================================
  // SECTION 5: HELPER FUNCTION TO COMPUTE BOUNDS
  // ============================================================================

  function computeBoundsFromMap(mapData) {
    let minX = Infinity, maxX = -Infinity;
    let minY = Infinity, maxY = -Infinity;
    let minZ = Infinity, maxZ = -Infinity;

    function expandBounds(x, y, z, padding) {
      minX = Math.min(minX, x - padding);
      maxX = Math.max(maxX, x + padding);
      minY = Math.min(minY, y - padding);
      maxY = Math.max(maxY, y + padding);
      minZ = Math.min(minZ, z - padding);
      maxZ = Math.max(maxZ, z + padding);
    }

    if (mapData.rooms) {
      for (const room of mapData.rooms) {
        const padding = (room.radius || 150) * 1.5;
        expandBounds(room.x || 0, room.y || 0, room.z || 0, padding);
      }
    }

    if (mapData.tunnels) {
      for (const tunnel of mapData.tunnels) {
        const padding = (tunnel.radius || 150) * 1.5;
        if (tunnel.points) {
          for (const p of tunnel.points) {
            expandBounds(p.x || 0, p.y || 0, p.z || 0, padding);
          }
        }
      }
    }

    // Ensure reasonable bounds even if no rooms
    if (!isFinite(minX)) {
      minX = -2000; maxX = 2000;
      minY = -1000; maxY = 3000;
      minZ = -2000; maxZ = 2000;
    }

    return { minX, maxX, minY, maxY, minZ, maxZ };
  }

  // ============================================================================
  // SECTION 6: INIT SCENE
  // ============================================================================

  function initScene(containerEl) {
    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x0a0520, 0.000015);

    const camera = new THREE.PerspectiveCamera(90, window.innerWidth / window.innerHeight, 1, 25000);
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setClearColor(0x0a0520);
    renderer.outputEncoding = THREE.sRGBEncoding || 3001;
    containerEl.appendChild(renderer.domElement);

    // Cartoon-style lighting
    const ambientLight = new THREE.AmbientLight(0x445577, 0.8);
    scene.add(ambientLight);

    const dirLight = new THREE.DirectionalLight(0xffeedd, 1.2);
    dirLight.position.set(1000, 3000, 1500);
    scene.add(dirLight);

    const dirLight2 = new THREE.DirectionalLight(0x8888ff, 0.4);
    dirLight2.position.set(-500, -1000, -500);
    scene.add(dirLight2);

    const pointLight = new THREE.PointLight(0x6699ff, 0.5, 12000);
    pointLight.position.set(0, 500, 0);
    scene.add(pointLight);

    const hemiLight = new THREE.HemisphereLight(0x6688cc, 0x224466, 0.6);
    scene.add(hemiLight);

    return { scene, camera, renderer };
  }

  // ============================================================================
  // SECTION 7: INIT POST-FX
  // ============================================================================

  function initPostFX(renderer) {
    const postFX = { enabled: true };

    postFX.rtScene = new THREE.WebGLRenderTarget(
      window.innerWidth * Math.min(window.devicePixelRatio, 2),
      window.innerHeight * Math.min(window.devicePixelRatio, 2),
      { minFilter: THREE.LinearFilter, magFilter: THREE.LinearFilter, format: THREE.RGBAFormat }
    );

    postFX.rtBright = new THREE.WebGLRenderTarget(
      Math.floor(postFX.rtScene.width / 2), Math.floor(postFX.rtScene.height / 2),
      { minFilter: THREE.LinearFilter, magFilter: THREE.LinearFilter, format: THREE.RGBAFormat }
    );
    postFX.rtBlurH = new THREE.WebGLRenderTarget(
      postFX.rtBright.width, postFX.rtBright.height,
      { minFilter: THREE.LinearFilter, magFilter: THREE.LinearFilter, format: THREE.RGBAFormat }
    );
    postFX.rtBlurV = new THREE.WebGLRenderTarget(
      postFX.rtBright.width, postFX.rtBright.height,
      { minFilter: THREE.LinearFilter, magFilter: THREE.LinearFilter, format: THREE.RGBAFormat }
    );

    postFX.quadGeo = new THREE.PlaneGeometry(2, 2);
    postFX.quadCamera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);

    postFX.brightMat = new THREE.ShaderMaterial({
      uniforms: { tDiffuse: { value: null }, threshold: { value: 0.7 } },
      vertexShader: `varying vec2 vUv; void main() { vUv = uv; gl_Position = vec4(position, 1.0); }`,
      fragmentShader: `
        uniform sampler2D tDiffuse;
        uniform float threshold;
        varying vec2 vUv;
        void main() {
          vec4 c = texture2D(tDiffuse, vUv);
          float brightness = dot(c.rgb, vec3(0.2126, 0.7152, 0.0722));
          gl_FragColor = brightness > threshold ? c : vec4(0.0, 0.0, 0.0, 1.0);
        }
      `
    });

    postFX.blurMat = new THREE.ShaderMaterial({
      uniforms: {
        tDiffuse: { value: null },
        direction: { value: new THREE.Vector2(1, 0) },
        resolution: { value: new THREE.Vector2(postFX.rtBright.width, postFX.rtBright.height) }
      },
      vertexShader: `varying vec2 vUv; void main() { vUv = uv; gl_Position = vec4(position, 1.0); }`,
      fragmentShader: `
        uniform sampler2D tDiffuse;
        uniform vec2 direction;
        uniform vec2 resolution;
        varying vec2 vUv;
        void main() {
          vec2 off = direction / resolution;
          vec4 c = vec4(0.0);
          c += texture2D(tDiffuse, vUv - 4.0 * off) * 0.0162;
          c += texture2D(tDiffuse, vUv - 3.0 * off) * 0.0540;
          c += texture2D(tDiffuse, vUv - 2.0 * off) * 0.1216;
          c += texture2D(tDiffuse, vUv - 1.0 * off) * 0.1945;
          c += texture2D(tDiffuse, vUv)              * 0.2270;
          c += texture2D(tDiffuse, vUv + 1.0 * off) * 0.1945;
          c += texture2D(tDiffuse, vUv + 2.0 * off) * 0.1216;
          c += texture2D(tDiffuse, vUv + 3.0 * off) * 0.0540;
          c += texture2D(tDiffuse, vUv + 4.0 * off) * 0.0162;
          gl_FragColor = c;
        }
      `
    });

    postFX.compositeMat = new THREE.ShaderMaterial({
      uniforms: {
        tScene: { value: null },
        tBloom: { value: null },
        bloomStrength: { value: 0.45 },
        vignetteIntensity: { value: 0.35 },
        vignetteSize: { value: 0.45 },
        chromAb: { value: 0.0 },
        time: { value: 0.0 }
      },
      vertexShader: `varying vec2 vUv; void main() { vUv = uv; gl_Position = vec4(position, 1.0); }`,
      fragmentShader: `
        uniform sampler2D tScene;
        uniform sampler2D tBloom;
        uniform float bloomStrength;
        uniform float vignetteIntensity;
        uniform float vignetteSize;
        uniform float chromAb;
        uniform float time;
        varying vec2 vUv;
        void main() {
          vec2 center = vUv - 0.5;
          float dist = length(center);
          float abAmount = chromAb * dist * 0.02;
          vec3 col;
          col.r = texture2D(tScene, vUv + center * abAmount).r;
          col.g = texture2D(tScene, vUv).g;
          col.b = texture2D(tScene, vUv - center * abAmount).b;
          vec3 bloom = texture2D(tBloom, vUv).rgb;
          col += bloom * bloomStrength;
          float vignette = 1.0 - smoothstep(vignetteSize, vignetteSize + 0.55, dist * 1.4);
          col *= mix(1.0, vignette, vignetteIntensity);
          float grain = (fract(sin(dot(vUv * time * 100.0, vec2(12.9898, 78.233))) * 43758.5453) - 0.5) * 0.03;
          col += grain;
          gl_FragColor = vec4(col, 1.0);
        }
      `
    });

    postFX.brightQuad = new THREE.Mesh(postFX.quadGeo, postFX.brightMat);
    postFX.blurQuad = new THREE.Mesh(postFX.quadGeo, postFX.blurMat);
    postFX.compositeQuad = new THREE.Mesh(postFX.quadGeo, postFX.compositeMat);
    postFX.passScene = new THREE.Scene();
    postFX.passScene.add(postFX.brightQuad);

    return postFX;
  }

  // ============================================================================
  // SECTION 8: RENDER POST-FX
  // ============================================================================

  function renderPostFX(postFX, renderer, scene, camera, time, damageAmount) {
    damageAmount = damageAmount || 0;
    postFX.compositeMat.uniforms.chromAb.value = damageAmount * 3.0;
    postFX.compositeMat.uniforms.time.value = time;

    renderer.setRenderTarget(postFX.rtScene);
    renderer.render(scene, camera);

    postFX.brightMat.uniforms.tDiffuse.value = postFX.rtScene.texture;
    postFX.passScene.remove(postFX.blurQuad, postFX.compositeQuad);
    postFX.passScene.add(postFX.brightQuad);
    renderer.setRenderTarget(postFX.rtBright);
    renderer.render(postFX.passScene, postFX.quadCamera);

    postFX.blurMat.uniforms.tDiffuse.value = postFX.rtBright.texture;
    postFX.blurMat.uniforms.direction.value.set(1, 0);
    postFX.passScene.remove(postFX.brightQuad, postFX.compositeQuad);
    postFX.passScene.add(postFX.blurQuad);
    renderer.setRenderTarget(postFX.rtBlurH);
    renderer.render(postFX.passScene, postFX.quadCamera);

    postFX.blurMat.uniforms.tDiffuse.value = postFX.rtBlurH.texture;
    postFX.blurMat.uniforms.direction.value.set(0, 1);
    renderer.setRenderTarget(postFX.rtBlurV);
    renderer.render(postFX.passScene, postFX.quadCamera);

    postFX.compositeMat.uniforms.tScene.value = postFX.rtScene.texture;
    postFX.compositeMat.uniforms.tBloom.value = postFX.rtBlurV.texture;
    postFX.passScene.remove(postFX.brightQuad, postFX.blurQuad);
    postFX.passScene.add(postFX.compositeQuad);
    renderer.setRenderTarget(null);
    renderer.render(postFX.passScene, postFX.quadCamera);
  }

  // ============================================================================
  // SECTION 9: CREATE STARFIELD
  // ============================================================================

  function createStarfield(scene) {
    const geo = new THREE.BufferGeometry();
    const count = 4000;
    const positions = new Float32Array(count * 3);
    const colors = new Float32Array(count * 3);

    const starColors = [
      [1.0, 0.9, 0.7], [0.7, 0.8, 1.0], [1.0, 0.6, 0.8],
      [0.6, 1.0, 0.8], [1.0, 1.0, 0.5], [0.8, 0.7, 1.0]
    ];

    for (let i = 0; i < count; i++) {
      positions[i*3]   = (Math.random() - 0.5) * 20000;
      positions[i*3+1] = (Math.random() - 0.5) * 20000;
      positions[i*3+2] = (Math.random() - 0.5) * 20000;
      const brightness = 0.5 + Math.random() * 0.5;
      const c = starColors[Math.floor(Math.random() * starColors.length)];
      colors[i*3]   = c[0] * brightness;
      colors[i*3+1] = c[1] * brightness;
      colors[i*3+2] = c[2] * brightness;
    }

    geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geo.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    const mat = new THREE.PointsMaterial({ size: 5, vertexColors: true, transparent: true, opacity: 0.9 });
    scene.add(new THREE.Points(geo, mat));
  }

  // ============================================================================
  // SECTION 10: BUILD LEVEL
  // ============================================================================

  function buildLevel(scene, mapData) {
    const bounds = computeBoundsFromMap(mapData);

    // Build SDF geometry from rooms and tunnels
    const levelSpheres = [];
    const levelCylinders = [];

    if (mapData.rooms) {
      for (const room of mapData.rooms) {
        levelSpheres.push({
          cx: room.x || 0,
          cy: room.y || 0,
          cz: room.z || 0,
          r: room.radius || 150
        });
      }
    }

    if (mapData.tunnels) {
      for (const tunnel of mapData.tunnels) {
        if (tunnel.points && tunnel.points.length >= 2) {
          // Multi-segment tunnel; create multiple cylinders
          for (let i = 0; i < tunnel.points.length - 1; i++) {
            const p1 = tunnel.points[i];
            const p2 = tunnel.points[i + 1];
            levelCylinders.push({
              ax: p1.x || 0,
              ay: p1.y || 0,
              az: p1.z || 0,
              bx: p2.x || 0,
              by: p2.y || 0,
              bz: p2.z || 0,
              r: tunnel.radius || 150
            });
          }
        } else {
          // Direct tunnel (straight line between rooms)
          const fromRoom = mapData.rooms && mapData.rooms.find(r => r.id === tunnel.from);
          const toRoom = mapData.rooms && mapData.rooms.find(r => r.id === tunnel.to);
          if (fromRoom && toRoom) {
            levelCylinders.push({
              ax: fromRoom.x || 0,
              ay: fromRoom.y || 0,
              az: fromRoom.z || 0,
              bx: toRoom.x || 0,
              by: toRoom.y || 0,
              bz: toRoom.z || 0,
              r: tunnel.radius || 150
            });
          }
        }
      }
    }

    // Generate marching cubes mesh
    const posArray = generateMarchingCubesMesh(bounds, 96, levelSpheres, levelCylinders);

    // Create geometry and material
    const levelGeo = new THREE.BufferGeometry();
    levelGeo.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
    levelGeo.computeVertexNormals();

    const roomPalette = [
      0x1a3050, 0x3a1010, 0x103a10, 0x351828,
      0x183520, 0x2a2040, 0x1a4030, 0x402020
    ];

    const roomCentersArr = [];
    const roomColorsArr = [];
    const roomRadiiArr = [];

    for (let i = 0; i < 8; i++) {
      if (i < levelSpheres.length) {
        const s = levelSpheres[i];
        roomCentersArr.push(new THREE.Vector3(s.cx, s.cy, s.cz));
        roomColorsArr.push(new THREE.Color(roomPalette[i % roomPalette.length]));
        roomRadiiArr.push(s.r);
      } else {
        roomCentersArr.push(new THREE.Vector3(0, 99999, 0));
        roomColorsArr.push(new THREE.Color(0x000000));
        roomRadiiArr.push(0);
      }
    }

    const sdfMat = new THREE.ShaderMaterial({
      vertexShader: sdfVertSrc,
      fragmentShader: sdfFragSrc,
      side: THREE.DoubleSide,
      uniforms: {
        time: { value: 0 },
        roomCenters: { value: roomCentersArr },
        roomColorsU: { value: roomColorsArr },
        roomRadii: { value: roomRadiiArr },
        roomCount: { value: Math.min(levelSpheres.length, 8) }
      }
    });

    const mesh = new THREE.Mesh(levelGeo, sdfMat);
    scene.add(mesh);

    return mesh;
  }

  // ============================================================================
  // SECTION 11: CREATE SHIP MESH
  // ============================================================================

  function createShipMesh(chassisData, teamColor) {
    const group = new THREE.Group();

    // Map chassis name to hull dimensions
    let w, h, l;
    const name = (chassisData.name || '').toUpperCase();
    if (name.includes('FRIGATE')) {
      w = 10; h = 6; l = 17.5; // scaled
    } else if (name.includes('CORVETTE')) {
      w = 12.5; h = 7.5; l = 20;
    } else {
      // DREADNOUGHT
      w = 17.5; h = 10; l = 27.5;
    }

    const hullMat = new THREE.MeshPhongMaterial({ color: teamColor, specular: 0x444444, shininess: 60 });
    const darkMat = new THREE.MeshPhongMaterial({ color: 0x222233, specular: 0x222222, shininess: 40 });
    const accentMat = new THREE.MeshPhongMaterial({ color: new THREE.Color(teamColor).offsetHSL(0, 0, -0.15), specular: 0x666666, shininess: 80 });
    const cockpitMat = new THREE.MeshPhongMaterial({ color: 0x1a3355, specular: 0x88bbff, shininess: 120, emissive: 0x0a1a33, emissiveIntensity: 0.4 });
    const engineGlowMat = new THREE.MeshBasicMaterial({
      color: teamColor, transparent: true, opacity: 0.85, blending: THREE.AdditiveBlending
    });
    const thrusterMat = new THREE.MeshBasicMaterial({
      color: 0x44ddff, transparent: true, opacity: 0.7, blending: THREE.AdditiveBlending
    });
    const outlineMat = new THREE.LineBasicMaterial({ color: 0x000000, linewidth: 2 });

    function addPart(geo, mat, pos, rot) {
      const mesh = new THREE.Mesh(geo, mat);
      if (pos) mesh.position.set(pos[0], pos[1], pos[2]);
      if (rot) mesh.rotation.set(rot[0], rot[1], rot[2]);
      group.add(mesh);
      const outline = new THREE.LineSegments(new THREE.EdgesGeometry(geo, 20), outlineMat);
      if (pos) outline.position.set(pos[0], pos[1], pos[2]);
      if (rot) outline.rotation.set(rot[0], rot[1], rot[2]);
      group.add(outline);
      return mesh;
    }

    let engineMesh;

    if (name.includes('FRIGATE')) {
      const noseGeo = new THREE.ConeGeometry(w * 0.6, l * 1.2, 4);
      noseGeo.rotateX(Math.PI / 2);
      addPart(noseGeo, hullMat, [0, 0, -l * 0.3]);

      const midGeo = new THREE.BoxGeometry(w * 1.2, h * 1.0, l * 1.4);
      addPart(midGeo, hullMat, [0, 0, l * 0.3]);

      const canopyGeo = new THREE.BoxGeometry(w * 0.5, h * 0.5, l * 0.5);
      addPart(canopyGeo, cockpitMat, [0, h * 0.55, -l * 0.2]);

      const wingGeo = new THREE.BoxGeometry(w * 2.0, h * 0.12, l * 1.0);
      const wingL = addPart(wingGeo, accentMat, [-w * 1.1, 0, l * 0.3]);
      wingL.rotation.z = -0.12;
      const wingR = addPart(wingGeo, accentMat, [w * 1.1, 0, l * 0.3]);
      wingR.rotation.z = 0.12;

      const tipGeo = new THREE.BoxGeometry(w * 0.15, h * 0.8, l * 0.4);
      addPart(tipGeo, darkMat, [-w * 2.0, h * 0.2, l * 0.5]);
      addPart(tipGeo, darkMat, [w * 2.0, h * 0.2, l * 0.5]);

      const podGeo = new THREE.CylinderGeometry(h * 0.35, h * 0.45, l * 0.6, 6);
      podGeo.rotateX(Math.PI / 2);
      addPart(podGeo, darkMat, [-w * 0.5, -h * 0.15, l * 0.9]);
      addPart(podGeo, darkMat, [w * 0.5, -h * 0.15, l * 0.9]);

      const glowGeo = new THREE.CircleGeometry(h * 0.35, 8);
      const glow1 = new THREE.Mesh(glowGeo, engineGlowMat);
      glow1.position.set(-w * 0.5, -h * 0.15, l * 1.2);
      group.add(glow1);
      const glow2 = new THREE.Mesh(glowGeo, engineGlowMat);
      glow2.position.set(w * 0.5, -h * 0.15, l * 1.2);
      group.add(glow2);

      engineMesh = glow1;

    } else if (name.includes('CORVETTE')) {
      const bodyGeo = new THREE.BoxGeometry(w * 1.6, h * 1.4, l * 2.0);
      addPart(bodyGeo, hullMat, [0, 0, 0]);

      const prowGeo = new THREE.BoxGeometry(w * 1.4, h * 1.0, l * 0.5);
      const prow = addPart(prowGeo, accentMat, [0, h * 0.1, -l * 1.1]);
      prow.rotation.x = 0.15;

      const bridgeGeo = new THREE.BoxGeometry(w * 0.9, h * 0.7, l * 0.7);
      addPart(bridgeGeo, cockpitMat, [0, h * 0.9, -l * 0.1]);

      const armorGeo = new THREE.BoxGeometry(w * 0.5, h * 1.2, l * 1.0);
      addPart(armorGeo, darkMat, [-w * 0.95, h * 0.1, l * 0.1]);
      addPart(armorGeo, darkMat, [w * 0.95, h * 0.1, l * 0.1]);

      const barrelGeo = new THREE.CylinderGeometry(h * 0.12, h * 0.12, l * 0.5, 6);
      barrelGeo.rotateX(Math.PI / 2);
      addPart(barrelGeo, darkMat, [-w * 0.95, h * 0.5, -l * 0.7]);
      addPart(barrelGeo, darkMat, [w * 0.95, h * 0.5, -l * 0.7]);

      const engineBlockGeo = new THREE.BoxGeometry(w * 1.2, h * 0.8, l * 0.4);
      addPart(engineBlockGeo, darkMat, [0, 0, l * 1.1]);

      const glowGeo = new THREE.CircleGeometry(h * 0.6, 8);
      engineMesh = new THREE.Mesh(glowGeo, engineGlowMat);
      engineMesh.position.set(0, 0, l * 1.3);
      group.add(engineMesh);

      const thrGeo = new THREE.CircleGeometry(h * 0.12, 6);
      [-1, 1].forEach(sx => [-1, 1].forEach(sy => {
        const thr = new THREE.Mesh(thrGeo, thrusterMat);
        thr.position.set(sx * w * 0.7, sy * h * 0.5, l * 1.0);
        group.add(thr);
      }));

    } else {
      // DREADNOUGHT
      const coreGeo = new THREE.BoxGeometry(w * 2.0, h * 1.6, l * 2.2);
      addPart(coreGeo, hullMat, [0, 0, 0]);

      const deckGeo = new THREE.BoxGeometry(w * 2.2, h * 0.3, l * 1.8);
      addPart(deckGeo, accentMat, [0, h * 0.9, 0]);
      addPart(deckGeo, accentMat, [0, -h * 0.9, 0]);

      const ramGeo = new THREE.BoxGeometry(w * 1.6, h * 1.0, l * 0.8);
      const ram = addPart(ramGeo, darkMat, [0, 0, -l * 1.3]);
      ram.rotation.x = 0.1;

      const towerGeo = new THREE.BoxGeometry(w * 0.8, h * 1.0, l * 0.5);
      addPart(towerGeo, cockpitMat, [0, h * 1.3, -l * 0.3]);

      const blisterGeo = new THREE.BoxGeometry(w * 0.6, h * 0.9, l * 1.4);
      addPart(blisterGeo, darkMat, [-w * 1.2, 0, l * 0.1]);
      addPart(blisterGeo, darkMat, [w * 1.2, 0, l * 0.1]);

      const heavyBarrelGeo = new THREE.CylinderGeometry(h * 0.15, h * 0.18, l * 0.8, 6);
      heavyBarrelGeo.rotateX(Math.PI / 2);
      addPart(heavyBarrelGeo, darkMat, [-w * 1.2, h * 0.2, -l * 0.8]);
      addPart(heavyBarrelGeo, darkMat, [w * 1.2, h * 0.2, -l * 0.8]);
      addPart(heavyBarrelGeo, darkMat, [0, h * 1.6, -l * 0.6]);

      const engineBankGeo = new THREE.BoxGeometry(w * 1.8, h * 1.2, l * 0.3);
      addPart(engineBankGeo, darkMat, [0, 0, l * 1.2]);

      const bigGlowGeo = new THREE.CircleGeometry(h * 0.35, 8);
      [-1, 0, 1].forEach(i => {
        const g = new THREE.Mesh(bigGlowGeo, engineGlowMat);
        g.position.set(i * w * 0.5, 0, l * 1.35);
        group.add(g);
      });

      const smGlowGeo = new THREE.CircleGeometry(h * 0.15, 6);
      [-1.5, -0.5, 0.5, 1.5].forEach(i => {
        const g = new THREE.Mesh(smGlowGeo, thrusterMat);
        g.position.set(i * w * 0.35, h * 0.5, l * 1.2);
        group.add(g);
      });

      engineMesh = group.children[group.children.length - 5];
    }

    const shieldGeo = new THREE.SphereGeometry(Math.max(w, l) * 2, 16, 12);
    const shieldMat = new THREE.MeshBasicMaterial({ color: 0x44ccff, transparent: true, opacity: 0, side: THREE.DoubleSide });
    const shield = new THREE.Mesh(shieldGeo, shieldMat);
    shield.name = 'shield';
    group.add(shield);

    const engineGlows = [];
    group.traverse(child => {
      if (child.material === engineGlowMat || child.material === thrusterMat) engineGlows.push(child);
    });

    const barrelMeshes = [];
    group.traverse(child => {
      if (child.geometry && child.geometry.type === 'CylinderGeometry' && child.material === darkMat) {
        barrelMeshes.push(child);
      }
    });

    group.userData = { engineMesh, shieldMesh: shield, engineGlows, barrelMeshes, engineGlowMat, thrusterMat };
    return group;
  }

  // ============================================================================
  // SECTION 12: ANIMATE SHIP MESH
  // ============================================================================

  function animateShipMesh(mesh, speed, maxSpeed, isFiring, dt, time) {
    if (!mesh || !mesh.userData) return;

    const t = Math.min(1, speed / maxSpeed);

    if (mesh.userData.engineGlows) {
      for (const glow of mesh.userData.engineGlows) {
        const baseOp = 0.3 + t * 0.6;
        const pulse = Math.sin(time * 12 + Math.random() * 0.1) * 0.08 * t;
        glow.material.opacity = baseOp + pulse;
        const baseScale = 0.6 + t * 0.8;
        const flicker = 1 + Math.sin(time * 18) * 0.05 * t;
        glow.scale.setScalar(baseScale * flicker);
      }
    }

    if (mesh.userData.barrelMeshes && isFiring) {
      for (const barrel of mesh.userData.barrelMeshes) {
        if (!barrel.userData.recoil) barrel.userData.recoil = 0;
        barrel.userData.recoil = 1.0;
      }
    }

    if (mesh.userData.barrelMeshes) {
      for (const barrel of mesh.userData.barrelMeshes) {
        if (barrel.userData.recoil > 0) {
          barrel.userData.recoil -= dt * 8;
          if (barrel.userData.recoil < 0) barrel.userData.recoil = 0;
          if (barrel.userData.originalZ === undefined) barrel.userData.originalZ = barrel.position.z;
          barrel.position.z = barrel.userData.originalZ + barrel.userData.recoil * 3;
          if (barrel.material.emissive) {
            barrel.material.emissive.setHex(barrel.userData.recoil > 0.5 ? 0xff8800 : 0x000000);
            barrel.material.emissiveIntensity = barrel.userData.recoil;
          }
        }
      }
    }
  }

  // ============================================================================
  // PUBLIC API
  // ============================================================================

  return {
    initScene,
    initPostFX,
    renderPostFX,
    createStarfield,
    buildLevel,
    createShipMesh,
    animateShipMesh
  };
})();
