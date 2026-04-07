/**
 * LSS (Last Ship Sailing) - Physics Math Utilities
 * Shared between Node.js server and browser client.
 * Pure functions for 3D math, quaternions, and collision detection.
 * No external dependencies.
 */

// Vec3 Helpers: 3D vectors represented as { x, y, z }

const vec3 = {
  /**
   * add(v1, v2): returns new vector v1 + v2
   */
  add(v1, v2) {
    return {
      x: v1.x + v2.x,
      y: v1.y + v2.y,
      z: v1.z + v2.z,
    };
  },

  /**
   * sub(v1, v2): returns new vector v1 - v2
   */
  sub(v1, v2) {
    return {
      x: v1.x - v2.x,
      y: v1.y - v2.y,
      z: v1.z - v2.z,
    };
  },

  /**
   * scale(v, scalar): returns new vector v * scalar
   */
  scale(v, scalar) {
    return {
      x: v.x * scalar,
      y: v.y * scalar,
      z: v.z * scalar,
    };
  },

  /**
   * dot(v1, v2): returns scalar dot product
   */
  dot(v1, v2) {
    return v1.x * v2.x + v1.y * v2.y + v1.z * v2.z;
  },

  /**
   * cross(v1, v2): returns new vector v1 x v2 (cross product)
   */
  cross(v1, v2) {
    return {
      x: v1.y * v2.z - v1.z * v2.y,
      y: v1.z * v2.x - v1.x * v2.z,
      z: v1.x * v2.y - v1.y * v2.x,
    };
  },

  /**
   * length(v): returns scalar length (magnitude)
   */
  length(v) {
    return Math.sqrt(v.x * v.x + v.y * v.y + v.z * v.z);
  },

  /**
   * normalize(v): returns new unit vector in direction of v
   * Returns { x: 0, y: 0, z: 0 } if v is zero-length
   */
  normalize(v) {
    const len = vec3.length(v);
    if (len < 1e-6) {
      return { x: 0, y: 0, z: 0 };
    }
    return vec3.scale(v, 1 / len);
  },

  /**
   * lerp(v1, v2, t): linear interpolation (0 <= t <= 1)
   */
  lerp(v1, v2, t) {
    return {
      x: v1.x + (v2.x - v1.x) * t,
      y: v1.y + (v2.y - v1.y) * t,
      z: v1.z + (v2.z - v1.z) * t,
    };
  },

  /**
   * distanceSq(v1, v2): returns squared distance (faster than distance)
   */
  distanceSq(v1, v2) {
    const dx = v2.x - v1.x;
    const dy = v2.y - v1.y;
    const dz = v2.z - v1.z;
    return dx * dx + dy * dy + dz * dz;
  },

  /**
   * distance(v1, v2): returns distance
   */
  distance(v1, v2) {
    return Math.sqrt(vec3.distanceSq(v1, v2));
  },
};

// Quaternion Helpers: unit quaternions represented as { x, y, z, w }

const quat = {
  /**
   * multiply(q1, q2): returns new quaternion q1 * q2 (composition)
   * Order matters: rotation q2 applied first, then q1
   */
  multiply(q1, q2) {
    const x1 = q1.x, y1 = q1.y, z1 = q1.z, w1 = q1.w;
    const x2 = q2.x, y2 = q2.y, z2 = q2.z, w2 = q2.w;

    return {
      x: w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
      y: w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
      z: w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2,
      w: w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
    };
  },

  /**
   * normalize(q): returns new unit quaternion
   */
  normalize(q) {
    const len = Math.sqrt(q.x * q.x + q.y * q.y + q.z * q.z + q.w * q.w);
    if (len < 1e-6) {
      return { x: 0, y: 0, z: 0, w: 1 }; // Identity quaternion
    }
    return {
      x: q.x / len,
      y: q.y / len,
      z: q.z / len,
      w: q.w / len,
    };
  },

  /**
   * conjugate(q): returns new quaternion q*
   * For unit quaternions, conjugate equals inverse
   */
  conjugate(q) {
    return {
      x: -q.x,
      y: -q.y,
      z: -q.z,
      w: q.w,
    };
  },

  /**
   * fromAxisAngle(axis, angleRadians): returns new quaternion
   * axis: { x, y, z } unit vector
   * angleRadians: scalar rotation angle
   */
  fromAxisAngle(axis, angleRadians) {
    const half = angleRadians * 0.5;
    const sinHalf = Math.sin(half);
    return {
      x: axis.x * sinHalf,
      y: axis.y * sinHalf,
      z: axis.z * sinHalf,
      w: Math.cos(half),
    };
  },

  /**
   * fromAngularVelocity(angVel, dt): returns new quaternion dq
   * Converts angular velocity { x, y, z } to rotation over time dt
   */
  fromAngularVelocity(angVel, dt) {
    const angle = vec3.length(angVel) * dt;
    if (angle < 1e-6) {
      return { x: 0, y: 0, z: 0, w: 1 };
    }
    const axis = vec3.normalize(angVel);
    return quat.fromAxisAngle(axis, angle);
  },

  /**
   * rotateVector(q, v): returns new vector q*v*q^-1
   * Rotates vector v by quaternion q
   */
  rotateVector(q, v) {
    // Convert vector to quaternion form: (v.x, v.y, v.z, 0)
    // Result = q * v_quat * q*
    const qV = { x: v.x, y: v.y, z: v.z, w: 0 };
    const qConj = quat.conjugate(q);
    const result = quat.multiply(quat.multiply(q, qV), qConj);
    return { x: result.x, y: result.y, z: result.z };
  },

  /**
   * slerp(q1, q2, t): spherical linear interpolation (0 <= t <= 1)
   * Smoothly interpolates between two rotations
   */
  slerp(q1, q2, t) {
    let dot = q1.x * q2.x + q1.y * q2.y + q1.z * q2.z + q1.w * q2.w;

    // If dot < 0, negate one quaternion to take shorter path
    let qb = q2;
    if (dot < 0) {
      dot = -dot;
      qb = { x: -q2.x, y: -q2.y, z: -q2.z, w: -q2.w };
    }

    // Clamp dot to avoid numerical issues with acos
    dot = Math.max(-1, Math.min(1, dot));

    const theta0 = Math.acos(dot);
    const sinTheta0 = Math.sin(theta0);

    if (sinTheta0 < 1e-6) {
      // Quaternions are very close; use linear interpolation
      return {
        x: q1.x + (qb.x - q1.x) * t,
        y: q1.y + (qb.y - q1.y) * t,
        z: q1.z + (qb.z - q1.z) * t,
        w: q1.w + (qb.w - q1.w) * t,
      };
    }

    const w0 = Math.sin((1 - t) * theta0) / sinTheta0;
    const w1 = Math.sin(t * theta0) / sinTheta0;

    return {
      x: w0 * q1.x + w1 * qb.x,
      y: w0 * q1.y + w1 * qb.y,
      z: w0 * q1.z + w1 * qb.z,
      w: w0 * q1.w + w1 * qb.w,
    };
  },

  /**
   * identity(): returns identity quaternion { x: 0, y: 0, z: 0, w: 1 }
   */
  identity() {
    return { x: 0, y: 0, z: 0, w: 1 };
  },
};

// Physics Integration

/**
 * integratePosition(pos, vel, dt): returns new position
 * Simple Euler integration: pos' = pos + vel * dt
 */
function integratePosition(pos, vel, dt) {
  return vec3.add(pos, vec3.scale(vel, dt));
}

/**
 * integrateRotation(quat, angVel, dt): returns new quaternion
 * Updates rotation: q' = q * dq where dq is rotation over time dt
 */
function integrateRotation(q, angVel, dt) {
  const dq = quat.fromAngularVelocity(angVel, dt);
  return quat.multiply(q, dq);
}

/**
 * applyDrag(vel, drag): returns new velocity with drag applied
 * vel' = vel * (1 - drag * dt)
 * drag: typically [0, 1] (0 = no drag, 1 = full stop per second)
 */
function applyDrag(vel, drag) {
  const dragFactor = Math.max(0, 1 - drag);
  return vec3.scale(vel, dragFactor);
}

// Collision Detection

/**
 * sphereVsSphere(p1, r1, p2, r2): returns { colliding: bool, normal: {x,y,z} }
 * p1, p2: { x, y, z } centers
 * r1, r2: scalars radii
 * normal: unit vector from p1 toward p2 (if colliding)
 */
function sphereVsSphere(p1, r1, p2, r2) {
  const diff = vec3.sub(p2, p1);
  const distSq = vec3.distanceSq(p1, p2);
  const minDist = r1 + r2;

  if (distSq < minDist * minDist) {
    const dist = Math.sqrt(distSq);
    const normal = dist > 1e-6 ? vec3.scale(diff, 1 / dist) : { x: 1, y: 0, z: 0 };
    return { colliding: true, normal };
  }

  return { colliding: false, normal: { x: 0, y: 0, z: 0 } };
}

/**
 * raySphere(origin, dir, center, radius): returns { hit: bool, t: scalar, normal: {x,y,z} }
 * origin, dir: { x, y, z }
 * center, radius: sphere
 * t: distance along ray to hit point (if hit)
 * normal: surface normal at hit point (pointing away from center)
 */
function raySphere(origin, dir, center, radius) {
  const oc = vec3.sub(origin, center);
  const a = vec3.dot(dir, dir);
  const b = 2.0 * vec3.dot(oc, dir);
  const c = vec3.dot(oc, oc) - radius * radius;
  const discriminant = b * b - 4 * a * c;

  if (discriminant < 0) {
    return { hit: false, t: -1, normal: { x: 0, y: 0, z: 0 } };
  }

  const sqrtDisc = Math.sqrt(discriminant);
  const t0 = (-b - sqrtDisc) / (2 * a);
  const t1 = (-b + sqrtDisc) / (2 * a);
  const t = t0 >= 0 ? t0 : (t1 >= 0 ? t1 : -1);

  if (t < 0) {
    return { hit: false, t: -1, normal: { x: 0, y: 0, z: 0 } };
  }

  const hitPoint = vec3.add(origin, vec3.scale(dir, t));
  const normal = vec3.normalize(vec3.sub(hitPoint, center));

  return { hit: true, t, normal };
}

/**
 * pointInCylinder(point, a, b, radius): returns bool
 * Checks if point is inside infinite cylinder with axis from a to b
 * a, b, point: { x, y, z }
 */
function pointInCylinder(point, a, b, radius) {
  const ab = vec3.sub(b, a);
  const ap = vec3.sub(point, a);
  const abLenSq = vec3.dot(ab, ab);

  if (abLenSq < 1e-6) {
    // Degenerate cylinder (a and b coincide); use sphere
    return vec3.distance(point, a) <= radius;
  }

  const t = vec3.dot(ap, ab) / abLenSq;
  const closest = vec3.add(a, vec3.scale(ab, Math.max(0, Math.min(1, t))));
  const distToCylinder = vec3.distance(point, closest);

  return distToCylinder <= radius;
}

/**
 * distToLineSegment(point, a, b): returns { dist: scalar, closest: {x,y,z}, t: [0,1] }
 * Finds closest point on line segment AB to the given point
 */
function distToLineSegment(point, a, b) {
  const ab = vec3.sub(b, a);
  const ap = vec3.sub(point, a);
  const abLenSq = vec3.dot(ab, ab);

  if (abLenSq < 1e-6) {
    // Degenerate segment (a and b coincide)
    return {
      dist: vec3.distance(point, a),
      closest: a,
      t: 0,
    };
  }

  let t = vec3.dot(ap, ab) / abLenSq;
  t = Math.max(0, Math.min(1, t)); // Clamp to [0, 1]

  const closest = vec3.add(a, vec3.scale(ab, t));
  const dist = vec3.distance(point, closest);

  return { dist, closest, t };
}

// Dual-environment export
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    vec3,
    quat,
    integratePosition,
    integrateRotation,
    applyDrag,
    sphereVsSphere,
    raySphere,
    pointInCylinder,
    distToLineSegment,
  };
} else {
  window.LSS_SHARED = window.LSS_SHARED || {};
  Object.assign(window.LSS_SHARED, {
    vec3,
    quat,
    integratePosition,
    integrateRotation,
    applyDrag,
    sphereVsSphere,
    raySphere,
    pointInCylinder,
    distToLineSegment,
  });
}
