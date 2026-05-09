# galaxy-gen feature inventory

Baseline snapshot of what this repo does, so future changes can be evaluated as scope increases or decreases. Sourced from the code as of 2026-05-08, not from the readme. Pairs with `readme.md` (high-level pitch) and `development.md` (architecture deep-dive).

## Simulation core (Rust, `src/rust/galaxy.rs`)

- **Cell-grid N-body sim** - flat `size × size` grid, Struct-of-Arrays storage (`mass`, `vel_x/y`, `frac_x/y`, `acc_x/y`, `xs_i/ys_i`) so the inner loop auto-vectorizes.
- **Newtonian gravity, O(N²/2) symmetric pair sweep** - skips zero-mass cells on either side, accumulates cartesian acceleration. Polar (mag/deg) representation was removed to drop four trig calls per pair.
- **Precomputed inv-r³ lookup table** - `inv_r3[r²] = G · (r² + soft)^(-3/2)`, indexed by integer r² so the hot path has no `sqrt`.
- **Sub-grid fractional offsets** - cells accumulate fractional position across ticks instead of snapping per step.
- **Per-tick step cap** (`MAX_SUBGRID_STEP = 0.5`) - keeps tight mass concentrations from teleporting across the grid.
- **Softening length** (`SOFTENING_SQ = 1.0`) - avoids divide-by-zero when cells share a cell.
- **Mass-merge on collision** - `apply_acceleration` reassigns cells to destination indices and accumulates into a `Vec<u32>` scratch buffer instead of a `HashMap`.
- **Immutable-style API** - `seed()` and `tick()` return a new `Galaxy`. Internally reuses scratch buffers and moves output arrays.
- **Four initial-condition presets** (`InitialCondition` enum, exposed to JS):
  - `Uniform` - random mass, zero initial velocity.
  - `Rotation` - disk with tangential velocity scaled by radius.
  - `Bang` - central mass cluster with outward radial velocity (plus jitter).
  - `Collision` - two offset clusters on grazing intercept.
- **Reproducible seeding** - `seed_with(additional, seed: u64)` uses ChaCha-based `StdRng`. Two galaxies with the same `(additional, seed)` are byte-identical. Powers `?seed=…` URL sharing.
- **State snapshot/restore** - `from_state(...)` rebuilds a `Galaxy` from raw arrays. Used to ship state in/out of the Web Worker without re-seeding.
- **External-acceleration tick path** - `tick_with_accel(time, acc_x, acc_y)` lets a non-Rust backend (WebGPU) supply the force field and reuse the CPU integrator + collision step.
- **Zero-copy typed-array exports** - `mass_ptr()` / `mass_len()` plus `mass()` / `x()` / `y()` / `vel_x()` / `vel_y()` / `frac_x()` / `frac_y()` accessors so JS can read directly from WASM memory.
- **Rust unit tests** in-file under `mod tests_*` blocks.
- **Bench harnesses** at `benches/tick_bench.rs` and `benches/debug_sim.rs`.

## JS / WASM boundary (`src/js/lib/galaxy.ts`)

- **`Frontend` class** wraps the WASM `Galaxy` and exposes a stable JS surface.
- **Pluggable compute backend** - `ComputeBackend = "cpu" | "webgpu"`, selectable at runtime, with WebGPU falling back to CPU on tick failure.
- **Snapshot / restore helpers** for moving state between main thread and worker.

## Web Worker tick loop (`src/js/lib/tick-worker.ts`)

- **Physics off the main thread** - the worker owns its own `Galaxy` WASM instance and runs the continuous tick loop.
- **Zero-copy buffer transfer** - state arrays are transferred (not copied) into and out of the worker.
- **Live `dt` updates** - main thread can change the time modifier mid-run.
- **Graceful degradation** - if `Worker` is unavailable, the run loop reports unsupported instead of crashing.

## WebGPU backend (`src/js/lib/webgpu.ts`)

- **WGSL compute shader** for direct-sum O(N²) N-body force kernel.
- **Storage / uniform buffer layout** - bodies as `(pos.xy, mass, _pad)`, params as `(n, g, soft_sq, _pad)`.
- **Feature detection + clean fallback** via `isWebGPUAvailable()` and `WebGPUForceBackend.create()`.
- **Hands acceleration back to Rust** through `tick_with_accel`, so collision and integration stay in WASM.

## React UI (`src/js/lib/application.tsx`)

- **Plain `useState`** for all UI state. No state library.
- **Controls**: galaxy size, seed mass, initial-condition dropdown, init / tick / run-pause / reset-view buttons.
- **Live stats**: `dt`, tick count, tick milliseconds, FPS.
- **Keyboard shortcuts**: `space` play/pause, `↑`/`↓` scale `dt` by 1.25×, `r` reset `dt` to 0.5.
- **URL parameter round-trip** - `?seed=&size=&mass=&dt=` parsed on load and written via `history.replaceState` (no history-stack churn).
- **u64 seed handling** - `crypto.getRandomValues` for fresh seeds, `BigInt` parse/validate for pasted seeds.
- **WASM-ready gate** - `data-wasm-ready` attribute on the app root, buttons disabled until the module loads.
- **Test-id contract** - every button/input/stat that E2E touches has a `data-testid`. Treated as load-bearing by AGENTS.md.

## Visualization (`src/js/lib/dataviz.tsx`)

- **Canvas (not SVG) renderer** - single `<canvas>` strokes every cell per frame. SVG `setAttribute` was a hot-path bottleneck.
- **DPR-aware** - clamped to 2× for HiDPI without ballooning canvas size.
- **Pan + zoom camera** - pointer-drag pan, wheel zoom (with ctrl-wheel pinch handling), zoom clamped to `[1, 50]`, pan clamped so the world rect always intersects the viewport.
- **Camera state observable** - `data-cam-tx` / `data-cam-ty` / `data-cam-zoom` published on `#dataviz` for E2E and external observers.
- **Reset-view button** to recenter pan/zoom.

## Build, test, deploy

- **Rust → WASM toolchain** - `wasm-pack build` outputs `pkg/`, linked into `node_modules/galaxy_gen_backend` via `npm install ./pkg`.
- **Webpack 5 + Babel** (React + TypeScript presets), Tailwind v4 via PostCSS.
- **HMR + dual auto-reload** - `make dev` runs `cargo watch` → `wasm-pack build --dev` alongside `webpack-dev-server`. JS dev server live-reloads on `pkg/` changes.
- **ESLint flat config + Prettier** over `src/` and `e2e/`.
- **TypeScript noEmit typecheck** (`npm run typecheck`).
- **Rust lint/format** - `cargo clippy -- -D warnings`, `cargo fmt`.
- **Playwright E2E** (`e2e/galaxy.spec.ts`) - boots dev server, asserts UI shell, init, seed cell count, tick advancement, mass redistribution, WebGPU path when `navigator.gpu` is present. Filters expected reload-noise console errors.
- **CI** - GitHub Actions runs `rust`, `js`, `e2e` jobs on push/PR to `main`. E2E uploads HTML report on failure.
- **Sentry browser SDK** wired in `src/js/index.js` (`SENTRY_DSN` env-driven).
- **Docker image** built and published to GitHub Container Registry.
- **Production hosting** - served through Caddy on k3s on `kai-server` via Tailscale, at `galaxy-gen.coilysiren.me`. Caddyfile and k8s manifest under `deploy/`.
- **Repo-baseline scripts** - `scripts/check-commit-closes-issue.py` enforces the workspace "every commit closes an issue" rule.

## Known scope-shape signals

- The repo lists nine inspirational sibling projects in the readme. Use that list when evaluating proposed scope adds. Items already pulled in: WebGPU compute kernel (idea #9), worker-based physics (echo of `n-body-wasm-webvr`), reproducible seeding + URL params (echo of `JS_ParticleSystem`'s parameter tuning).
- The Python predecessor (`galaxySim`) is explicitly retired. Don't port features back from it without checking they survived the Rust rewrite intentionally.
- `docs/perf-rewrite.md` documents the SoA + cartesian + lookup-table rewrite. Treat its decisions as load-bearing for the inner loop.
