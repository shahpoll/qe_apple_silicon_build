# Results Gallery

Key artefacts from the silicon (Si) validation run.

## Band structure

![Si band structure](../../cases/si/manual/plots/si_band_structure.png)

- Path: Γ → X → W → K → Γ → L (40 points per segment).
- Energies referenced to the DOS-derived E_F (red dashed line at 0 eV).

## Total DOS

![Si DOS](../../cases/si/manual/plots/si_total_dos.png)

- Derived from the 12×12×12 NSCF run + `dos.x` (`ngauss=0`, `degauss=1.47 meV`).
- Energy range: –15 to 20 eV with ΔE = 0.02 eV, referenced to E_F.

## Projected DOS (s/p channels)

![Si PDOS](../../cases/si/manual/plots/si_pdos.png)

- Aggregated s and p contributions for the two Si atoms (`nbnd = 36`).
- Generated with `projwfc.x` and plotted via `plot_si_pdos.py`; zero energy denotes E_F.

## Band-gap summary (`si_band_summary.txt`)

```
# Silicon band summary (derived from silicon.bands.dat.gnu)
Fermi level (from silicon.dos)  :   6.2200 eV
Valence band maximum            :   6.2198 eV at k-index 0 (s = 0.0000)
Conduction band minimum         :   6.7897 eV at k-index 34 (s = 0.8500)
Indirect gap (Cmin - Vmax)      :   0.5699 eV
Direct gap (min over k)         :   2.5598 eV at k-index 0 (s = 0.0000)
```

These metrics are produced by `cases/common/scripts/analyze_si_bandgap.py` (invoked via the local wrapper).
