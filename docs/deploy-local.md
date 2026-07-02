# Local deploy: host prerequisites

`ward exec deploy` (`makefile` `deploy` -> `publish` -> `.deploy`) builds the
image locally, pushes it to the in-cluster registry, and applies + rolls the
Deployment. Use it from an on-LAN host when CI is down or you need an
out-of-band roll. The CI path and its prerequisites are in [deploy.md](deploy.md).

## Host prerequisites (kais-macbook-pro)

The Mac's arch and networking add friction the in-cluster runner does not have.
For `ward exec deploy` to work from a Mac on the LAN:

- **OrbStack must trust the insecure registry.** Add `192.168.0.194:30500` to `insecure-registries` in `~/.orbstack/config/docker.json` so the plain-http push round-trips. Set it in that file (persistent), not via a transient flag, or it will not survive an OrbStack restart.
- **The OrbStack VM must have a healthy route to the LAN.** A degraded VM -> LAN route makes the registry push or the `kubectl` roll hang or i/o-timeout mid-apply. A clean OrbStack relaunch (quit fully, reopen) restored the route during the #23 cutover.
- **The build must target amd64.** The `makefile` `.build-docker` target already passes `--platform linux/amd64`. kai-server is amd64 and the build stage hardcodes the x86_64 binaryen tarball, so an arm64 build (Apple Silicon default) produces a manifest the node rejects at pull time with `no match for platform in manifest`.
- **kubectl must reach the k3s API.** `.deploy` defaults to the LAN IP (`k8s-api=https://192.168.0.194:6443`), in the cert SANs and rock-solid from on-LAN hosts. The kubeconfig's `kai-server` context resolves to the flaky tailnet MagicDNS route, so override to the tailnet only when deploying off-LAN: `ward exec deploy k8s-api=https://kai-server:6443` (galaxy-gen#25).

## Troubleshooting

- **`no match for platform in manifest` at pod pull** - an arm64 image reached the registry. Rebuild with `--platform linux/amd64` (the makefile already does).
- **Local push or roll hangs / i/o-times-out** - degraded OrbStack VM -> LAN route. Relaunch OrbStack; confirm `192.168.0.194:30500` is in `insecure-registries`.
- **`connection refused` / auth error on apply** - kubectl is aimed at the wrong API or lacks creds. Confirm `k8s-api` and that your kubeconfig context is cluster-admin on-LAN.

## See also

- [deploy.md](deploy.md) - overview + CI deploy path.
- `../makefile` - the `deploy` / `publish` / `.deploy` targets.
</content>
