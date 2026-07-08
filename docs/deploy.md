# Deploying galaxy-gen

galaxy-gen serves a static WASM + JS bundle from a stock `caddy:2-alpine` on
k3s on `kai-server`. Manifest: `deploy/main.yml`. The "stock caddy + data
bundle" shape is in [FEATURES.md](FEATURES.md) (galaxy-gen#22).

There are two deploy paths now:

- Pull-side update - the normal redeploy path. The cluster reconciler picks up
  a new bundle image without GitHub Actions touching k3s or the tailnet.
- Local (`ward exec deploy` on an on-LAN host) - see
  [deploy-local.md](deploy-local.md). The manual fallback.

The Forgejo workflow (`.forgejo/workflows/build-publish-deploy.yml`) runs
`test` on push to `main` and nothing else. Browser e2e and `tsc` stay on GitHub
PR CI (`.github/workflows/action.yml`).

## See also

- [../AGENTS.md](../AGENTS.md) - the Deploy section.
- [deploy-local.md](deploy-local.md) - local deploy host prerequisites.
- `../.forgejo/workflows/build-publish-deploy.yml` - the Forgejo test pipeline.
