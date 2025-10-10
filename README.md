# 1. Arcball Camera Explanation

Nice — let’s walk through this **step-by-step** and tie each idea directly to the code you pasted. I’ll explain the math and the data flow (mouse → 3D points → quaternion → view matrix), point out a small bug I found, and give a tiny usage snippet so you can see exactly how to hook it into a render loop.

---

# High-level idea (one sentence)

An arcball maps 2D mouse positions to points on a virtual sphere, computes the rotation that moves the start point to the end point (axis = cross, angle = acos(dot)), represents that rotation as a quaternion, composes it with the current camera rotation, and converts the quaternion to a 4×4 rotation matrix used in the view transform.

---

# Step-by-step (with code references)

### 1) Map mouse coords → normalized [-1, 1] window coordinates

Code:

```py
old, new = ((2*vec(pos) - winsize) / winsize for pos in (old, new))
```

Explanation: if `pos` is pixel coordinates and `winsize` is (width, height), this maps the mouse x,y to a coordinate where the center of the window is (0,0), left is -1, right +1, etc. That normalized 2D coordinate is what we feed into the virtual trackball.

---

### 2) Project the 2D point to a 3D point on the virtual sphere (or a hyperbolic sheet)

Code:

```py
def _project3d(self, position2d, radius=0.8):
    p2, r2 = sum(position2d*position2d), radius*radius
    zcoord = math.sqrt(r2 - p2) if 2*p2 < r2 else r2 / (2*math.sqrt(p2))
    return vec(*position2d, zcoord)
```

Explanation & intuition:

* If the 2D point lies inside the projected disk of the sphere, we place it on the sphere: (z = \sqrt{r^2 - x^2 - y^2}).
* If it lies outside, we use a *hyperbolic sheet* mapping `z = r^2 / (2*sqrt(x^2+y^2))` to keep motion continuous and well-behaved when the mouse is far from the center.
* This gives two 3D points (`old3`, `new3`) on/near the unit sphere which we then normalize.

---

### 3) Compute rotation axis and angle between the two 3D vectors

Code:

```py
old, new = (normalized(self._project3d(pos)) for pos in (old, new))
phi = 2 * math.acos(np.clip(np.dot(old, new), -1, 1))
return quaternion_from_axis_angle(np.cross(old, new), radians=phi)
```

Mathematics (correct approach):

* Let (u) and (v) be the normalized 3D points. The axis of rotation that takes (u) → (v) is the normalized cross product: (\mathbf{axis} = u \times v).
* The angle between the vectors is (\theta = \arccos(u\cdot v)).
* The quaternion for rotating by angle (\theta) around `axis` is
  [
  q = \big(\cos(\tfrac{\theta}{2}),; \mathbf{axis}\cdot\sin(\tfrac{\theta}{2})\big).
  ]
  **Important note / bug:** the code uses `phi = 2 * acos(dot)` and then passes `phi` into `quaternion_from_axis_angle`. That double-counts the angle. Correct formula is:

```py
phi = math.acos(np.clip(np.dot(old, new), -1, 1))
return quaternion_from_axis_angle(np.cross(old, new), radians=phi)
```

(With `phi = acos(dot)`, `quaternion_from_axis_angle` — which itself uses the half-angle internally — constructs the correct quaternion (q) with (\cos(\theta/2)) and (\sin(\theta/2)).)

If you leave `2*acos(...)` you end up with twice the intended rotation (for example a 90° mouse drag gives 180° rotation).

---

### 4) Build quaternion and compose with existing rotation

Functions:

```py
def quaternion_from_axis_angle(axis, radians=...):
    sin, cos = sincos(radians=radians*0.5)
    return quaternion(normalized(vec(axis))*sin, w=cos)

def quaternion_mul(q1, q2):  # matrix multiplication trick
    ...
```

Explanation:

* `quaternion_from_axis_angle` returns (q = [w, x, y, z] = [\cos(\theta/2), ; \mathbf{axis}\sin(\theta/2)]).
* `quaternion_mul(q_new, q_old)` composes rotations: `q_result = q_new * q_old`.
  In the code `self.rotation = quaternion_mul(self._rotate(old,new), self.rotation)` means “apply the new small rotation `q_new` *before* the existing rotation.” (Order matters; you can pre- or post- multiply depending on whether you want rotations in world or camera space.)

**Always keep quaternions normalized** after many multiplications (the `quaternion_matrix()` function normalizes `q` anyway but it’s good practice to normalize on update).

---

### 5) Turn quaternion into a 4×4 rotation matrix

Code:

```py
def quaternion_matrix(q):
    q = normalized(q)
    # then compute matrix entries
    return np.array([...], 'f')
```

Explanation: a unit quaternion maps exactly to a 3×3 rotation matrix. `quaternion_matrix` builds that matrix and returns a 4×4 with bottom row/col for homogeneous coordinates. You can apply this matrix to points or use it as the rotational part of your view matrix.

---

### 6) Build the final view matrix (translation + rotation)

Code:

```py
def view_matrix(self):
    return translate(*self.pos2d, -self.distance) @ self.matrix()
```

Explanation:

* `matrix()` returns the 4×4 rotation from the quaternion.
* `translate(*self.pos2d, -self.distance)` moves the camera back by `distance` and offsets by `pos2d` (panning).
* Multiplying `translate @ rotation` yields a full view transform you can pass to your renderer (modelview = view @ model).

---

### 7) Zoom and Pan

* `zoom(self, delta, size)` multiplies `distance` to zoom in/out.
* `pan(self, old, new)` changes `pos2d` to slide the target; the displacement is scaled by `0.001 * distance` so panning sensitivity scales with camera distance.

---

# How to use in a render loop (pseudo)

```py
tb = Trackball()

# on mouse-down:
mouse_old = (mx, my)

# on mouse-drag:
tb.drag(mouse_old, (mx, my), winsize=(width, height))
mouse_old = (mx, my)

# on mouse-wheel:
tb.zoom(delta, max(width, height))

# in render:
view = tb.view_matrix()
proj = tb.projection_matrix((width, height))
# pass view and proj to your shader / set modelview = view @ model
```

