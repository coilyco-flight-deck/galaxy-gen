---
name: coding-galaxy-gen-references
description: External reference resources for the galaxy sim - real-galaxy catalogs, N-body library design references, Astropy primitives worth mirroring. Use when the sim needs a real-world parameter or validation. Triggers - NASA ADS, SIMBAD, NED, astropy, FITS, sky survey, REBOUND, GADGET, n-body simulation, galaxy catalog, SDSS, GAIA, JWST, Hubble.
---

# References for galaxy-gen

Repo: [coilysiren/galaxy-gen](https://github.com/coilyco-flight-deck/galaxy-gen). Sister skills: [`coding-galaxy-gen-astrophysics`](../coding-galaxy-gen-astrophysics/SKILL.md) (galaxy-scale physics), [`coding-galaxy-gen-cosmology`](../coding-galaxy-gen-cosmology/SKILL.md) (universe-scale physics).

This skill is about pointers, not theory. Use it when the sim needs a number from the real universe, or when you want to look at how a battle-tested gravitational simulator handles a problem instead of redesigning it yourself.

## When to reach for real data

Three honest cases for a procedural sim:

* **Picking defaults.** "What is a reasonable disk scale length for an Sb spiral?" 3.5 kpc. Could just hardcode it, but if you want a range, real catalogs have one.
* **Sanity-checking output.** "Does my generated rotation curve look like NGC 3198's?" Plot real curves over your sim curves. Plenty published.
* **Validation gallery.** "What does a real Sbc galaxy look like?" SDSS gallery, Hubble Legacy Archive, JWST. Free, indexed.

You almost never want to ingest real FITS files into a procedural sim. The astrophysics-data-guide content is for analysis pipelines, not generators.

## Literature lookup: NASA ADS

The bibliographic database for astronomy. Indispensable for "what does the literature say about X galaxy property". Free API, 3000 requests/day.

* **Register for a token** - https://ui.adsabs.harvard.edu/user/settings/token (free, no expiry).
* **Auth** - `Authorization: Bearer $ADS_API_TOKEN` header. Keep the token out of the repo (env var, secret store, or `.env` listed in `.gitignore`).
* **Search endpoint** - `GET https://api.adsabs.harvard.edu/v1/search/query?q=...&fl=title,author,year,bibcode,citation_count&rows=10&sort=citation_count+desc`.
* **Object search** - `q=object:"M31"` returns papers about a specific galaxy. Useful when copying real-galaxy parameters into the sim.
* **Docs** - https://ui.adsabs.harvard.edu/help/api/

For galaxy-gen specifically, ADS is overkill for routine work. It is the right reach when picking sim defaults from published surveys (e.g. "what is the Schechter function's M_star value in the local universe").

## Catalogs and image archives

When picking real galaxies to study as visual reference, or copying parameters from observed populations.

* **SDSS (Sloan Digital Sky Survey)** - https://skyserver.sdss.org/ - the biggest public galaxy catalog. Photometry, spectra, morphology. Galaxy Zoo classifications are derived from SDSS.
* **GAIA** - stellar catalog for the Milky Way. 1.8 billion stars with parallax, proper motion, color. Use for Milky Way-shaped scenes specifically.
* **NED (NASA Extragalactic Database)** - https://ned.ipac.caltech.edu/ - the canonical reference for any named galaxy. Multi-wavelength photometry, redshift, classification.
* **SIMBAD** - http://simbad.u-strasbg.fr/simbad/ - same idea but covers all object types. Better for stellar / Galactic objects.
* **Hubble Legacy Archive** - https://hla.stsci.edu/ - reference imagery. The pretty pictures.
* **JWST archives** - https://archive.stsci.edu/missions-and-data/jwst - higher-resolution successors to Hubble. Especially relevant for high-z morphology if the sim renders early-universe galaxies.

## Astropy: what is worth knowing

The Python astronomy library. Mostly irrelevant for a Rust/WASM sim, but a few primitives are worth recognizing when comparing notes.

* **astropy.coordinates** - the standard for sky-coordinate transformations (ICRS, Galactic, ecliptic, alt-az). If the sim ever maps a real galaxy onto its sky, Astropy is the reference implementation.
* **astropy.units** - dimensional analysis with units. The right model for any "physical-units" type in the Rust side (kpc, M_sun, km/s, etc.). Don't port it; just mirror the convention.
* **astropy.cosmology** - canned LCDM cosmology. `cosmology.lookback_time(z)`, `cosmology.luminosity_distance(z)`. Same integrals the sim needs in `coding-galaxy-gen-cosmology`. Cross-check sim lookup tables against Astropy output once.
* **FITS** - the standard data format. Skip unless ingesting real catalogs. The sim does not need to emit FITS.

## N-body simulation libraries: design references

If galaxy-gen ever moves from "static sampling" to "time-evolved gravitational dynamics", the wheel has been built many times. Read the design, do not necessarily port it.

* **REBOUND** - https://rebound.readthedocs.io/ - C library with Python bindings. Symplectic integrators (WHFast, IAS15) optimized for celestial mechanics. Small-N, high-accuracy. The right reference if galaxy-gen ever simulates stellar orbits in a galactic potential.
* **GADGET-4** - https://wwwmpa.mpa-garching.mpg.de/gadget4/ - the production cosmological N-body + SPH simulator. Tree + particle-mesh for gravity, SPH for gas. Massive scale (millions to billions of particles). The reference for "how would the pros do this".
* **AREPO** - moving-mesh hydro alternative to GADGET. Used for the IllustrisTNG simulation suite. Visually striking but probably overkill for a browser sim.
* **Galpy** - https://github.com/jobovy/galpy - pure-Python galactic-dynamics library. Lighter than GADGET, focused on stellar orbits in analytic potentials. Closest in scope to what a browser galaxy sim would do.

Useful patterns to lift from these:

* **Tree codes (Barnes-Hut)** - O(N log N) gravity. Threshold the box-opening angle theta; cells too far to resolve get treated as point masses. Maps cleanly to a WASM implementation.
* **Particle-mesh (PM)** - FFT-based. O(N log N) via Poisson solve on a grid. Right for cosmological-scale sims, overkill for single-galaxy.
* **Symplectic integrators** - preserve energy over long integrations. Leapfrog is the simplest; KDK (kick-drift-kick) is the standard. Use over RK4 for anything orbiting.

## Computational-physics framing for galaxy-gen

Beyond N-body specifically, the broader comp-physics methods inventory has a few relevant entries:

* **Particle-in-cell (PIC)** - if galaxy-gen ever models galactic-scale magnetic-field-driven plasma (probably not for a procedural sim).
* **SPH (smoothed-particle hydrodynamics)** - gas dynamics as particles. Used in GADGET. Relevant if the sim renders gas/dust as physical, not as a texture.
* **Adaptive mesh refinement (AMR)** - grid-based hydro that refines near density gradients. Different paradigm; not needed for a particle-only sim.

For a procedural sim that fakes most of this with sampling + visual approximations, treat these as a reference vocabulary for any future "make it more realistic" pivot.

## When this skill stops being useful

The moment galaxy-gen commits to a real-time interactive procedural sim with a fixed visual budget (browser, single galaxy in view), most of the above becomes overkill. The astrophysics + cosmology skills are the active references. Reach here only when picking defaults, validating output, or designing a dynamics layer.

## Sources

* [wentorai/physics-skills](https://github.com/wentorai/research-plugins/tree/main/skills/domains/physics) - the bundle the adjacent content came from. Includes astrophysics-data-guide (Astropy/FITS), nasa-ads-api (full API guide), and computational-physics-guide (MD/MC/N-body taxonomy).
* NASA ADS, SDSS, GAIA, NED, SIMBAD, Hubble Legacy, JWST archive - linked inline above.
* REBOUND, GADGET-4, AREPO, Galpy - linked inline above. None pulled into the repo; these are reference targets.
