---
name: coding-galaxy-gen-astrophysics
description: Galaxy-scale astrophysics for the procedural galaxy sim. Morphology, mass distribution, rotation curves, star formation, stellar populations, AGN, mergers. Triggers - galaxy generation, galaxy morphology, spiral arms, elliptical, rotation curve, dark matter halo, IMF, HR diagram, star formation, AGN, supermassive black hole, galaxy merger, Hubble sequence, Tully-Fisher.
---

# Astrophysics for galaxy-gen

Repo: [coilysiren/galaxy-gen](https://github.com/coilysiren/galaxy-gen). Stack: Rust compiled to WASM, rendered in the browser via JS/TS. Sister skill: [`coding-galaxy-gen-cosmology`](../coding-galaxy-gen-cosmology/SKILL.md) covers the cosmological-scale physics.

This skill encodes the galaxy-scale astrophysics that should shape design decisions. It is not a survey of the field. It is the subset that maps onto procedural-sim choices: what to sample, what to ignore, what gets a closed-form approximation vs. a particle simulation.

## What to sample, what to fake

A procedural galaxy sim is sampling from physically motivated distributions. The fidelity question is which distributions are load-bearing for the visual and which can be hand-waved. Order of importance for a browser-rendered sim:

* **Morphology class** - elliptical / spiral / lenticular / irregular - drives every downstream sampler (geometry, kinematics, color, gas fraction). Pick the class first, then sample the rest conditionally.
* **Mass distribution** - the stellar bulge + disk + halo split sets where particles can plausibly sit. Dark matter halo dominates total mass (5-10x stellar) and explains flat rotation curves, but emits no light.
* **Stellar population** - the per-particle color and luminosity. Driven by the IMF (initial mass function) and age. Cheap to sample, high visual payoff.
* **Star-forming gas + dust** - controls reddening and the bright knots in spiral arms. Optional; faking with a noise texture aligned to the spiral pattern is often enough.
* **AGN** - one bright nucleus, only for a fraction of galaxies. Bolt-on, not foundational.

## Morphology and the Hubble sequence

Hubble's tuning-fork classification still does the work for procedural pickers. Sample the class up front, then condition everything else on it.

* **Ellipticals (E0-E7)** - axisymmetric, dispersion-supported (random stellar orbits, not rotation). Old stellar populations (red, low gas, low star formation). Sersic light profile with index n ~ 4 (de Vaucouleurs profile). Axis ratio is the only major geometric knob.
* **Spirals (Sa-Sd)** - rotation-supported thin disk + central bulge. Sa has a fat bulge and tight arms, Sd has almost no bulge and loose arms. Disk follows an exponential surface-brightness profile. Spiral arms are density waves, not material structures. Use a logarithmic spiral pattern with pitch angle 10-40 degrees (tight to loose).
* **Barred spirals (SBa-SBd)** - same as spirals but with a stellar bar across the bulge. Common (about a third of disk galaxies including the Milky Way). The bar is a kinematic feature, modeled as an elongated mass concentration.
* **Lenticular (S0)** - disk like a spiral but gas-poor, no arms. Often skipped in procedural sims.
* **Irregular** - no symmetry. Easiest to fake with pure noise; covers dwarfs and merger remnants.

The Hubble fractions vary by environment but a reasonable global mix is roughly 70% spirals (with bars), 25% ellipticals, 5% irregulars in the local universe. Higher elliptical fraction in clusters.

## Stellar mass profiles

These are the closed-form profiles you sample from for stellar positions. Both are cheap, both have analytic inverses for rejection sampling.

* **Exponential disk** - Sigma(R) = Sigma_0 exp(-R / R_d). Use for spiral disks. R_d is the scale length, typically 2-5 kpc. Vertical scale height h_z is about 10% of R_d for thin disks.
* **Sersic / de Vaucouleurs** - Sigma(R) = Sigma_e exp(-b_n [(R/R_e)^(1/n) - 1]). n = 4 for ellipticals and bulges, n = 1 reduces to exponential. R_e is the effective radius enclosing half the light.
* **NFW dark matter halo** - rho(r) = rho_0 / ((r/r_s)(1 + r/r_s)^2). Only matters if you want rotation curves to flatten correctly. Dark particles are invisible; the halo enters as a gravitational potential.

## Rotation curves

The "flat rotation curve" is the most famous galaxy-scale physics result and the cleanest dark-matter signature. If the sim shows orbits, it should show flat curves.

* **Keplerian fall-off** - v(r) proportional to 1/sqrt(r) outside the visible mass. This is what you would see if only stellar+gas mass contributed. Real galaxies do not do this.
* **Observed flat curve** - v(r) approaches a constant v_flat at large r. v_flat is set by total enclosed mass (mostly dark halo). Typical v_flat is 150-300 km/s.
* **Tully-Fisher relation** - L proportional to v_flat^4 for spirals. Tight enough to use as a sanity check or as a generator: pick v_flat, derive luminosity.
* **Faber-Jackson relation** - same shape for ellipticals using stellar velocity dispersion sigma instead of rotation. L proportional to sigma^4.

## Stellar populations

Per-particle color and luminosity. Visual fidelity lives here.

* **IMF (initial mass function)** - Salpeter: dN/dM proportional to M^-2.35 for M > 0.5 M_sun. Most stars are low-mass red; rare massive stars dominate the luminosity and color in young populations.
* **HR diagram** - luminosity vs. temperature. Main sequence holds 90% of stars; giants and white dwarfs are separate branches. "Main sequence + a tail of giants" covers the visual budget.
* **Mass-luminosity** - L proportional to M^3.5 on the main sequence. A 10 M_sun star is 3000x brighter than the Sun.
* **Color-age coupling** - young populations are blue (hot massive stars still alive), old populations are red (only red dwarfs and red giants left). Spiral arms are blue because stars form there now. Ellipticals are red because they stopped forming stars long ago.

## Star formation, AGN, mergers

* **Jeans / Schmidt-Kennicutt** - star formation tracks cold dense gas. Spiral arms compress gas, hence the blue arms. SFR density proportional to gas density^1.4.
* **Feedback** - supernovae and stellar winds blow gas back out, quenching further formation. The term to add when star-forming regions look "too efficient".
* **SMBH + M-sigma** - every massive galaxy has a central black hole (10^6 to 10^10 M_sun) tightly scaling with bulge velocity dispersion. Sample directly from bulge mass.
* **AGN** - 1-10% of massive galaxies are actively accreting. Visual budget: a bright central pixel plus an optional thin jet.
* **Mergers** - major (> 1:3) destroy disks and produce ellipticals, with tidal tails as the mid-merger signature. Minor mergers leave the disk intact but seed halo streams.

## Common design pitfalls in procedural galaxy sims

These are the ones that produce galaxies that look wrong to anyone who has seen real images.

* **Spiral arms as material structures.** Arms are density waves; stars pass through them. Modeling arms as fixed-stellar-content "spokes" makes them rotate as rigid bodies and look wrong over time. Use a static or slowly-rotating logarithmic spiral as a density modulation, not as a stellar membership.
* **Uniform stellar color.** Real galaxies show clear color gradients (bluer toward arms / outskirts, redder toward bulge). Even a coarse age gradient fixes this.
* **No dark halo, sharp light cutoff.** Without a halo, stellar orbits at large radii are wrong. Even if dark matter is invisible, the rotation curve it produces is not.
* **All galaxies same scale.** Real galaxy luminosities span 5+ orders of magnitude (dwarfs to giants). A flat distribution looks fake. Sample from the Schechter luminosity function (a power-law with an exponential cutoff at high luminosity).
* **AGN on every galaxy.** Most galaxies are not active. Sampling AGN on every nucleus makes the universe too bright.

## Numerical hooks for Rust/WASM

* **Particle budget** - 10^4 to 10^5 particles per galaxy is realistic for WASM in a vertex buffer. Real galaxies have 10^10+ stars, so each particle is a luminosity-weighted sample. Weight matters more than count.
* **Sampling** - exponential disk, Sersic, and Salpeter IMF all have inverse CDFs. NFW does not; use rejection or a lookup table.
* **Spiral arms as a phase field** - theta_arm(R) = theta_0 + ln(R/R_0) / tan(pitch). Modulate density by cos(N (theta - theta_arm)) for an N-armed spiral. Density modulation, not stellar membership.
* **Color from temperature** - blackbody color from stellar effective temperature is a standard lookup. Precompute at build time.

## Concept reference

Verbatim Wikipedia lead paragraphs (CC BY-SA 4.0) for every concept above live in [`references/wikipedia-concepts.md`](references/wikipedia-concepts.md). Reach there when a term needs a precise definition before deciding how to model it.

## Sources

Synthesized from public skills, originals are richer if a topic needs depth:

* [luokai0/astrophysics-expert](https://github.com/luokai0/ai-agent-skills-by-luo-kai/tree/main/ai-agent-skills/15-earth-and-space-sciences%20%28by%20Luo%20Kai%29/astrophysics-expert) - stellar physics, galaxy formation, high-energy.
* [sandraschi/astronomy-astrophysics-expert](https://github.com/sandraschi/advanced-memory-mcp/tree/master/skill-zips/astronomy-astrophysics-expert/astronomy-astrophysics-expert) - mission data + observational context.
* [CaelanDrayer/astronomer](https://github.com/CaelanDrayer/cAgents/tree/main/analyst/astronomer) - celestial mechanics + observational framing.
