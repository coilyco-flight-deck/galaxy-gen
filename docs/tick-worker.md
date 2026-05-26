# Tick worker message protocol

Web Worker that owns its own `Galaxy` WASM instance and runs `tick` off the main thread.

## Main to worker

- `init` with `size, mass, velX, velY, fracX, fracY`. Hydrate a new Galaxy from transferred state.
- `start` with `timeModifier`. Begin looping. Tick, post snapshot, schedule next.
- `setTimeModifier` with `timeModifier`. Live-update dt without stopping.
- `stop`. Halt the loop. Worker replies with final state for rehydration.

## Worker to main

- `snapshot` with `mass, tickMs, tickId`. Per-tick mass snapshot (Uint16Array, transferred).
- `stopped` with `mass, velX, velY, fracX, fracY`. Final state after stop, so the main thread can rehydrate without losing velocity or sub-grid position.
