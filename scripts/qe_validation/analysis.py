"""Ancestry-checked datasets and honest numerical comparison."""
import json
from pathlib import Path
from .core import Campaign, ValidationError, compare_arrays, gaps, read_bands, read_table, sha256, tree_manifest, write_json, last_number, NUMBER

def dataset(base: Path | None) -> dict:
    if base is None:raise ValidationError('DATASET_REQUIRED','Supply --base for a fresh run with dataset.json; bundled historical files are not current results','ERROR')
    file=base/'dataset.json'
    if not file.is_file():raise ValidationError('DATASET_MANIFEST_MISSING',str(file),'BLOCKED')
    manifest=json.loads(file.read_text())
    if manifest.get('state')!='PASS':raise ValidationError('DATASET_NOT_VALID','Dataset workflow is not PASS','BLOCKED')
    actual=tree_manifest(base/'data')
    if actual!=manifest['artifacts']:raise ValidationError('ARTIFACT_HASH_MISMATCH','Dataset artifacts changed or are incomplete','BLOCKED')
    return manifest

def band_summary(base: Path) -> dict:
    manifest=dataset(base)
    grid,bands=read_bands(base/'data/silicon.bands.dat.gnu')
    fermi=last_number((base/'data/silicon.dos').read_text(),rf'EFermi\s*=\s*({NUMBER})','DOS Fermi')
    indirect,direct=gaps(bands,fermi)
    return {'fermi_ev':fermi,'path_sampled_indirect_gap_ev':indirect,'path_sampled_direct_gap_ev':direct,'sampling':manifest['sampling'],'band_count':len(bands),'kpoint_count':len(grid)}

def compare_runs(manual: Path, other: Path, out_dir: Path | None, spectral_atol: float = 1e-5, band_atol: float = 1e-5) -> int:
    a,b=dataset(manual),dataset(other)
    c=Campaign(out_dir,['settings','bands','dos','pdos'],profile='dataset-comparison')
    try:
        def settings(log,work):
            if a['settings']!=b['settings']:raise ValidationError('PHYSICS_MISMATCH','Inputs, UPF, grids, bands, or broadening differ')
        s=c.case('settings',None,validator=settings)
        def bands(log,work):
            xa,ea=read_bands(manual/'data/silicon.bands.dat.gnu');xb,eb=read_bands(other/'data/silicon.bands.dat.gnu')
            rowsa=[[x,*vals] for x,vals in zip(xa,zip(*ea))];rowsb=[[x,*vals] for x,vals in zip(xb,zip(*eb))]
            return {'assertions':[compare_arrays(rowsa,rowsb,atol=band_atol)]}
        c.case('bands',None,validator=bands,blocked='Physics settings differ' if s['state']!='PASS' else None)
        def spectra(name):
            def check(log,work):return {'assertions':[compare_arrays(read_table(manual/'data'/name),read_table(other/'data'/name),atol=spectral_atol)]}
            return check
        c.case('dos',None,validator=spectra('silicon.dos'),blocked='Physics settings differ' if s['state']!='PASS' else None)
        def pdos(log,work):
            names=sorted(p.name for p in (manual/'data').glob('silicon.pdos_*') if not p.name.endswith('projwfc_up'))
            if not names:raise ValidationError('ARTIFACT_MISSING','No PDOS files')
            return {'assertions':[dict(compare_arrays(read_table(manual/'data'/name),read_table(other/'data'/name),atol=spectral_atol),name=name) for name in names]}
        c.case('pdos',None,validator=pdos,blocked='Physics settings differ' if s['state']!='PASS' else None)
    finally:rc=c.finish()
    return rc
