# syntax=docker/dockerfile:1.7
# -----------------------------------------------------------------------------
# Stage 1: build Rust -> WASM -> JS static bundle
# -----------------------------------------------------------------------------
FROM rust:1.90-bookworm AS builder

# Node (for webpack) + curl (for wasm-pack and binaryen installers).
# Binaryen is pulled from the upstream release tarball below, NOT apt:
# Debian's binaryen produces wasm-opt output that trips
# `WebAssembly.Table.grow(): failed to grow table by 4` in chromium at
# instantiation time, which wedges the whole JS module graph (React never
# mounts). Matches the pin used by .github/workflows/*.yml.
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      curl ca-certificates \
 && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
 && apt-get install -y --no-install-recommends nodejs \
 && rm -rf /var/lib/apt/lists/*

# Pinned upstream binaryen release. Keep the version in sync with
# .github/workflows/action.yml and build-and-publish.yml.
RUN VER=version_119 \
 && curl -sSL "https://github.com/WebAssembly/binaryen/releases/download/${VER}/binaryen-${VER}-x86_64-linux.tar.gz" -o /tmp/binaryen.tgz \
 && tar -xzf /tmp/binaryen.tgz -C /usr/local --strip-components=1 \
 && rm /tmp/binaryen.tgz \
 && wasm-opt --version

RUN curl -sSf https://rustwasm.github.io/wasm-pack/installer/init.sh | sh

WORKDIR /app

# Cache rust deps: copy manifests and build a shim first.
COPY Cargo.toml Cargo.lock ./
RUN mkdir -p src/rust && \
    echo "fn main() {}" > src/rust/lib.rs && \
    cargo fetch

# Now the real sources.
COPY src ./src
RUN wasm-pack build --release --out-dir pkg

# Node dependencies + build
COPY package.json package-lock.json ./
COPY webpack.config.js postcss.config.js tsconfig.json ./
RUN npm ci
RUN npm install ./pkg --no-save

# Sentry DSN is baked into the JS bundle at build time by webpack's
# DefinePlugin (see webpack.config.js). Browser is the runtime, so a
# k8s env var would be too late. Absent ARG = empty DSN = Sentry stays
# disabled, which is the correct local/dev default.
ARG SENTRY_DSN=""
ENV SENTRY_DSN=${SENTRY_DSN}
RUN npm run build

# -----------------------------------------------------------------------------
# Stage 2: pure data image - the built bundle + its Caddyfile, nothing to run.
# -----------------------------------------------------------------------------
# The runtime is a *stock, unmodified* caddy:2-alpine in the Deployment (see
# deploy/main.yml). This image carries only the payload: an initContainer runs
# it and copies /dist + /Caddyfile into a shared emptyDir the caddy container
# then serves. So the asset bundle and its server config roll atomically per
# git-sha while the serving layer stays byte-for-byte upstream caddy.
#
# Base is busybox (not scratch) because the initContainer needs `sh`/`cp` to
# move the payload into the volume. Swap to `FROM scratch` + a `volumes[].image`
# mount once kai-server is on k8s 1.33+ (ImageVolume GA). See galaxy-gen#22.
FROM busybox:1.37 AS runtime

COPY --from=builder /app/dist /dist
COPY deploy/Caddyfile /Caddyfile
