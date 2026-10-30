"""QE 7.5 example inputs; materialized only inside owned run directories."""
import pathlib
import re
from .core import ROOT
INPUTS_DIR = ROOT / "inputs"
PP_DIR = ROOT / "cases/common/pp"

def replace_pseudo_dir(content: str) -> str:
    return re.sub(r"pseudo_dir\s*=\s*'[^']*'", f"pseudo_dir='{PP_DIR}'", content)

def replace_prefix_and_outdir(content: str, prefix: str, outdir: str) -> str:
    content = re.sub(r"prefix\s*=\s*'[^']*'", f"prefix='{prefix}'", content)
    content = re.sub(r"outdir\s*=\s*'[^']*'", f"outdir='{outdir}'", content)
    return content

def write_inputs(input_dir: pathlib.Path) -> dict[str, pathlib.Path]:
    mapping: dict[str, pathlib.Path] = {}
    for name in [
        "Si.scf.in",
        "Si.bands.in",
        "Si.bands_post.in",
        "Si.nscf.in",
        "Si.dos.in",
        "Si.projwfc.in",
    ]:
        src = INPUTS_DIR / name
        dst = input_dir / name
        content = src.read_text(encoding="utf-8")
        if "pseudo_dir" in content:
            content = replace_pseudo_dir(content)
        dst.write_text(content, encoding="utf-8")
        mapping[name] = dst

    # Additional generated inputs used by the validation campaign.
    pp_in = input_dir / "Si.pp.in"
    pp_in.write_text(
        "&inputpp\n"
        "  prefix='silicon',\n"
        "  outdir='./tmp',\n"
        "  filplot='silicon.rho',\n"
        "  plot_num=0\n"
        "/\n"
        "&plot\n"
        "  nfile=1,\n"
        "  filepp(1)='silicon.rho',\n"
        "  weight(1)=1.0,\n"
        "  iflag=3,\n"
        "  output_format=6,\n"
        "  fileout='silicon_rho.cube'\n"
        "/\n",
        encoding="utf-8",
    )
    mapping["Si.pp.in"] = pp_in

    scf_ph_in = input_dir / "Si.scf_ph.in"
    scf_ph_in.write_text(
        "&control\n"
        "  calculation='scf', prefix='siliconph', pseudo_dir='" + str(PP_DIR) + "', outdir='./tmp_ph'\n"
        "/\n"
        "&system\n"
        "  ibrav=2, celldm(1)=10.26, nat=2, ntyp=1, ecutwfc=30.0, ecutrho=240.0,\n"
        "  occupations='fixed'\n"
        "/\n"
        "&electrons\n"
        "  conv_thr=1.0d-8, mixing_beta=0.7\n"
        "/\n"
        "ATOMIC_SPECIES\n"
        " Si 28.085 Si.pbe-n-rrkjus_psl.1.0.0.UPF\n"
        "ATOMIC_POSITIONS crystal\n"
        " Si 0.00 0.00 0.00\n"
        " Si 0.25 0.25 0.25\n"
        "K_POINTS automatic\n"
        " 8 8 8  0 0 0\n",
        encoding="utf-8",
    )
    mapping["Si.scf_ph.in"] = scf_ph_in

    ph_in = input_dir / "Si.ph.in"
    ph_in.write_text(
        "&inputph\n"
        " tr2_ph=1.0d-14,\n"
        " prefix='siliconph',\n"
        " outdir='./tmp_ph',\n"
        " amass(1)=28.085,\n"
        " fildyn='siliconph.dynG'\n"
        "/\n"
        "0.0 0.0 0.0\n",
        encoding="utf-8",
    )
    mapping["Si.ph.in"] = ph_in

    ph_grid = input_dir / "Si.ph_grid.in"
    ph_grid.write_text(
        "&inputph\n"
        " tr2_ph=1.0d-14,\n"
        " prefix='siliconph',\n"
        " outdir='./tmp_ph',\n"
        " amass(1)=28.085,\n"
        " ldisp=.true.,\n"
        " nq1=1,\n"
        " nq2=1,\n"
        " nq3=1,\n"
        " fildyn='siliconph_grid.dyn'\n"
        "/\n",
        encoding="utf-8",
    )
    mapping["Si.ph_grid.in"] = ph_grid

    q2r = input_dir / "Si.q2r.in"
    q2r.write_text(
        "&input\n"
        "  fildyn = 'siliconph_grid.dyn'\n"
        "  zasr = 'simple'\n"
        "  flfrc = 'silicon.fc'\n"
        "/\n",
        encoding="utf-8",
    )
    mapping["Si.q2r.in"] = q2r

    matdyn = input_dir / "Si.matdyn.in"
    matdyn.write_text(
        "&input\n"
        "  asr='simple'\n"
        "  flfrc='silicon.fc'\n"
        "  flfrq='silicon.freq'\n"
        "  q_in_cryst_coord=.true.\n"
        "/\n"
        "1\n"
        "0.0 0.0 0.0\n",
        encoding="utf-8",
    )
    mapping["Si.matdyn.in"] = matdyn

    hp_scf = input_dir / "Si.hp.scf.in"
    hp_scf.write_text(
        "&control\n"
        "  calculation='scf',\n"
        "  prefix='sihp',\n"
        "  pseudo_dir='" + str(PP_DIR) + "',\n"
        "  outdir='./tmp_hp'\n"
        "/\n"
        "&system\n"
        "  ibrav=2, celldm(1)=10.26, nat=2, ntyp=1,\n"
        "  ecutwfc=30.0, ecutrho=240.0,\n"
        "  occupations='fixed'\n"
        "/\n"
        "&electrons\n"
        "  conv_thr=1.0d-8, mixing_beta=0.7\n"
        "/\n"
        "ATOMIC_SPECIES\n"
        " Si 28.085 Si.pbe-n-rrkjus_psl.1.0.0.UPF\n"
        "ATOMIC_POSITIONS crystal\n"
        " Si 0.00 0.00 0.00\n"
        " Si 0.25 0.25 0.25\n"
        "K_POINTS automatic\n"
        " 4 4 4 0 0 0\n"
        "HUBBARD (ortho-atomic)\n"
        "U Si-3p 1.0\n",
        encoding="utf-8",
    )
    mapping["Si.hp.scf.in"] = hp_scf

    hp_in = input_dir / "Si.hp.in"
    hp_in.write_text(
        "&inputhp\n"
        "  prefix='sihp'\n"
        "  outdir='./tmp_hp'\n"
        "  nq1=1\n"
        "  nq2=1\n"
        "  nq3=1\n"
        "  determine_num_pert_only=.true.\n"
        "/\n",
        encoding="utf-8",
    )
    mapping["Si.hp.in"] = hp_in

    neb_in = input_dir / "Si.neb.in"
    neb_in.write_text(
        "BEGIN\n"
        "BEGIN_PATH_INPUT\n"
        "&PATH\n"
        "  restart_mode='from_scratch',\n"
        "  string_method='neb',\n"
        "  nstep_path=5,\n"
        "  num_of_images=3,\n"
        "  opt_scheme='quick-min',\n"
        "  ds=1.0d0,\n"
        "/\n"
        "END_PATH_INPUT\n"
        "\n"
        "BEGIN_ENGINE_INPUT\n"
        "&CONTROL\n"
        "  calculation='scf',\n"
        "  prefix='sineb',\n"
        "  pseudo_dir='" + str(PP_DIR) + "',\n"
        "  outdir='./tmp_neb',\n"
        "  tprnfor=.true.\n"
        "/\n"
        "&SYSTEM\n"
        "  ibrav=2, celldm(1)=10.26,\n"
        "  nat=2, ntyp=1,\n"
        "  ecutwfc=30.0, ecutrho=240.0,\n"
        "  occupations='fixed'\n"
        "/\n"
        "&ELECTRONS\n"
        "  conv_thr=1.0d-7,\n"
        "  mixing_beta=0.7\n"
        "/\n"
        "ATOMIC_SPECIES\n"
        " Si 28.085 Si.pbe-n-rrkjus_psl.1.0.0.UPF\n"
        "K_POINTS automatic\n"
        " 2 2 2 0 0 0\n"
        "\n"
        "BEGIN_POSITIONS\n"
        "FIRST_IMAGE\n"
        "ATOMIC_POSITIONS crystal\n"
        " Si 0.00 0.00 0.00\n"
        " Si 0.25 0.25 0.25\n"
        "INTERMEDIATE_IMAGE\n"
        "ATOMIC_POSITIONS crystal\n"
        " Si 0.00 0.00 0.00\n"
        " Si 0.30 0.25 0.25\n"
        "LAST_IMAGE\n"
        "ATOMIC_POSITIONS crystal\n"
        " Si 0.00 0.00 0.00\n"
        " Si 0.35 0.25 0.25\n"
        "END_POSITIONS\n"
        "END_ENGINE_INPUT\n"
        "END\n",
        encoding="utf-8",
    )
    mapping["Si.neb.in"] = neb_in

    epw_scf = input_dir / "Si.epw.scf.in"
    epw_scf.write_text(
        "&control\n"
        " calculation='scf',\n"
        " prefix='siepw',\n"
        " pseudo_dir='" + str(PP_DIR) + "',\n"
        " outdir='./tmp_epw',\n"
        " verbosity='high',\n"
        " wf_collect=.true.\n"
        "/\n"
        "&system\n"
        " ibrav=2,\n"
        " celldm(1)=10.26,\n"
        " nat=2,\n"
        " ntyp=1,\n"
        " ecutwfc=30.0,\n"
        " ecutrho=240.0,\n"
        " occupations='fixed',\n"
        " nbnd=8\n"
        "/\n"
        "&electrons\n"
        " conv_thr=1.0d-10,\n"
        " mixing_beta=0.7\n"
        "/\n"
        "ATOMIC_SPECIES\n"
        " Si 28.085 Si.pbe-n-rrkjus_psl.1.0.0.UPF\n"
        "ATOMIC_POSITIONS crystal\n"
        " Si 0.00 0.00 0.00\n"
        " Si 0.25 0.25 0.25\n"
        "K_POINTS automatic\n"
        " 2 2 2 0 0 0\n",
        encoding="utf-8",
    )
    mapping["Si.epw.scf.in"] = epw_scf

    epw_nscf = input_dir / "Si.epw.nscf.in"
    epw_nscf.write_text(
        "&control\n"
        " calculation='nscf',\n"
        " prefix='siepw',\n"
        " pseudo_dir='" + str(PP_DIR) + "',\n"
        " outdir='./tmp_epw',\n"
        " wf_collect=.true.\n"
        "/\n"
        "&system\n"
        " ibrav=2,\n"
        " celldm(1)=10.26,\n"
        " nat=2,\n"
        " ntyp=1,\n"
        " ecutwfc=30.0,\n"
        " ecutrho=240.0,\n"
        " occupations='fixed',\n"
        " nbnd=8\n"
        "/\n"
        "&electrons\n"
        " conv_thr=1.0d-10,\n"
        " mixing_beta=0.7\n"
        "/\n"
        "ATOMIC_SPECIES\n"
        " Si 28.085 Si.pbe-n-rrkjus_psl.1.0.0.UPF\n"
        "ATOMIC_POSITIONS crystal\n"
        " Si 0.00 0.00 0.00\n"
        " Si 0.25 0.25 0.25\n"
        "K_POINTS crystal\n"
        "8\n"
        "0.0000000000 0.0000000000 0.0000000000 0.1250000000\n"
        "0.0000000000 0.0000000000 0.5000000000 0.1250000000\n"
        "0.0000000000 0.5000000000 0.0000000000 0.1250000000\n"
        "0.0000000000 0.5000000000 0.5000000000 0.1250000000\n"
        "0.5000000000 0.0000000000 0.0000000000 0.1250000000\n"
        "0.5000000000 0.0000000000 0.5000000000 0.1250000000\n"
        "0.5000000000 0.5000000000 0.0000000000 0.1250000000\n"
        "0.5000000000 0.5000000000 0.5000000000 0.1250000000\n",
        encoding="utf-8",
    )
    mapping["Si.epw.nscf.in"] = epw_nscf

    epw_win = input_dir / "siepw.win"
    epw_win.write_text(
        "num_wann = 4\n"
        "num_bands = 8\n"
        "dis_win_max = 20.0\n"
        "dis_froz_max = 10.0\n"
        "iprint = 2\n"
        "conv_tol = 1.0d-10\n"
        "begin unit_cell_cart\n"
        "bohr\n"
        " -5.1300000000  0.0000000000  5.1300000000\n"
        "  0.0000000000  5.1300000000  5.1300000000\n"
        " -5.1300000000  5.1300000000  0.0000000000\n"
        "end unit_cell_cart\n"
        "begin atoms_frac\n"
        " Si 0.000000 0.000000 0.000000\n"
        " Si 0.250000 0.250000 0.250000\n"
        "end atoms_frac\n"
        "begin projections\n"
        " Si:sp3\n"
        "end projections\n"
        "mp_grid = 2 2 2\n"
        "begin kpoints\n"
        " 0.0000000000 0.0000000000 0.0000000000\n"
        " 0.0000000000 0.0000000000 0.5000000000\n"
        " 0.0000000000 0.5000000000 0.0000000000\n"
        " 0.0000000000 0.5000000000 0.5000000000\n"
        " 0.5000000000 0.0000000000 0.0000000000\n"
        " 0.5000000000 0.0000000000 0.5000000000\n"
        " 0.5000000000 0.5000000000 0.0000000000\n"
        " 0.5000000000 0.5000000000 0.5000000000\n"
        "end kpoints\n",
        encoding="utf-8",
    )
    mapping["siepw.win"] = epw_win

    epw_pw2wan = input_dir / "Si.epw.pw2wan.in"
    epw_pw2wan.write_text(
        "&inputpp\n"
        " outdir='./tmp_epw',\n"
        " prefix='siepw',\n"
        " seedname='siepw',\n"
        " write_amn=.true.,\n"
        " write_mmn=.true.,\n"
        " write_unk=.false.\n"
        "/\n",
        encoding="utf-8",
    )
    mapping["Si.epw.pw2wan.in"] = epw_pw2wan

    epw_in = input_dir / "Si.epw.in"
    epw_in.write_text(
        "&inputepw\n"
        " prefix='siepw',\n"
        " amass(1)=28.085,\n"
        " outdir='./tmp_epw',\n"
        " elph=.false.,\n"
        " ep_coupling=.false.,\n"
        " epwwrite=.true.,\n"
        " epwread=.false.,\n"
        " nbndsub=4,\n"
        " wannierize=.false.,\n"
        " num_iter=10,\n"
        " iprint=2,\n"
        " dis_win_max=20.0,\n"
        " dis_froz_max=10.0,\n"
        " proj(1)='f=0,0,0:l=-3',\n"
        " elecselfen=.false.,\n"
        " phonselfen=.false.,\n"
        " a2f=.false.,\n"
        " nk1=2,\n"
        " nk2=2,\n"
        " nk3=2,\n"
        " nq1=1,\n"
        " nq2=1,\n"
        " nq3=1\n"
        "/\n",
        encoding="utf-8",
    )
    mapping["Si.epw.in"] = epw_in
    return mapping
