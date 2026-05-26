# Galaxy simulation internals

Cell grid with Newtonian gravity, in-place tick.

## Layout

Struct-of-arrays (parallel `Vec<f32>` / `Vec<u16>`) so the physics inner loop is a tight numeric kernel the optimizer can auto-vectorize. Acceleration accumulates in cartesian (ax, ay). The old polar representation required four trig calls per pair, which dominated tick cost.

## Hot path

`tick()` runs two passes:

- `gravitate_all()`. O(N squared / 2) pair sweep, symmetric per Newton's third law. Skips mass=0 on either side.
- `apply_acceleration()`. Integrate one step, reassign cells to destination grid indices, accumulate mass on collision. Uses a `Vec<u32>` (size N squared) instead of a `HashMap` to coalesce masses.

`tick` returns a new `Galaxy` to preserve the JS API, but internally reuses scratch buffers and moves the resulting arrays.

## Constants

- `GRAVATIONAL_CONSTANT` is 5.0e-2. Newton's G of 6.67e-11 is numerically invisible at this grid scale.
- `SOFTENING_SQ` is 1.0. Avoids division by ~0 when cells share a grid cell.
- `MAX_SUBGRID_STEP` is 0.5. Caps per-tick position delta so we don't teleport across the grid on a tight mass concentration.

## Buffers

- `vel_x`, `vel_y`. Persistent per-cell velocity. Without persistence the sim restarts from rest each tick and produces imperceptible motion.
- `frac_x`, `frac_y`. Sub-grid fractional offsets so a cell accumulates toward its next grid cell across ticks rather than snapping.
- `xs_i`, `ys_i`. Integer cell positions. Integer diffs let us index an inv-r-cubed lookup with r squared, no `sqrt` in the hot loop.
- `inv_r3`. Precomputed `g * (r squared + soft) ^ (-3/2)` indexed by integer r squared. Populated in `new()`, reused across seeds and ticks.
- `scratch_mass`. Reused across ticks.
