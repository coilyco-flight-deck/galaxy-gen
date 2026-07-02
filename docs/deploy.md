# Deploying galaxy-gen

galaxy-gen serves a static WASM + JS bundle from a stock `caddy:2-alpine` on k3s
on `kai-server`. Manifest: `deploy/main.yml`. The "stock caddy + data bundle"
shape is in [FEATURES.md](FEATURES.md) (galaxy-gen#22).

Two ways to roll a deploy. Both build the same amd64 image, push it to the
in-cluster registry over plain http, and `kubectl set image` the bundle-loader
initContainer to trigger a rollout.

- CI (push to `main`) - `.forgejo/workflows/build-publish-deploy.yml`. The sustainable path: in-cluster, native amd64, node-local registry push. Preferred.
- Local (`ward exec deploy` on an on-LAN host) - see [deploy-local.md](deploy-local.md). The manual fallback.

## CI deploy path

On every push to `main` the in-cluster Forgejo Actions runner runs `test` (Rust
unit tests) then `deploy` (install static docker + kubectl, resolve the DinD
host, `docker build --platform linux/amd64` + push to `192.168.0.194:30500`,
`kubectl set image` + `rollout status` against the k3s API at
`192.168.0.194:6443`).

### Prerequisites (host/infra, not in this repo)

A green `test` with a failing `deploy` almost always points at one of these two,
which live outside the repo tree:

- **The in-cluster Forgejo Actions runner must be online.** If a push to `main` creates no new run (the newest run stays pinned to an old commit), the runner is stalled. It runs in-cluster, so recovery is a cluster-side action (restart / re-register the runner pod), not a repo change.
- **The `DEPLOY_KUBECONFIG` Actions secret must be present on THIS repo.** It is a base64 kubeconfig for the `deployer` ServiceAccount (`deploy/main.yml`) that authenticates the `Roll deployment` step. Forgejo Actions secrets are per-repo and **do not migrate when a repo moves orgs** (this repo moved `coilysiren` -> `coilyco-flight-deck`), so re-set it after such a move or the roll fails instantly having reached no cluster.

Historically `deploy` always failed at `Roll deployment` while `Build and push`
succeeded - the signature of a missing/stale kubeconfig. The step now guards for
an empty secret and preflights auth before rolling, so the failure names the
real cause instead of a cryptic 0-second kubectl error (galaxy-gen#26).

### Rebuilding DEPLOY_KUBECONFIG

If the secret is missing or the token rotated, rebuild it from the deployer SA's
token Secret and set it on the repo's Forgejo Actions secrets. Run on an on-LAN
host with a cluster-admin kubeconfig, in namespace `coilysiren-galaxy-gen`:

```bash
NS=coilysiren-galaxy-gen
CA=$(kubectl -n "$NS" get secret deployer-token -o jsonpath='{.data.ca\.crt}')
TOKEN=$(kubectl -n "$NS" get secret deployer-token -o jsonpath='{.data.token}' | base64 -d)
kubectl config set-cluster k3s --server=https://192.168.0.194:6443 --kubeconfig=/tmp/kc
kubectl config set clusters.k3s.certificate-authority-data "$CA" --kubeconfig=/tmp/kc
kubectl config set-credentials deployer --token="$TOKEN" --kubeconfig=/tmp/kc
kubectl config set-context deployer --cluster=k3s --user=deployer --namespace="$NS" --kubeconfig=/tmp/kc
kubectl config use-context deployer --kubeconfig=/tmp/kc
base64 -w0 /tmp/kc   # paste into the DEPLOY_KUBECONFIG Actions secret
```

## Troubleshooting

- **`deploy` fails at `Roll deployment`, 0 seconds, `Build and push` green** - `DEPLOY_KUBECONFIG` is empty/stale. Rebuild it (above). Top suspect after an org move.
- **No CI run appears for a push to `main`** - the in-cluster Forgejo runner is offline. Recover it cluster-side.
- **Orphaned registry images** - an arm64 `coilysiren-galaxy-gen:dcb1533...` from the pre-`--platform` build sits in the registry. Harmless, GC when convenient.
- Local-path symptoms (arch mismatch, hung push, LAN route) live in [deploy-local.md](deploy-local.md).

## See also

- [../AGENTS.md](../AGENTS.md) - the Deploy section.
- [deploy-local.md](deploy-local.md) - local deploy host prerequisites.
- `../.forgejo/workflows/build-publish-deploy.yml` - the CI pipeline.
</content>
