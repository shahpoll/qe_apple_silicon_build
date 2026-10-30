# Pseudopotential identity and convergence

The canonical silicon regression uses the checked-in `cases/common/pp/Si.pbe-n-rrkjus_psl.1.0.0.UPF`, SHA256 `669fb75395a9d26973b0ea1ce8223bbcb30d3396c5d48bf5e794d1243c52375a`. Validators check its hash and do not download over it.

30/240 Ry is a historical regression setting, not a general accuracy recommendation. The separate 50/400 Ry, 12³ study uses declared silicon energy/path-gap budgets against 80/800 Ry, 16³. Its first run was superseded after a warning-policy review; the new strict OpenBLAS rerun passed the original budget, with exact results in the external evidence report. Other observables and materials need their own convergence study.

For upstream numerical references, a familiar filename is insufficient: the exact benchmark MD5 must match. Newly downloaded or converted files can differ from the archived reference. Preserve mismatches, obtain an authenticated matching file, and keep dependent cases BLOCKED until then. Changing a pseudopotential creates a new model variant and requires requalification.
