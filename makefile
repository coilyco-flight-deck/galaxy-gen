.DEFAULT_GOAL := help

.PHONY: help install test-rust build-rust build-wasm build-js-prod dev dev-js dev-rust \
        test-e2e test-e2e-ui test build-docker publish deploy \
        .build-docker .publish .deploy .deploy-ssh

# --- Config (sourced from coily.yaml, same pattern as the eco-* repos) ------
dns-name    ?= $(shell cat coily.yaml | yq e '.dns-name')
email       ?= $(shell cat coily.yaml | yq e '.email')
name        ?= $(shell cat coily.yaml | yq e '.name')
port        ?= $(shell cat coily.yaml | yq e '.port')
name-dashed ?= $(subst /,-,$(name))
git-hash    ?= $(shell git rev-parse HEAD 2>/dev/null || echo dev)
# Fully-qualified ref into the in-cluster registry. Forgejo Actions builds
# this, pushes it over plain http (the runner's DinD carries
# --insecure-registry=192.168.0.194:30500), and kai-server's containerd
# pulls it via its registries.yaml insecure entry. See
# coilysiren/infrastructure#168, #171.
image-url   ?= 192.168.0.194:30500/$(name-dashed):$(git-hash)

help: ## Show this help
	@perl -nle'print $& if m{^[a-zA-Z_-]+:.*?## .*$$}' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-25s\033[0m %s\n", $$1, $$2}'

# --- Local dev -------------------------------------------------------------

install: ## Install Rust, WASM, and JS deps (cargo build + wasm-pack + npm install + playwright install).
	cargo build
	cargo install wasm-pack
	wasm-pack build
	npm install
	npx playwright install chromium

test-rust: ## cargo check + cargo test.
	cargo check
	cargo test -- --color always

build-rust: build-wasm ## Build Rust + WASM (debug).
	cargo build

build-wasm: ## Compile Rust to WASM via wasm-pack (pkg/).
	wasm-pack build

build-js-prod: build-wasm ## Production webpack build.
	npx webpack --config webpack.config.js --mode production

dev: ## Run the rust/wasm watcher and webpack-dev-server concurrently with auto-reload.
	@echo "Starting rust watcher + JS dev server (Ctrl-C stops both)"
	@trap 'kill 0' INT TERM EXIT; \
		cargo watch -w src/rust -w Cargo.toml -s "wasm-pack build --dev" & \
		npx webpack serve --open & \
		wait

dev-js: ## Run only the JS dev server with HMR.
	npx webpack serve --open

dev-rust: ## Run only the Rust/WASM watcher.
	cargo watch -w src/rust -w Cargo.toml -s "wasm-pack build --dev"

test-e2e: build-wasm ## Run Playwright end-to-end tests.
	npm install ./pkg --no-save
	npx playwright test

test-e2e-ui: build-wasm ## Run Playwright tests in UI mode.
	npm install ./pkg --no-save
	npx playwright test --ui

test: test-rust test-e2e ## Run all tests (rust + e2e)

# --- Docker / deploy (same shape as eco-spec-tracker) ----------------------

.build-docker:
	docker build \
		--progress plain \
		--build-arg BUILDKIT_INLINE_CACHE=1 \
		--build-arg SENTRY_DSN=$(SENTRY_DSN) \
		--cache-from $(name):latest \
		-t $(name):$(git-hash) \
		-t $(name):latest \
		.

build-docker: .build-docker ## Build the docker image locally with BuildKit cache.

run-docker: ## Run the production image locally on $(port)
	docker run -e PORT=$(port) -p $(port):$(port) -it --rm $(name):latest

.publish:
	docker tag $(name):$(git-hash) $(image-url)
	docker push $(image-url)

publish: build-docker .publish ## Tag and push the docker image to the in-cluster registry.

.deploy:
	env \
		NAME=$(name-dashed) \
		DNS_NAME=$(dns-name) \
		IMAGE=$(image-url) \
		envsubst < deploy/main.yml | kubectl apply -f -
	kubectl rollout status deployment/$(name-dashed)-app -n $(name-dashed) --timeout=5m

# Stream the rendered manifest over Tailscale SSH and apply on kai-server.
# Fallback path when the tailnet kubectl route is unavailable.
.deploy-ssh:
	env \
		NAME=$(name-dashed) \
		DNS_NAME=$(dns-name) \
		IMAGE=$(image-url) \
		envsubst < deploy/main.yml | \
		ssh -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile=/dev/null kai@kai-server \
			'kubectl --kubeconfig=/home/kai/.kube/config apply -f -'

deploy: publish .deploy ## Build, push, and apply to the cluster
