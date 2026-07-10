---
name: coding-galaxy-gen-cosmology
description: Cosmology and relativity for the procedural galaxy sim. Universe-scale physics - Hubble flow, FLRW, redshift, dark sector, gravitational physics, CMB. Sister to the galaxy-scale skill. Triggers - cosmology, FLRW, Hubble's law, redshift, dark energy, dark matter, CMB, cosmic web, gravitational lensing, Schwarzschild, black hole, general relativity, lookback time, comoving distance.
---

# Cosmology for galaxy-gen

Repo: galaxy-gen. Stack: Rust to WASM in the browser. Sister skill: [`coding-galaxy-gen-astrophysics`](../coding-galaxy-gen-astrophysics/SKILL.md) covers galaxy-scale physics.

This skill covers physics that only matters when the sim's scene is bigger than one galaxy, or when the visual needs to be redshift-aware. A single isolated-galaxy sim can largely ignore this. A cosmic-web or "zoom out" sim cannot.

## Scope decision: how big is the scene

This question gates everything in this skill. Pick a scope before designing the data model.

* **Single galaxy** - tens of kpc across, fixed observer, no expansion. Stop reading. Use only the astrophysics skill.
* **Galaxy field** - Mpc scale, many galaxies, no redshift. Need Schechter luminosity function (galaxy-scale skill). Hubble expansion still negligible at this scale.
* **Local universe** - hundreds of Mpc, redshift up to about 0.1. Hubble flow visible as velocity-distance correlation. Use linear Hubble's law.
* **Cosmological** - Gpc and z > 0.5. Full FLRW geometry, lookback time, comoving vs proper distance distinction matters. Redshift affects color and surface brightness.

## Hubble's law and the expansion

The relationship between distance and velocity that makes the universe expand.

* **Hubble's law** - v = H_0 d. H_0 is about 70 km/s/Mpc (the Hubble tension between local and CMB measurements is real but does not matter for a sim). v is recession velocity, d is proper distance.
* **Redshift** - z = (lambda_obs - lambda_emit) / lambda_emit. For small z: z ~ v/c. For large z: 1 + z = sqrt((1 + v/c) / (1 - v/c)) (relativistic) or compute from cosmology.
* **Lookback time** - light from a galaxy at z arrived after traveling for a time that depends on cosmology. For a quick approximation: t_lookback / t_H ~ z for z << 1, where t_H = 1/H_0 ~ 14 Gyr. Past z ~ 1 you need to integrate.
* **Comoving distance** - the distance that grows with the universe. Useful for placing galaxies in a fixed coordinate system. Convert to proper distance by multiplying by the scale factor a(t).

## FLRW geometry

The standard cosmological metric. Only needed at cosmological scope.

* **Scale factor a(t)** - dimensionless, a = 1 today, a < 1 in the past. All comoving distances scale by a(t). H(t) = a_dot / a is the Hubble parameter; H_0 is its value today.
* **Friedmann equation** - H^2 = H_0^2 (Omega_m / a^3 + Omega_r / a^4 + Omega_Lambda + Omega_k / a^2). Cosmological parameters: Omega_m ~ 0.3 (matter), Omega_Lambda ~ 0.7 (dark energy), Omega_r ~ 10^-4 (radiation, negligible today), Omega_k ~ 0 (spatial flatness). LCDM is the consensus.
* **Useful approximations** - matter-dominated era (z > 1): a proportional to t^(2/3). Dark-energy-dominated (today): a proportional to exp(H_0 t). Radiation era is irrelevant unless modeling the early universe.

## Dark matter

Already covered as a halo profile in the galaxy-scale skill. The cosmology angle:

* **Cosmic web** - dark matter forms a filamentary network at the largest scales. Galaxies form at the nodes and along filaments. Voids are empty bubbles tens of Mpc across.
* **Why it matters for a sim** - if zooming out to many galaxies, do not distribute them uniformly. Use a power-spectrum-based density field or a precomputed N-body realization. A noise-modulated Voronoi tessellation gives a passable cheap approximation.
* **Mass scale hierarchy** - galaxies live inside halos of 10^11 - 10^14 M_sun. Cluster halos are 10^14 - 10^15. Superclusters are not gravitationally bound.

## Dark energy

The thing accelerating the expansion. Visually it does not show up directly but it controls the timeline.

* **Cosmological constant Lambda** - simplest model. Constant energy density (w = -1). Consistent with all data so far.
* **Sim impact** - sets the lookback-time-vs-distance function. If the sim shows the universe at different epochs (different z values), dark energy controls how much earlier each z corresponds to. Stretching is non-linear at large z.

## Gravitational physics for visuals

* **Schwarzschild radius** - r_s = 2 G M / c^2. Stellar BH: 30 km. Galactic SMBH (10^9 M_sun): 20 AU. Tiny in absolute terms; lensing reach is much larger.
* **Gravitational lensing** - foreground mass bends background light. Einstein rings, cluster arcs, microlensing. Procedural cheap version: radial distortion kernel around lensing masses.
* **Time dilation, Hawking radiation** - skip unless rendering a BH close-in or modeling primordial micro BHs.

## Cosmic microwave background

* **As a backdrop** - 2.725 K blackbody, 10^-5 anisotropies, locked at z ~ 1100 (universe became transparent at 380 kyr after Big Bang). If the sim has a sky sphere, use the Planck temperature map as the texture.
* **As a constraint** - CMB anisotropies fix Omega_m, Omega_Lambda, H_0. A cosmologically motivated sim should use Planck-consistent parameters.

## Redshift-dependent visuals

If the sim renders galaxies at varying z, get these right or the visual lies.

* **Color shift** - redshifted spectra slide blue to red. A blue spiral at z = 1 looks redder than the same spiral at z = 0. Apply by computing observed wavelength = (1 + z) * emitted wavelength, then re-evaluating the blackbody color.
* **Surface brightness dimming** - SB falls as (1 + z)^4 (Tolman dimming). High-z galaxies are dramatically fainter per unit area. This is why deep surveys see them only as compact bright spots.
* **Angular size** - has a turning point near z ~ 1.5 in LCDM. Galaxies at z = 5 are not arbitrarily small; their angular size starts to grow again because the universe was smaller when the light was emitted.
* **Cosmological dimming** - distance modulus mu = 5 log10(d_L / 10 pc), where d_L is luminosity distance (not the same as comoving distance at large z). The (1+z) factors are not interchangeable.

## Special relativity

Mostly does not matter unless the sim has fast-moving objects.

* **Relativistic beaming** - jets pointed at the observer appear brighter (factor proportional to gamma^4 or so). Explains why some AGN are extreme.
* **Aberration** - high-velocity observer sees the apparent direction of stars shift forward. Only relevant if the sim has an in-universe relativistic spaceship view.

## Common cosmology pitfalls

* **Linear Hubble's law at high z.** v = H_0 d only works for z << 1. Past z ~ 0.3 you need the full luminosity-distance integral. Linear extrapolation places z = 2 galaxies way too close.
* **Comoving vs proper distance.** If the sim has a fixed coordinate system, those are comoving coordinates. Light travel time and angular size depend on proper distance at the time of emission. Mixing them up gives wrong sizes and wrong delays.
* **Confusing Hubble flow with peculiar velocity.** Galaxies have local random motion (a few hundred km/s) on top of Hubble flow. For z < 0.01 the random motion dominates. The Local Group is moving toward the Virgo cluster at 600 km/s.
* **Treating dark matter as visible.** Dark matter is gravitational only. It produces lensing and rotation curves, not light. The halo is invisible in any electromagnetic-spectrum rendering.

## Numerical hooks for Rust/WASM

* **Cosmology lookup tables** - z to lookback time, z to luminosity distance, and z to comoving distance are all integrals with no closed form in LCDM. Precompute once as a table on Rust side, interpolate per particle.
* **Power spectrum for cosmic web** - if generating large-scale structure procedurally, use a Gaussian random field with the CDM power spectrum. The expensive part is the FFT; do it offline and ship the result.
* **Lensing as a 2D displacement field** - per-pixel deflection from a static lensing-mass texture is cheap on GPU. Skip the iterative photon-tracing approach unless modeling strong lensing specifically.

## Concept reference

Verbatim Wikipedia lead paragraphs (CC BY-SA 4.0) for every concept above live in [`references/wikipedia-concepts.md`](references/wikipedia-concepts.md). Reach there when a term needs a precise definition.

## Sources

Synthesized from public-license skill content. Originals carry derivations and worked examples if needed:

* [Tibsfox/relativity-astrophysics](https://github.com/Tibsfox/gsd-skill-creator/tree/main/examples/skills/physics/relativity-astrophysics) - SR + GR + cosmology with derivations. Strongest single source for this skill.
* [luokai0/astrophysics-expert](https://github.com/luokai0/ai-agent-skills-by-luo-kai/tree/main/ai-agent-skills/15-earth-and-space-sciences%20%28by%20Luo%20Kai%29/astrophysics-expert) - high-energy + observational angles on cosmology.
* [sandraschi/astronomy-astrophysics-expert](https://github.com/sandraschi/advanced-memory-mcp/tree/master/skill-zips/astronomy-astrophysics-expert/astronomy-astrophysics-expert) - recent mission data, Euclid / JWST results.
