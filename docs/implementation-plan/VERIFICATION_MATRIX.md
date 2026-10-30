# Qualification cases and supported calculation scope

These are proposed acceptance contracts, not completed tests. W00 must expand each family into exact case IDs with input/reference hashes, numerical limits, resource budgets and required artifacts. A family name alone cannot satisfy a release gate. All negative cases require the intended typed rejection and a preserved failure record; an unrelated exception does not count as detection.

**Profiles and coverage**

| Profile | Required scope | Permitted claim |
|---|---|---|
| Harness CI | Applicable H cases and synthetic I cases | Validator/runner logic behaves as specified; no QE physics claim |
| Install smoke | Exact-binary preflight, reviewed seed S01, serial/direct and explicitly selected MPI check | This configuration loads and executes this small fixture correctly |
| Core release | All H/I cases relevant to the packaged product; S01–S03, S07–S11, R01–R07 and their prerequisite cases | Core PW/postprocessing/phonon workflows verified for listed combinations |
| Workstation release | Core plus S04–S06, S12–S13, S20 and documented S18/S19 admission/convergence behavior | Common electronic, structural, path, nonbulk and dynamics modes verified as listed |
| Comprehensive workstation — final target | Workstation plus S14–S17; every advertised optional-module executable mapped to a real numerical case | Broad declared QE suite support, with exact feature/configuration coverage |
| Production study | The selected supported workflow plus system-specific S18 convergence/error-budget work | The chosen observable meets its stated numerical target under its stated model |

A module that is not selected may remain visibly UNTESTED/UNSUPPORTED. A selected module is mandatory for that profile; its absence blocks that profile. Completing core alone does not complete this project's comprehensive target. Profile names do not imply every possible cross-product of functional, spin, UPF, boundary condition and module is supported. Build a feature-combination registry and add a fixture before advertising a new combination. Unsupported external plugins are separate extension work, not silently counted as present.

**H: adversarial validator and execution cases**

| ID | Exact scenario to exercise | Required observation |
|---|---|---|
| H01 | NaN/Inf/-Inf, overflow notation, missing numeric values and malformed numbers in each supported parser | Nonfinite/parse reason; no tolerance PASS, fake zero, or nonstandard JSON NaN |
| H02 | Good-looking energy without completion; explicit nonconvergence with JOB DONE; first value differs from final; truncated/concatenated calculations | Calculation-specific rejection or correct final-state extraction; a legitimate complete control passes |
| H03 | Audit +5 Ry baseline error and 1 Ry rank/repeat spreads; identical wrong values across ranks; a single outlier among repeats | Reference and peer gates each work independently; nonzero campaign result |
| H04 | Missing DOS/EF/reference/artifact, parser exception, failed prerequisite | Named failed/error/blocked predicate and preserved report; no hidden ERROR TSV with overall success |
| H05 | Empty/duplicate-only ranks, nonpositive ranks, inadequate repeats, omitted expected case | Invalid/incomplete profile cannot PASS |
| H06 | Request 4 ranks, observe 1 or unknown; serial binary or fallback under MPI request | MPI capability fails/blocks regardless of numerical match |
| H07 | Initial application failure then successful retry; old energy plus new completion; transient pre-launch failure plus genuine recovery | Original failure preserved; mixed evidence rejected; only a policy-authorized diagnosed transient can yield recovered case PASS |
| H08 | Old valid plot inputs, wrong parent hashes, overwritten NSCF data, mismatched grids/UPFs, artifacts from another attempt | Freshness/ancestry checks reject; correct same-run parent accepted. Subcases: `.scratch`, `.parser`, `.workflow` |
| H09 | Output path is root/home/checkout/ancestor, symlink escape or unrelated populated directory | Sentinels unchanged; operation refused before deletion |
| H10 | Hung child/process group, legitimate quiet work, interrupted journal, report-write error, disk full | Typed timeout/error; correct cleanup; durable partial evidence or explicit inability to save; no false completion. Subcases: `.journal`, `.process`, `.ci` |
| H11 | Duplicate/missing case records, unknown schema, corrupted hashes, nonfinite JSON, untracked source change | Evidence invalidation and non-success, including fingerprint of newly added files |
| H12 | Values exactly at and just inside/outside limits; near-zero reference; unit/grid mismatch; spectral scale/shift alteration | Correct documented boundary behavior; invalid comparison rejected before subtraction |
| H13 | Conflicting QE selectors, inherited thread/library environment, wrong launcher or mixed module paths | Single recorded explicit selection or clear error; all children use controlled configuration |
| H14 | Unknown warnings, known benign version-specific warnings, severe floating-point/error markers, changed output version | Preserve diagnostics; case-specific policy; unknown severe interpretation blocks qualification rather than broad suppression |
| H15 | Planned checkpoint stop, step-limit termination, SIGINT/SIGKILL/power-loss simulation, corrupt/incompatible restart | Checkpoint availability and completion are distinct; interrupted job never PASS; valid compatible restart has linked proof. Subcases: `.state`, `.parser`, `.process`, `.qe` |

For H14, early unconverged eigenvectors or benign diagnostic flags are not automatically fatal in every calculation. Rules must consider the final state and the metric contract. Unknown warning handling must be explicit, reproducible and reviewable.

**I: clean install, upgrade and environmental cases**

| ID | Positive and negative case pair | Required proof |
|---|---|---|
| I01 | Native supported machine versus Rosetta/mixed architecture, missing/stale CLT/SDK | Accurate preflight and actionable block; recorded coherent supported toolchain |
| I02 | Exact valid suite versus invalid/partial explicit path with other installations available | No fallback to another suite; all executable paths/hashes match selected manifest |
| I03 | Valid dependencies versus deliberately missing temporary dylib, wrong architecture or MPI/ABI mismatch | Loader and compatibility checks catch the defect; valid small numerical test still works |
| I04 | Isolated declared Python environment versus no global NumPy/Matplotlib and rendering unavailable | Installed checks function; numerical verdicts do not rely on the user's global packages or plotting |
| I05 | Verified cached/online source and UPF versus HTTP error HTML, partial file, bad hash, changed tag or corrupt extraction | Cache/download is verified atomically; old valid data unaffected by failure |
| I06 | Empty-prefix selected-profile build versus seeded stale executables and omitted build target | Complete expected module set with one build lineage; no borrowed old binary |
| I07 | Bounded successful build versus compile/link failure, killed build or resource exhaustion | No active partial installation; logs identify first causal failure; bounded recovery |
| I08 | First install, same-version reinstall, successful upgrade and rollback versus failed validation/activation/dependency removal | Idempotent declared behavior; usable previous release plus dependency closure; no fabricated rollback guarantee |
| I09 | Concurrent scratch jobs and serialized upgrades versus stale lock/interrupted owner | Independent scratch and safe activation, with process identity verified before cleanup. Subcases: `.scratch-concurrency`, `.activation` |
| I10 | Ordinary path versus spaces/Unicode, read-only package path, offline use and noninteractive shell | Correct argv/path handling and writable run storage; explicit unsupported prerequisites, no silent relocation. Subcases: `.paths`, `.package` |
| I11 | Every public packaged CLI subcommand from an unrelated cwd, compared with source-tree invocation | Delegation resolves correctly and a real numerical check uses the selected suite |
| I12 | Correct actual-source CMake configuration versus literal shell substitution/wrong BLAS path | Existing resolved libraries and known backend; configured/built executable numerically qualified |
| I13 | Admitted job versus unavailable feature combination, inadequate memory/disk or prohibited MPI | Typed admission result, retained input and next action; no quiet shrinking or serial replacement |

Synthetic dependency/download failures must use test-owned fixtures and directories. Do not deliberately break the user's real dependencies to prove detection. Test real upgrade/rollback against isolated staging installations first.

**S: scientific workflow families**

All cases require finite observables, correct units, exact ancestry, successful applicable convergence and reviewed references. The table adds family-specific assertions. It is a proposed test design; choose actual fixture inputs/limits in W00/W13, not from an arbitrary candidate's output. Baseline PW syntax and calculation-specific controls should be checked against the pinned source documentation; the [official PW input reference](https://www.quantum-espresso.org/Doc/INPUT_PW.html) is a current cross-check.

| ID | Required fixture/feature coverage | Additional proof and essential negative control |
|---|---|---|
| S01 | Insulating SCF with separate NC, ultrasoft and PAW fixtures; one authenticated upstream seed | Final-state energy, electron count and selected state metrics; fixed occupations without printed EF handled correctly. Reject false completion/nonfinite output. Early subcases `.seed-parser` and `.seed-comparison` replay reviewed output; `.live` executes QE |
| S02 | Metallic SCF | Match occupation/kernel/broadening, weights, EF and band coverage; converge the target over smearing/mesh. Reject inconsistent occupation or inadequate requested spectral coverage |
| S03 | Collinear magnetic fixture with identified state | Match energy and meaningful magnetization/occupation metrics; test different seeds as separate branches. Convergence to another metastable state cannot silently count as the same solution |
| S04 | Noncollinear and SOC fixtures with suitable relativistic UPFs | Match energy, splittings and magnetic components; use sensible degenerate-state matching. Disabling SOC or substituting a different relativistic model is not an equivalent fallback |
| S05 | DFT+U, with explicit projector/site/U/J/V combinations | Match occupations, state and energy under the same definitions. A changed U/projector is a new model, not an acceptance repair |
| S06 | Separate hybrid, meta-GGA and dispersion fixtures for supported implementations | Check their declared numerical observables and additional convergence variables; hybrid inner/outer convergence and exchange sampling need explicit contracts. Semilocal substitution does not certify a hybrid calculation |
| S07 | Separate ionic relax and vc-relax | Final relevant forces, energy change, constraints and stress/target pressure; finite geometry/positive volume; fresh static final-geometry check. Step-limit stopping must not pass optimization |
| S08 | Uniform NSCF and band-path calculations from a valid SCF parent | Correct k-point/band/spin dimensions and diagonalization outputs; gaps labeled according to sampling. Reject wrong parent or dimension mismatch. `.parser` is archival parser proof; `.live` covers execution |
| S09 | Corrected manual and PWTK DOS/PDOS | Uniform parent, same integration/broadening/grid/bands/window; reviewed spectral residuals and applicable integrals. Inject band-path parent and stale spectra; both must fail |
| S10 | Representative charge-density and other advertised pp.x outputs | Grid, cell, units, field identity and representation-aware integrated quantities. Wrong plot field or missing augmentation treatment must not satisfy a charge-integral contract |
| S11 | PH at Γ and nonzero q; insulating, polar and metallic fixtures; q2r/matdyn chain and PH restart | All requested perturbations/q points complete; mode counts for complete systems; reference mode groups; sampled-q reconstruction using matching masses, ASR and nonanalytic/LO–TO conventions. Polar fixture checks dielectric/Born-charge output and declared directional Γ limit. Raw and corrected data remain distinct |
| S12 | Genuinely converged NEB with a known reference path | Image/endpoint identity, complete profile, converged path residual and finite barrier. The audited step-limited run is a negative convergence control; a printed barrier alone cannot pass |
| S13 | Separate Born–Oppenheimer and Car–Parrinello dynamics; continuous and restarted runs | Requested step count, finite state and applicable electronic work; ensemble/conserved-quantity tests, timestep refinement, CP-specific electronic dynamics. Short deterministic comparisons plus statistical/conservation tests for longer trajectories |
| S14 | Actual HP response/U or U/V fixtures for selected combinations | Required perturbations, finite response/output matrices and derived values within limits. Perturbation counting without response must fail a response-capability claim |
| S15 | Wannier/EPW interpolation and actual electron–phonon coupling | Correct electronic/phonon/Wannier ancestry; interpolation residuals and a coupling-derived reference metric. Coupling disabled or heading-only output fails coupling coverage |
| S16 | Separate selected turbo optical, EELS and magnon workflows and required spectrum tools | Ground-state ancestry, response convergence and actual spectral metrics on declared grids/broadening. Missing spectrum/response or banner-only launch fails |
| S17 | XSpectra and separately all_currents/QEHeat outputs currently advertised by the project | XSpectra: declared absorber/core/polarization model and reviewed spectral metrics without freely fitted shifts. all_currents: adopt an actual version-matched numerical fixture with units and trajectory ancestry. A launch banner cannot close either subcase |
| S18 | Observable-specific convergence harness across representative workflows | Known synthetic direct gap; cutoff/charge-density/mesh/band/smearing ladders, applicable force/stress/phonon/path/time-step studies. Results not meeting the declared convergence target must fail; final sampled point alone is not proof |
| S19 | Unseen supported workflow and unsupported feature combinations | Report exact capability and model/convergence requirements; allow only declared, reviewed case contracts to certify results. Unsupported combinations stay explicit, with preserved inputs and next diagnostics |
| S20 | Isolated molecule and slab/2D fixtures; separate charged/correction/finite-field variants if advertised | Correct boundary/electrostatic model and declared vacuum/cell convergence; reference energy, forces and applicable dipole observables. Insufficient vacuum or incorrect boundary treatment cannot be certified by a bulk-only smoke case |

For S09, finite-window DOS integrals need matching occupations and sufficient coverage; positivity is not a universal rule for every broadening kernel. Atomic PDOS may not sum exactly to total DOS because projection/spilling conventions matter. Use declared conventions from the [DOS input reference](https://www.quantum-espresso.org/Doc/INPUT_DOS.html) and [projection reference](https://www.quantum-espresso.org/Doc/INPUT_PROJWFC.html), not invented universal sum rules.

For S11, distinguish a physically unstable structure from a bad build; retain raw and ASR-corrected outputs separately. For a complete phonon calculation, mode-count checks must match the actual requested system/perturbation scope. Consult the [PH input reference](https://www.quantum-espresso.org/Doc/INPUT_PH.html). For S12, define the converged path requirement from the selected version's controls rather than accepting an exit code or barrier string; see the [NEB input reference](https://www.quantum-espresso.org/Doc/INPUT_NEB.html).

CP-specific numerical parameters and conserved quantities need their own fixtures; PW MD is not a replacement for CP testing. See the [CP input reference](https://www.quantum-espresso.org/Doc/INPUT_CP.html). HP response is distinct from perturbation discovery; see [HP inputs](https://www.quantum-espresso.org/Doc/INPUT_HP.html). EPW interpolation, coupling, mobility and superconductivity are separate claims, each requiring an appropriate fixture; see [EPW inputs](https://docs.epw-code.org/Inputs/Inputs.html). That online page currently describes EPW 6.1, so the implementing agent must use documentation matching the EPW revision bundled with the pinned QE source. Likewise, pin the relevant [turbo response controls](https://www.quantum-espresso.org/Doc/INPUT_Lanczos.html) for S16.

**R: cross-run and cross-build evidence**

| ID | Experiment | Gate |
|---|---|---|
| R01 | Fresh identical reviewed SCF fixture at real ranks 1, 2 and 4 | Correct observed ranks; every result agrees with reference and peers within frozen limits |
| R02 | At least three fresh repeats at selected ranks/threads | Required count present; max deviation/span limits satisfied; original outliers retained |
| R03 | Supported pool/band/thread decompositions, chosen to fit fixture dimensions | Same scientific inputs and correct topology; numerical equivalence; unsupported layout rejected clearly |
| R04 | Identical fixtures on independently validated Accelerate/OpenBLAS builds, plus separate trusted reference provenance | Distinguish toolchain variation from model change; no backend declared correct merely by agreement with itself |
| R05 | Fresh canonical manual and PWTK workflows | Matching input/UPF/parent settings and toleranced outputs; no inherited archives or unapproved scale/shift |
| R06 | Controlled uninterrupted versus valid checkpoint/restart calculations for relevant PW/PH/dynamics families | Matching provenance and declared final observables/continuity; corrupt/incompatible checkpoint rejected. Verify version-specific rank/decomposition and saved-wavefunction restrictions before reuse; execution-layout changes do not automatically preserve compatibility |
| R07 | Finite-difference energy/force and energy/strain/stress checks on suitable simple fixtures | Frozen displacement/strain ladders, consistent constraints/coordinates and units; finite-difference convergence supports sign/scale consistency. Avoid symmetry-forced zero-force-only examples; apply to declared fixtures rather than impose exact universal identities |

**Candidate upstream fixtures already located**

The local QE 7.5 source tree contains these candidate families. W00 must authenticate the pinned upstream source, inspect exact files, choose benchmarks and preserve hashes; local existence is not provenance by itself.

| Coverage | Candidate local families under `q-e-qe-7.5/test-suite/` |
|---|---|
| PW core/pseudopotential/metal/magnetism | `pw_scf`, `pw_pbe`, `pw_uspp`, `pw_pawatom`, `pw_metal`, `pw_lsda` |
| Advanced PW | `pw_noncolin`, `pw_spinorbit`, `pw_lda+U`, `pw_hse`, `pw_b3lyp`, `pw_metaGGA`, `pw_vdw` |
| Structure/workflows/dynamics | `pw_relax`, `pw_vc-relax`, `pw_md`, `pw_workflow_scf_dos`, `pw_workflow_vc-relax_scf` |
| Nonbulk/boundaries | `pw_cluster`, `pw_dipole`; inspect compatible versioned slab/2D examples and `ph_2d` if response is advertised |
| PH | `ph_base`, `ph_metal`, `ph_restart`, `ph_U_insulator_us`, `ph_U_insulator_paw` |
| CP | `cp_si`, `cp_h2o`, `cp_o2` |
| HP | `hp_insulator_us`, `hp_insulator_paw`, `hp_insulator_us_intersiteV` |
| EPW | `epw_base`, `epw_metal`, `epw_polar`, `epw_soc`; additional observable-specific families if advertised |
| TDDFPT | `tddfpt_CH4`, `tddfpt_eels-si`, `tddfpt_magnons_fe` |

Inspect version-matched NEB/XSpectra/QEHeat examples and their benchmark provenance for gaps in the local test families. Do not assume an example includes an automated numerical verdict. Official QE distinguishes its automated tests from examples requiring result inspection; use its [test-suite instructions](https://www.quantum-espresso.org/Doc/user_guide/node15.html) to configure the pinned source's tests, not a guessed universal command.

**Audit cadence and change impact**

| Trigger | Required verification before claiming unchanged support |
|---|---|
| Parser/verdict/runner change | Affected H cases, positive archived controls, relevant real S/R workflow and report reconciliation |
| Input/UPF/reference/tolerance change | New case identity, independent review, affected S/R and observable convergence; no automatic baseline replacement |
| Compiler/MPI/BLAS/FFT/QE change | Fresh candidate; I preflight/build/package, all required profile numerical cases, rank/repeat and independent-reference checks |
| macOS/SDK/hardware change | New platform fingerprint, loader/MPI preflight and required supported-profile qualification; prior platform results remain historical |
| Workflow ordering/output change | H08, related S chain, R05 where applicable, stale-data negative control |
| Installation/upgrade change | I cases, rollback with dependency closure, public-CLI numerical smoke and failure-artifact retention |
| Before every production job | Suite/dependency fingerprint, input/UPF/parent identity, capability and resource admission; do not rerun the entire suite if nothing relevant changed |
| Periodic maintenance | Recheck dependency drift and backup/evidence readability on a documented schedule; full requalification after material drift |

Use quick harness CI for ordinary edits, affected real cases for integration, and the full selected matrix for releases/nightly or scheduled capable-host runs. Avoid treating slow/unavailable CI hardware as an excuse to omit mandatory release checks. Hardware support claims list exactly the chips/OS/toolchains tested; one M-series machine does not prove every generation or OS minor version.

**Final release checklist**

The independent reviewer must verify the frozen expected-case inventory against terminal case results, actual executables/dependencies/ranks, reference provenance, threshold calibration and all evidence hashes. Every mandatory positive case passes; every mandatory adversarial test correctly rejects its target. Required capabilities have no unresolved errors, blocks, unknown limits or missing integration proof. Installed CLI, clean installation, upgrade and dependency-aware rollback all have evidence. The final report lists remaining untested combinations explicitly and separates installation regression from production scientific convergence. Publication remains a subsequent authorized action.
