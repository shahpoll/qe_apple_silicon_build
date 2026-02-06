# Thread 7 — Mac mini M4 build attempt (negative result if failed)

**BLAS/LAPACK chosen:** Accelerate+veclibfort (fallback Attempt A uses OpenBLAS)
**MPI:** Homebrew OpenMPI
**Rosetta used:** No

## Packages
cmake 4.1.2
gcc 15.2.0
open-mpi 5.0.8
openblas 0.3.30
veclibfort 0.4.3

## Attempt A — CMake + OpenBLAS
```
=== Attempt A: configure ===
-- The Fortran compiler identification is GNU 15.2.0
-- The C compiler identification is AppleClang 17.0.0.17000013
-- Checking whether Fortran compiler has -isysroot
-- Checking whether Fortran compiler has -isysroot - yes
-- Checking whether Fortran compiler supports OSX deployment target flag
-- Checking whether Fortran compiler supports OSX deployment target flag - yes
-- Detecting Fortran compiler ABI info
-- Detecting Fortran compiler ABI info - done
-- Check for working Fortran compiler: /opt/homebrew/bin/mpif90 - skipped
-- Detecting C compiler ABI info
-- Detecting C compiler ABI info - done
-- Check for working C compiler: /opt/homebrew/bin/mpicc - skipped
-- Detecting C compile features
-- Detecting C compile features - done
-- Setting build type to 'Release' as none was specified
-- Enable sanitizer QE_ENABLE_SANITIZER=none
-- C preprocessor used by qe_preprocess_source in qeHelpers.cmake: /usr/bin/cpp
-- Performing Test Fortran_ISYSTEM_SUPPORTED
-- Performing Test Fortran_ISYSTEM_SUPPORTED - Success
-- Found OpenMP_Fortran: -fopenmp (found version "4.5")
-- Found OpenMP: TRUE (found version "4.5") found components: Fortran
-- Found MPI_Fortran: /opt/homebrew/bin/mpif90 (found version "3.1")
-- Found MPI: TRUE (found version "3.1") found components: Fortran
-- Selected the Fortran 'mpi' module. QE_ENABLE_MPI_MODULE=ON
-- MPI settings used by CTest
     MPIEXEC_EXECUTABLE : /opt/homebrew/bin/mpiexec
     MPIEXEC_NUMPROC_FLAG : -n
     MPIEXEC_PREFLAGS : 
   Tests run as : /opt/homebrew/bin/mpiexec -n <NUM_PROCS>  <EXECUTABLE>
-- Found Git: /opt/homebrew/bin/git (found suitable version "2.50.1", minimum required is "2.13")
-- Source files are cloned from a git repository.
   sed supports -E
   Git branch: HEAD
   Git commit hash: 500de340b820e1cb8c05f2d8bb8fced102f377c1
-- Trying to find LAPACK from ARM Performance Library
-- Found BLAS: /opt/homebrew/opt/openblas/lib/libopenblas.dylib
-- Found LAPACK: /opt/homebrew/opt/openblas/lib/libopenblas.dylib
-- Looking for Fortran zhpev
-- Looking for Fortran zhpev - found
-- Installing Wannier90 via submodule
Submodule 'external/wannier90' (https://github.com/wannier-developers/wannier90.git) registered for path 'external/wannier90'
Cloning into '/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1/external/wannier90'...
From https://github.com/wannier-developers/wannier90
 * branch            1d6b187374a2d50b509e5e79e2cab01a79ff7ce1 -> FETCH_HEAD
Submodule path 'external/wannier90': checked out '1d6b187374a2d50b509e5e79e2cab01a79ff7ce1'
-- Installing MBD via submodule
Submodule 'external/mbd' (https://github.com/libmbd/libmbd.git) registered for path 'external/mbd'
Cloning into '/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1/external/mbd'...
Submodule path 'external/mbd': checked out '89a3cc199c0a200c9f0f688c3229ef6b9a8d63bd'
-- Found Git: /opt/homebrew/bin/git (found version "2.50.1")
-- Setting version tag to 0.13.0-2-g89a3cc1 from Git
-- Installing DeviceXlib via submodule
Submodule 'external/devxlib' (https://gitlab.com/max-centre/components/devicexlib.git) registered for path 'external/devxlib'
Cloning into '/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1/external/devxlib'...
From https://gitlab.com/max-centre/components/devicexlib
 * branch            a6b89ef77b1ceda48e967921f1f5488d2df9226d -> FETCH_HEAD
Submodule path 'external/devxlib': checked out 'a6b89ef77b1ceda48e967921f1f5488d2df9226d'
-- Could NOT find VendorFFTW (missing: VendorFFTW_LIBRARIES VendorFFTW_INCLUDE_DIRS VendorFFTW_ID) 
-- Found PkgConfig: /opt/homebrew/bin/pkg-config (found version "2.5.1")
...
      |                                                                           1
Warning: More actual than formal arguments in procedure call at (1)
[100%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/input.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/loc_scdm_k.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/electrons.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/punch.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/read_file_new.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/wfcinit.f90.o
[100%] Linking Fortran static library ../lib/libqe_pw.a
[100%] Built target qe_pw
[100%] Building Fortran object PW/CMakeFiles/qe_pw_tools_ev_exe.dir/tools/ev.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw_tools_cell2ibrav_exe.dir/tools/cell2ibrav.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw_tools_scan_ibrav_exe.dir/tools/scan_ibrav.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw_tools_pwi2xsf_exe.dir/tools/pwi2xsf.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw_tools_kpoints_exe.dir/tools/kpoints.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw_exe.dir/src/pwscf.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw_tools_ibrav2cell_exe.dir/tools/ibrav2cell.f90.o
[100%] Linking Fortran executable ../bin/pw.x
[100%] Linking Fortran executable ../bin/cell2ibrav.x
[100%] Linking Fortran executable ../bin/ibrav2cell.x
ld: warning: ignoring duplicate libraries: '../lib/libqe_modules.a'
ld: warning: ignoring duplicate libraries: '../lib/libqe_lax.a', '../lib/libqe_modules.a', '../lib/libqe_upflib.a'
ld: warning: ignoring duplicate libraries: '../lib/libqe_modules.a'
[100%] Linking Fortran executable ../bin/scan_ibrav.x
[100%] Linking Fortran executable ../bin/pwi2xsf.x
[100%] Linking Fortran executable ../bin/kpoints.x
[100%] Built target qe_pw_tools_cell2ibrav_exe
[100%] Built target qe_pw_tools_ibrav2cell_exe
[100%] Built target qe_pw_exe
ld: warning: ignoring duplicate libraries: '../lib/libqe_modules.a'
ld: warning: ignoring duplicate libraries: '../lib/libqe_modules.a'
ld: warning: ignoring duplicate libraries: '../lib/libqe_modules.a'
[100%] Built target qe_pw_tools_pwi2xsf_exe
[100%] Built target qe_pw_tools_scan_ibrav_exe
[100%] Built target qe_pw_tools_kpoints_exe
[100%] Linking Fortran executable ../bin/ev.x
ld: warning: ignoring duplicate libraries: '../lib/libqe_modules.a'
[100%] Built target qe_pw_tools_ev_exe
[100%] basic code for scf, structure optimization, MD
[100%] Built target pw
```

## Attempt B — configure + Accelerate
```
=== Attempt B: configure ===
-n directory LAXlib : ok
-n directory FFTXlib/src : ok
-n directory UtilXlib : ok
-n directory dft-d3 : ok
-n directory KS_Solvers/Davidson : ok
-n directory KS_Solvers/Davidson_RCI : ok
-n directory KS_Solvers/CG : ok
-n directory KS_Solvers/PPCG : ok
-n directory KS_Solvers/ParO : ok
-n directory KS_Solvers/DENSE : ok
-n directory KS_Solvers/RMM : ok
-n directory upflib : ok
-n directory XClib : ok
-n directory Modules : ok
-n directory LR_Modules : ok
-n directory PW/src : ok
-n directory CPV/src : ok
-n directory PW/tools : ok
-n directory PP/src : ok
-n directory PWCOND/src : ok
-n directory PHonon/Gamma : ok
-n directory PHonon/PH : ok
-n directory PHonon/FD : ok
-n directory HP/src : ok
-n directory atomic/src : ok
-n directory EPW/src : ok
-n directory EPW/ZG/src : ok
-n directory XSpectra/src : ok
-n directory NEB/src : ok
-n directory TDDFPT/src : ok
-n directory GWW/pw4gww : ok
-n directory GWW/gww : ok
-n directory GWW/head : ok
-n directory GWW/bse : ok
-n directory GWW/simple : ok
-n directory GWW/simple_bse : ok
-n directory GWW/simple_ip : ok
-n directory QEHeat/src : ok
-n directory KCW/src : ok
-n directory KCW/PP : ok

all dependencies updated successfully
checking build system type... aarch64-apple-darwin24.3.0
checking ARCH... mac686
checking setting AR... ... ar
checking setting ARFLAGS... ... ruv
checking for gfortran... gfortran
checking whether the Fortran compiler works... yes
checking for Fortran compiler default output file name... a.out
checking for suffix of executables... 
checking whether we are cross compiling... no
checking for suffix of object files... o
checking whether we are using the GNU Fortran compiler... yes
checking whether gfortran accepts -g... yes
checking for Fortran flag to compile .f90 files... none
checking for mpif90... mpif90
checking whether we are using the GNU Fortran compiler... yes
checking whether mpif90 accepts -g... yes
checking version of mpif90... gfortran 15.2
...
a - read_fhi.o
a - read_ncpp.o
a - read_ps.o
a - read_psml.o
a - read_upf_new.o
a - read_upf_v1.o
a - read_uspp.o
a - spinor.o
a - sph_ind.o
a - sph_bes.o
a - splinelib.o
a - simpsn.o
a - upf_auxtools.o
a - upf_const.o
a - upf_error.o
a - upf_invmat.o
a - upf_io.o
a - upf_ions.o
a - upf_kinds.o
a - upf_params.o
a - upf_parallel_include.o
a - upf_spinorb.o
a - upf_to_internal.o
a - upf_utils.o
a - uspp.o
a - uspp_param.o
a - write_upf_new.o
a - xmltools.o
a - ylmr2.o
a - ylmr2_gpu.o
a - dom.o
a - wxml.o
ranlib -c libupf.a    
ld: warning: ignoring duplicate libraries: '-lvecLibFort'
ld: warning: ignoring duplicate libraries: '-lvecLibFort'
gfortran -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include   -c mbd.F90
mpif90 -g -o virtual_v2.x virtual_v2.o atom.o atomic_number.o dylmr2.o gth.o paw_variables.o pseudo_types.o radial_grids.o read_cpmd.o read_fhi.o read_ncpp.o read_ps.o read_psml.o read_upf_new.o read_upf_v1.o read_uspp.o spinor.o sph_ind.o sph_bes.o splinelib.o simpsn.o upf_auxtools.o upf_const.o upf_error.o upf_invmat.o upf_io.o upf_ions.o upf_kinds.o upf_params.o upf_parallel_include.o upf_spinorb.o upf_to_internal.o upf_utils.o uspp.o uspp_param.o write_upf_new.o xmltools.o ylmr2.o ylmr2_gpu.o dom.o wxml.o -L/opt/homebrew/opt/veclibfort/lib -lvecLibFort -framework Accelerate -L/opt/homebrew/opt/veclibfort/lib -lvecLibFort -framework Accelerate
ld: warning: ignoring duplicate libraries: '-lvecLibFort'
ar -r libmbd.a mbd.o mbd_constants.o mbd_coulomb.o mbd_damping.o mbd_defaults.o mbd_density.o mbd_dipole.o mbd_formulas.o mbd_geom.o mbd_gradients.o mbd_hamiltonian.o mbd_lapack.o mbd_linalg.o mbd_matrix.o mbd_methods.o mbd_rpa.o mbd_scs.o mbd_ts.o mbd_utils.o mbd_version.o mbd_vdw_param.o
ar: creating archive libmbd.a
```

## Errors
Attempt A (tail):
```
[ 91%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/mix_rho.f90.o
[ 94%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/weights.f90.o
[ 94%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/gcscf_input.f90.o
/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1/PW/src/vhpsi_gpu.f90:159:22:

  153 |                       vns_d(1,1,na), ldimax, &
      |                      2
......
  159 |                       wfcU(1,offsetU(na)+1), 2*ldap, rtemp_d, ldimaxt, &
      |                      1
Warning: Type mismatch between actual argument at (1) and actual argument at (2) (COMPLEX(8)/REAL(8)).
/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1/PW/src/vhpsi_gpu.f90:160:30:

  154 |                       proj_r(offsetU(na)+1,1), nwfcU, 0.0_dp, rtemp_d, ldimaxt )
      |                                                              2
......
  160 |                       1.0_dp, hpsi, 2*ldap )
      |                              1
Warning: Type mismatch between actual argument at (1) and actual argument at (2) (COMPLEX(8)/REAL(8)).
/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1/PW/src/vhpsi.f90:382:28:

  379 |                             rvaux,ldimx, projauxr,ldimx, 0.0_dp, rtemp, ldimx)
      |                            2
......
  382 |                             wfcUaux, 2*np, rtemp, ldimx, &
      |                            1
Warning: Type mismatch between actual argument at (1) and actual argument at (2) (COMPLEX(8)/REAL(8)).
/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1/PW/src/vhpsi.f90:383:36:

  379 |                             rvaux,ldimx, projauxr,ldimx, 0.0_dp, rtemp, ldimx)
      |                                                                 2
......
  383 |                             1.0_dp, hpsi, 2*ldap)
      |                                    1
Warning: Type mismatch between actual argument at (1) and actual argument at (2) (COMPLEX(8)/REAL(8)).
[ 94%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/v_of_rho.f90.o
[ 94%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/sum_band.f90.o
[ 94%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/scissor.f90.o
/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1/PW/src/force_hub.f90:2520:20:

 2413 |       CALL MYDGEMM( 'T','N',ldim, nbnd, 2*npw, 2.0_DP, dwfc, 2*npwx, spsi, &
      |                                                       2
......
 2520 |                     wfatdbeta, nwfcU, betapsi(1,nb_s), nh(nt), 1.0_dp, &
      |                    1
Warning: Type mismatch between actual argument at (1) and actual argument at (2) (REAL(8)/COMPLEX(8)).
/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1/PW/src/force_hub.f90:2520:38:

 2413 |       CALL MYDGEMM( 'T','N',ldim, nbnd, 2*npw, 2.0_DP, dwfc, 2*npwx, spsi, &
      |                                                                     2
......
 2520 |                     wfatdbeta, nwfcU, betapsi(1,nb_s), nh(nt), 1.0_dp, &
      |                                      1
Warning: Type mismatch between actual argument at (1) and actual argument at (2) (REAL(8)/COMPLEX(8)).
[ 94%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/c_bands.f90.o
[ 94%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/run_driver.f90.o
[ 97%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/environ_pw_module.f90.o
[ 97%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/potinit.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/setlocal.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/forces.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/newd_gpu.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/newd.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/hinit0.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/addusdens.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/us_exx.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/print_clock_pw.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/s_psi.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/addusforce.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/s_1psi.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/addusstress.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/data_structure.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/hs_1psi.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/s_1psi_gpu.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/s_psi_acc.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/hs_1psi_gpu.f90.o
/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1/PW/src/s_psi_acc.f90:296:55:

  281 |                                   qq_at(1,1,na), nhm, becpr(ofsbeta(na)+1,1),&
      |                                  2                     
......
  296 |           CALL MYDGEMM( 'N', 'N', 2 * n, m, nkb, 1.D0, vkb, &
      |                                                       1
Warning: Type mismatch between actual argument at (1) and actual argument at (2) (COMPLEX(8)/REAL(8)).
/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1/PW/src/s_psi_acc.f90:297:39:

  282 |                                   nkb, 0.0_dp, ps(ofsbeta(na)+1,1), nkb )
      |                                               2
......
  297 |                2 * lda, ps, nkb, 1.D0, spsi, 2*lda )
      |                                       1
Warning: Type mismatch between actual argument at (1) and actual argument at (2) (COMPLEX(8)/REAL(8)).
/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1/PW/src/addusstress.f90:195:31:

  160 |                                qgm, 2*ngm_l, tbecsum, nij, 0.0_dp, aux2, 2*ngm_l )
      |                                             2
......
  195 |                                aux2, 2*ngm_l, 0.0_dp, fac, 3 )
      |                               1
Warning: Type mismatch between actual argument at (1) and actual argument at (2) (COMPLEX(8)/REAL(8)).
/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1/PW/src/addusstress.f90:195:54:

  160 |                                qgm, 2*ngm_l, tbecsum, nij, 0.0_dp, aux2, 2*ngm_l )
      |                                                                   2
......
  195 |                                aux2, 2*ngm_l, 0.0_dp, fac, 3 )
      |                                                      1
Warning: Type mismatch between actual argument at (1) and actual argument at (2) (REAL(8)/COMPLEX(8)).
/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1/PW/src/s_psi.f90:228:53:

  217 |                                   qq_at(1,1,na), nhm, becp%r(ofsbeta(na)+1,1),&
      |                                  2                   
......
  228 |           CALL DGEMM( 'N', 'N', 2 * n, m, nkb, 1.D0, vkb, &
      |                                                     1
Warning: Type mismatch between actual argument at (1) and actual argument at (2) (COMPLEX(8)/REAL(8)).
/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1/PW/src/s_psi.f90:229:39:

  218 |                                   nkb, 0.0_dp, ps(ofsbeta(na)+1,1), nkb )
      |                                               2
......
  229 |                2 * lda, ps, nkb, 1.D0, spsi, 2*lda )
      |                                       1
Warning: Type mismatch between actual argument at (1) and actual argument at (2) (COMPLEX(8)/REAL(8)).
[100%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/move_ions.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/hinit1.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/init_run.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/exx.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/compute_becsum.f90.o
/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1/PW/src/compute_becsum.f90:290:30:

  255 |                       1.0_dp, auxg1, nbnd_loc,    &
      |                              2
......
  290 |                       1.0_dp, auxk1, 2*this_bgrp_nbnd, auxk2, 2*this_bgrp_nbnd, &
      |                              1
Warning: Type mismatch between actual argument at (1) and actual argument at (2) (COMPLEX(8)/REAL(8)).
/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1/PW/src/compute_becsum.f90:290:55:

  256 |                       auxg2, nbnd_loc, 0.0_dp, aux_gk, nhnt )
      |                      2                                 
......
  290 |                       1.0_dp, auxk1, 2*this_bgrp_nbnd, auxk2, 2*this_bgrp_nbnd, &
      |                                                       1
Warning: Type mismatch between actual argument at (1) and actual argument at (2) (COMPLEX(8)/REAL(8)).
[100%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/pw_restart_new.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/clean_pw.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/h_psi.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/h_psi_gpu.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/loc_scdm.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/non_scf.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/run_pwscf.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/setup.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/summary.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/memory_report.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/pw2casino_write.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/stress.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/scale_h.f90.o
/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1/PW/src/stress.f90:108:75:

  108 |                          nspin, dfftp, g, alat, omega, sigmaxc, rho%kin_r )
      |                                                                           1
Warning: More actual than formal arguments in procedure call at (1)
[100%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/input.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/loc_scdm_k.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/electrons.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/punch.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/read_file_new.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw.dir/src/wfcinit.f90.o
[100%] Linking Fortran static library ../lib/libqe_pw.a
[100%] Built target qe_pw
[100%] Building Fortran object PW/CMakeFiles/qe_pw_tools_ev_exe.dir/tools/ev.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw_tools_cell2ibrav_exe.dir/tools/cell2ibrav.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw_tools_scan_ibrav_exe.dir/tools/scan_ibrav.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw_tools_pwi2xsf_exe.dir/tools/pwi2xsf.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw_tools_kpoints_exe.dir/tools/kpoints.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw_exe.dir/src/pwscf.f90.o
[100%] Building Fortran object PW/CMakeFiles/qe_pw_tools_ibrav2cell_exe.dir/tools/ibrav2cell.f90.o
[100%] Linking Fortran executable ../bin/pw.x
[100%] Linking Fortran executable ../bin/cell2ibrav.x
[100%] Linking Fortran executable ../bin/ibrav2cell.x
ld: warning: ignoring duplicate libraries: '../lib/libqe_modules.a'
ld: warning: ignoring duplicate libraries: '../lib/libqe_lax.a', '../lib/libqe_modules.a', '../lib/libqe_upflib.a'
ld: warning: ignoring duplicate libraries: '../lib/libqe_modules.a'
[100%] Linking Fortran executable ../bin/scan_ibrav.x
[100%] Linking Fortran executable ../bin/pwi2xsf.x
[100%] Linking Fortran executable ../bin/kpoints.x
[100%] Built target qe_pw_tools_cell2ibrav_exe
[100%] Built target qe_pw_tools_ibrav2cell_exe
[100%] Built target qe_pw_exe
ld: warning: ignoring duplicate libraries: '../lib/libqe_modules.a'
ld: warning: ignoring duplicate libraries: '../lib/libqe_modules.a'
ld: warning: ignoring duplicate libraries: '../lib/libqe_modules.a'
[100%] Built target qe_pw_tools_pwi2xsf_exe
[100%] Built target qe_pw_tools_scan_ibrav_exe
[100%] Built target qe_pw_tools_kpoints_exe
[100%] Linking Fortran executable ../bin/ev.x
ld: warning: ignoring duplicate libraries: '../lib/libqe_modules.a'
[100%] Built target qe_pw_tools_ev_exe
[100%] basic code for scf, structure optimization, MD
[100%] Built target pw
```
Attempt B (tail):
```
   INTEGER LAX_DESC_SIZE
   PARAMETER (LAX_DESC_SIZE=32)
   INTEGER LAX_DESC_IR
   PARAMETER (LAX_DESC_IR=1)
   INTEGER LAX_DESC_NR
   PARAMETER (LAX_DESC_NR=2)
   INTEGER LAX_DESC_IC
   PARAMETER (LAX_DESC_IC=3)
   INTEGER LAX_DESC_NC
   PARAMETER (LAX_DESC_NC=4)
   INTEGER LAX_DESC_NRCX
   PARAMETER (LAX_DESC_NRCX=5)
   INTEGER LAX_DESC_ACTIVE_NODE
   PARAMETER (LAX_DESC_ACTIVE_NODE=6)
   INTEGER LAX_DESC_N
   PARAMETER (LAX_DESC_N=7)
   INTEGER LAX_DESC_NX
   PARAMETER (LAX_DESC_NX=8)
   INTEGER LAX_DESC_NPR
   PARAMETER (LAX_DESC_NPR=9)
   INTEGER LAX_DESC_NPC
   PARAMETER (LAX_DESC_NPC=10)
   INTEGER LAX_DESC_MYR
   PARAMETER (LAX_DESC_MYR=11)
   INTEGER LAX_DESC_MYC
   PARAMETER (LAX_DESC_MYC=12)
   INTEGER LAX_DESC_COMM
   PARAMETER (LAX_DESC_COMM=13)
   INTEGER LAX_DESC_CNTX
   PARAMETER (LAX_DESC_CNTX=14)
   INTEGER LAX_DESC_MYPE
   PARAMETER (LAX_DESC_MYPE=15)
   INTEGER LAX_DESC_NRL
   PARAMETER (LAX_DESC_NRL=16)
   INTEGER LAX_DESC_NRLX
   PARAMETER (LAX_DESC_NRLX=17)
   !
   INTEGER LAX_STATUS_SIZE
   PARAMETER (LAX_STATUS_SIZE=32)
   INTEGER LAX_STATUS_NPROC        ! nproc_ortho
   PARAMETER (LAX_STATUS_NPROC=1)
   INTEGER LAX_STATUS_LEG          ! leg_ortho
   PARAMETER (LAX_STATUS_LEG=2)
   INTEGER LAX_STATUS_NP1          ! np_ortho(1)
   PARAMETER (LAX_STATUS_NP1=3)
   INTEGER LAX_STATUS_NP2          ! np_ortho(2)
   PARAMETER (LAX_STATUS_NP2=4)
   INTEGER LAX_STATUS_ME1          ! me_ortho(1)
   PARAMETER (LAX_STATUS_ME1=5)
   INTEGER LAX_STATUS_ME2          ! me_ortho(2)
   PARAMETER (LAX_STATUS_ME2=6)
   INTEGER LAX_STATUS_COMM         ! ortho_comm
   PARAMETER (LAX_STATUS_COMM=7)
   INTEGER LAX_STATUS_ROWCOMM      ! ortho_row_comm
   PARAMETER (LAX_STATUS_ROWCOMM=8)
   INTEGER LAX_STATUS_COLCOMM      ! ortho_col_comm
   PARAMETER (LAX_STATUS_COLCOMM=9)
   INTEGER LAX_STATUS_COMMID       ! ortho_comm_id
   PARAMETER (LAX_STATUS_COMMID=10)
   INTEGER LAX_STATUS_PARENTCOMM   ! ortho_parent_comm
   PARAMETER (LAX_STATUS_PARENTCOMM=11)
   INTEGER LAX_STATUS_ORTHOCNTX    ! ortho_cntx
   PARAMETER (LAX_STATUS_ORTHOCNTX=12)
   INTEGER LAX_STATUS_DISTDIAG     ! do_distr_diag_inside_bgrp
   PARAMETER (LAX_STATUS_DISTDIAG=13)

1 warning generated.
cc: error: no input files
cc: error: no input files
make[1]: *** [laxlib_hi.fh] Error 1
make[1]: *** Waiting for unfinished jobs....
make[1]: *** [laxlib_low.fh] Error 1
cc: error: no input files
cc: error: no input files
make[1]: *** [laxlib_kinds.fh] Error 1
make[1]: *** [laxlib.fh] Error 1
cc: error: no input files
make[1]: *** [laxlib_mid.fh] Error 1
cc: error: no input files
make[1]: *** [laxlib_param.fh] Error 1
make: *** [libla] Error 1
make: *** Waiting for unfinished jobs....
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I../UtilXlib -I. -c upf_const.f90 -o upf_const.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I../UtilXlib -I. -c pseudo_types.f90 -o pseudo_types.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I../UtilXlib -I. -c upf_invmat.f90 -o upf_invmat.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I../UtilXlib -I. -c paw_variables.f90 -o paw_variables.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I../UtilXlib -I. -c dylmr2.f90 -o dylmr2.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I../UtilXlib -I. -c splinelib.f90 -o splinelib.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I../UtilXlib -I. -c xmltools.f90 -o xmltools.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I../UtilXlib -I. -c spinor.f90 -o spinor.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I../UtilXlib -I. -c sph_ind.f90 -o sph_ind.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I../UtilXlib -I. -c simpsn.f90 -o simpsn.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I../UtilXlib -I. -c atomic_number.f90 -o atomic_number.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I../UtilXlib -I. -c upf_error.f90 -o upf_error.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I../UtilXlib -I. -c radial_grids.f90 -o radial_grids.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I../UtilXlib -I. -c sph_bes.f90 -o sph_bes.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I../UtilXlib -I. -c ylmr2.f90 -o ylmr2.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I../UtilXlib -I. -c atom.f90 -o atom.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I../UtilXlib -I. -c uspp_param.f90 -o uspp_param.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I../UtilXlib -I. -c gth.f90 -o gth.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I../UtilXlib -I. -c read_cpmd.f90 -o read_cpmd.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I../UtilXlib -I. -c read_fhi.f90 -o read_fhi.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I../UtilXlib -I. -c read_ncpp.f90 -o read_ncpp.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I../UtilXlib -I. -c read_upf_v1.f90 -o read_upf_v1.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I../UtilXlib -I. -c read_uspp.f90 -o read_uspp.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I../UtilXlib -I. -c upf_auxtools.f90 -o upf_auxtools.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I../UtilXlib -I. -c upf_to_internal.f90 -o upf_to_internal.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I../UtilXlib -I. -c casino_pp.f90 -o casino_pp.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I../UtilXlib -I. -c atwfc_mod.f90 -o atwfc_mod.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I../UtilXlib -I. -c qrad_mod.f90 -o qrad_mod.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I../UtilXlib -I. -c rhoat_mod.f90 -o rhoat_mod.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I../UtilXlib -I. -c rhoc_mod.f90 -o rhoc_mod.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I../UtilXlib -I. -c upf_spinorb.f90 -o upf_spinorb.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I../UtilXlib -I. -c init_us_0.f90 -o init_us_0.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I../UtilXlib -I. -c init_us_b0.f90 -o init_us_b0.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I../UtilXlib -I. -c upf_ions.f90 -o upf_ions.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I../UtilXlib -I. -c read_psml.f90 -o read_psml.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I../UtilXlib -I. -c read_upf_new.f90 -o read_upf_new.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I../UtilXlib -I. -c write_upf_new.f90 -o write_upf_new.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I../UtilXlib -I. -c wxml.f90 -o wxml.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I../UtilXlib -I. -c uspp.f90 -o uspp.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I../UtilXlib -I. -c qvan2.f90 -o qvan2.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I../UtilXlib -I. -c dqvan2.f90 -o dqvan2.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I../UtilXlib -I. -c init_us_1.f90 -o init_us_1.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I../UtilXlib -I. -c beta_mod.f90 -o beta_mod.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I../UtilXlib -I. -c vloc_mod.f90 -o vloc_mod.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I../UtilXlib -I. -c gen_us_dj.f90 -o gen_us_dj.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I../UtilXlib -I. -c gen_us_dy.f90 -o gen_us_dy.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I../UtilXlib -I. -c init_us_2_acc.f90 -o init_us_2_acc.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I../UtilXlib -I. -c virtual_v2.f90 -o virtual_v2.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I../UtilXlib -I. -c upfconv.f90 -o upfconv.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I../UtilXlib -I. -c casino2upf.f90 -o casino2upf.o
gfortran -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include   -c mbd_methods.F90
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I../UtilXlib -I. -c read_ps.f90 -o read_ps.o
ar ruv libupf.a atwfc_mod.o beta_mod.o qrad_mod.o rhoat_mod.o rhoc_mod.o vloc_mod.o qvan2.o dqvan2.o gen_us_dj.o gen_us_dy.o init_us_0.o init_us_b0.o init_us_1.o init_us_2_acc.o atom.o atomic_number.o dylmr2.o gth.o paw_variables.o pseudo_types.o radial_grids.o read_cpmd.o read_fhi.o read_ncpp.o read_ps.o read_psml.o read_upf_new.o read_upf_v1.o read_uspp.o spinor.o sph_ind.o sph_bes.o splinelib.o simpsn.o upf_auxtools.o upf_const.o upf_error.o upf_invmat.o upf_io.o upf_ions.o upf_kinds.o upf_params.o upf_parallel_include.o upf_spinorb.o upf_to_internal.o upf_utils.o uspp.o uspp_param.o write_upf_new.o xmltools.o ylmr2.o ylmr2_gpu.o dom.o wxml.o       
mpif90 -g -o upfconv.x upfconv.o casino_pp.o atom.o atomic_number.o dylmr2.o gth.o paw_variables.o pseudo_types.o radial_grids.o read_cpmd.o read_fhi.o read_ncpp.o read_ps.o read_psml.o read_upf_new.o read_upf_v1.o read_uspp.o spinor.o sph_ind.o sph_bes.o splinelib.o simpsn.o upf_auxtools.o upf_const.o upf_error.o upf_invmat.o upf_io.o upf_ions.o upf_kinds.o upf_params.o upf_parallel_include.o upf_spinorb.o upf_to_internal.o upf_utils.o uspp.o uspp_param.o write_upf_new.o xmltools.o ylmr2.o ylmr2_gpu.o dom.o wxml.o -L/opt/homebrew/opt/veclibfort/lib -lvecLibFort -framework Accelerate -L/opt/homebrew/opt/veclibfort/lib -lvecLibFort -framework Accelerate
mpif90 -g -o casino2upf.x casino2upf.o casino_pp.o atom.o atomic_number.o dylmr2.o gth.o paw_variables.o pseudo_types.o radial_grids.o read_cpmd.o read_fhi.o read_ncpp.o read_ps.o read_psml.o read_upf_new.o read_upf_v1.o read_uspp.o spinor.o sph_ind.o sph_bes.o splinelib.o simpsn.o upf_auxtools.o upf_const.o upf_error.o upf_invmat.o upf_io.o upf_ions.o upf_kinds.o upf_params.o upf_parallel_include.o upf_spinorb.o upf_to_internal.o upf_utils.o uspp.o uspp_param.o write_upf_new.o xmltools.o ylmr2.o ylmr2_gpu.o dom.o wxml.o -L/opt/homebrew/opt/veclibfort/lib -lvecLibFort -framework Accelerate -L/opt/homebrew/opt/veclibfort/lib -lvecLibFort -framework Accelerate
ar: creating archive libupf.a
a - atwfc_mod.o
a - beta_mod.o
a - qrad_mod.o
a - rhoat_mod.o
a - rhoc_mod.o
a - vloc_mod.o
a - qvan2.o
a - dqvan2.o
a - gen_us_dj.o
a - gen_us_dy.o
a - init_us_0.o
a - init_us_b0.o
a - init_us_1.o
a - init_us_2_acc.o
a - atom.o
a - atomic_number.o
a - dylmr2.o
a - gth.o
a - paw_variables.o
a - pseudo_types.o
a - radial_grids.o
a - read_cpmd.o
a - read_fhi.o
a - read_ncpp.o
a - read_ps.o
a - read_psml.o
a - read_upf_new.o
a - read_upf_v1.o
a - read_uspp.o
a - spinor.o
a - sph_ind.o
a - sph_bes.o
a - splinelib.o
a - simpsn.o
a - upf_auxtools.o
a - upf_const.o
a - upf_error.o
a - upf_invmat.o
a - upf_io.o
a - upf_ions.o
a - upf_kinds.o
a - upf_params.o
a - upf_parallel_include.o
a - upf_spinorb.o
a - upf_to_internal.o
a - upf_utils.o
a - uspp.o
a - uspp_param.o
a - write_upf_new.o
a - xmltools.o
a - ylmr2.o
a - ylmr2_gpu.o
a - dom.o
a - wxml.o
ranlib -c libupf.a    
ld: warning: ignoring duplicate libraries: '-lvecLibFort'
ld: warning: ignoring duplicate libraries: '-lvecLibFort'
gfortran -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include   -c mbd.F90
mpif90 -g -o virtual_v2.x virtual_v2.o atom.o atomic_number.o dylmr2.o gth.o paw_variables.o pseudo_types.o radial_grids.o read_cpmd.o read_fhi.o read_ncpp.o read_ps.o read_psml.o read_upf_new.o read_upf_v1.o read_uspp.o spinor.o sph_ind.o sph_bes.o splinelib.o simpsn.o upf_auxtools.o upf_const.o upf_error.o upf_invmat.o upf_io.o upf_ions.o upf_kinds.o upf_params.o upf_parallel_include.o upf_spinorb.o upf_to_internal.o upf_utils.o uspp.o uspp_param.o write_upf_new.o xmltools.o ylmr2.o ylmr2_gpu.o dom.o wxml.o -L/opt/homebrew/opt/veclibfort/lib -lvecLibFort -framework Accelerate -L/opt/homebrew/opt/veclibfort/lib -lvecLibFort -framework Accelerate
ld: warning: ignoring duplicate libraries: '-lvecLibFort'
ar -r libmbd.a mbd.o mbd_constants.o mbd_coulomb.o mbd_damping.o mbd_defaults.o mbd_density.o mbd_dipole.o mbd_formulas.o mbd_geom.o mbd_gradients.o mbd_hamiltonian.o mbd_lapack.o mbd_linalg.o mbd_matrix.o mbd_methods.o mbd_rpa.o mbd_scs.o mbd_ts.o mbd_utils.o mbd_version.o mbd_vdw_param.o
ar: creating archive libmbd.a
```

## Version captures
```
=== BREW VERSIONS ===
cmake 4.1.2
gcc 15.2.0
open-mpi 5.0.8
openblas 0.3.30
veclibfort 0.4.3
=== BREW CONFIG ===
HOMEBREW_VERSION: 4.6.18
ORIGIN: https://github.com/Homebrew/brew
HEAD: 00001bedf8eac442bdabd327148be0b97998b27b
Last commit: 6 days ago
Branch: stable
Core tap JSON: 25 Oct 17:10 UTC
Core cask tap JSON: 25 Oct 17:10 UTC
HOMEBREW_PREFIX: /opt/homebrew
HOMEBREW_CASK_OPTS: []
HOMEBREW_FORBID_PACKAGES_FROM_PATHS: set
HOMEBREW_MAKE_JOBS: 10
Homebrew Ruby: 3.4.5 => /opt/homebrew/Library/Homebrew/vendor/portable-ruby/3.4.5/bin/ruby
CPU: deca-core 64-bit arm_donan
Clang: 17.0.0 build 1700
Git: 2.50.1 => /opt/homebrew/bin/git
Curl: 8.7.1 => /usr/bin/curl
macOS: 15.3-arm64
CLT: 16.4.0.0.1.1747106510
Xcode: N/A
Rosetta 2: false
=== TOOL VERSIONS ===
GNU Fortran (Homebrew GCC 15.2.0) 15.2.0
Copyright (C) 2025 Free Software Foundation, Inc.
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

mpirun (Open MPI) 5.0.8

Report bugs to https://www.open-mpi.org/community/help/

cmake version 4.1.2

CMake suite maintained and supported by Kitware (kitware.com/cmake).
```

## Assessment
Build succeeded on Apple Silicon. Use this machine for light tests; keep heavy runs on the server.
## Attempt B2 (configure+Accelerate) result
ranlib -c libpw.a
if test -d PW ; then \
	( cd PW ; /Library/Developer/CommandLineTools/usr/bin/make TLDEPS= all || exit 1) ; fi
( cd src ; /Library/Developer/CommandLineTools/usr/bin/make all || exit 1 )
if test -n "" ; then \
	( cd ../.. ; /Library/Developer/CommandLineTools/usr/bin/make  || exit 1 ) ; fi
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//upflib -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//XClib -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//Modules -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//FFTXlib/src -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//LAXlib -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//UtilXlib -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//MBD -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//KS_Solvers  -I../../dft-d3/ -c pwscf.f90 -o pwscf.o
mpif90 -g -o pw.x \
	   pwscf.o  libpw.a ../../KS_Solvers/libks_solvers.a ../../dft-d3/libdftd3qe.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//Modules/libqemod.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//upflib/libupf.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//XClib/xc_lib.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//FFTXlib/src/libqefft.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//LAXlib/libqela.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//UtilXlib/libutil.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//MBD/libmbd.a  -L/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -ldevXlib  -L/opt/homebrew/opt/veclibfort/lib -lvecLibFort -framework Accelerate   -L/opt/homebrew/opt/veclibfort/lib -lvecLibFort -framework Accelerate     
ld: warning: ignoring duplicate libraries: '-lvecLibFort'
( cd ../../bin; ln -fs ../PW/src/pw.x . ; \
               ln -fs ../PW/src/pw.x dist.x ; ln -fs ../PW/src/pw.x manypw.x ; )
( cd tools ; /Library/Developer/CommandLineTools/usr/bin/make all || exit 1 )
if test -n "" ; then \
	( cd ../.. ; /Library/Developer/CommandLineTools/usr/bin/make  || exit 1 ) ; fi
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//upflib -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//XClib -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//Modules -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//FFTXlib/src -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//LAXlib -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//UtilXlib -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//MBD -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//KS_Solvers  -I../src -I../../dft-d3/ -c ev.f90 -o ev.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//upflib -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//XClib -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//Modules -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//FFTXlib/src -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//LAXlib -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//UtilXlib -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//MBD -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//KS_Solvers  -I../src -I../../dft-d3/ -c kpoints.f90 -o kpoints.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//upflib -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//XClib -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//Modules -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//FFTXlib/src -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//LAXlib -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//UtilXlib -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//MBD -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//KS_Solvers  -I../src -I../../dft-d3/ -c pwi2xsf.f90 -o pwi2xsf.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//upflib -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//XClib -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//Modules -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//FFTXlib/src -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//LAXlib -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//UtilXlib -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//MBD -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//KS_Solvers  -I../src -I../../dft-d3/ -c ibrav2cell.f90 -o ibrav2cell.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//upflib -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//XClib -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//Modules -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//FFTXlib/src -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//LAXlib -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//UtilXlib -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//MBD -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//KS_Solvers  -I../src -I../../dft-d3/ -c cell2ibrav.f90 -o cell2ibrav.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//upflib -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//XClib -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//Modules -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//FFTXlib/src -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//LAXlib -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//UtilXlib -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//MBD -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//KS_Solvers  -I../src -I../../dft-d3/ -c scan_ibrav.f90 -o scan_ibrav.o
mpif90 -O3 -g -fallow-argument-mismatch -cpp -D__FFTW -D__MPI -D__MPI_MODULE  -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -I. -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//include -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//upflib -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//XClib -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//Modules -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//FFTXlib/src -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//LAXlib -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//UtilXlib -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//MBD -I/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//KS_Solvers  -I../src -I../../dft-d3/ -c rism1d.f90 -o rism1d.o
mpif90 -g -o rism1d.x \
		rism1d.o ../src/libpw.a ../../KS_Solvers/libks_solvers.a ../../dft-d3/libdftd3qe.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//Modules/libqemod.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//upflib/libupf.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//XClib/xc_lib.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//FFTXlib/src/libqefft.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//LAXlib/libqela.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//UtilXlib/libutil.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//MBD/libmbd.a   -L/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -ldevXlib  -L/opt/homebrew/opt/veclibfort/lib -lvecLibFort -framework Accelerate   -L/opt/homebrew/opt/veclibfort/lib -lvecLibFort -framework Accelerate     
ld: warning: ignoring duplicate libraries: '-lvecLibFort'
mpif90 -g -o cell2ibrav.x \
		cell2ibrav.o ../src/libpw.a ../../KS_Solvers/libks_solvers.a ../../dft-d3/libdftd3qe.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//Modules/libqemod.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//upflib/libupf.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//XClib/xc_lib.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//FFTXlib/src/libqefft.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//LAXlib/libqela.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//UtilXlib/libutil.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//MBD/libmbd.a  -L/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -ldevXlib  -L/opt/homebrew/opt/veclibfort/lib -lvecLibFort -framework Accelerate   -L/opt/homebrew/opt/veclibfort/lib -lvecLibFort -framework Accelerate     
mpif90 -g -o ibrav2cell.x \
		ibrav2cell.o ../src/libpw.a ../../KS_Solvers/libks_solvers.a ../../dft-d3/libdftd3qe.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//Modules/libqemod.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//upflib/libupf.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//XClib/xc_lib.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//FFTXlib/src/libqefft.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//LAXlib/libqela.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//UtilXlib/libutil.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//MBD/libmbd.a  -L/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -ldevXlib  -L/opt/homebrew/opt/veclibfort/lib -lvecLibFort -framework Accelerate   -L/opt/homebrew/opt/veclibfort/lib -lvecLibFort -framework Accelerate     
ld: warning: ignoring duplicate libraries: '-lvecLibFort'
( cd ../../bin ; ln -fs ../PW/tools/rism1d.x . )
ld: warning: ignoring duplicate libraries: '-lvecLibFort'
( cd ../../bin ; ln -fs ../PW/tools/cell2ibrav.x . )
( cd ../../bin ; ln -fs ../PW/tools/ibrav2cell.x . )
mpif90 -g -o scan_ibrav.x \
		scan_ibrav.o ../src/libpw.a ../../KS_Solvers/libks_solvers.a ../../dft-d3/libdftd3qe.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//Modules/libqemod.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//upflib/libupf.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//XClib/xc_lib.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//FFTXlib/src/libqefft.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//LAXlib/libqela.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//UtilXlib/libutil.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//MBD/libmbd.a  -L/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -ldevXlib  -L/opt/homebrew/opt/veclibfort/lib -lvecLibFort -framework Accelerate   -L/opt/homebrew/opt/veclibfort/lib -lvecLibFort -framework Accelerate     
mpif90 -g -o pwi2xsf.x \
		pwi2xsf.o ../src/libpw.a ../../KS_Solvers/libks_solvers.a ../../dft-d3/libdftd3qe.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//Modules/libqemod.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//upflib/libupf.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//XClib/xc_lib.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//FFTXlib/src/libqefft.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//LAXlib/libqela.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//UtilXlib/libutil.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//MBD/libmbd.a  -L/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -ldevXlib  -L/opt/homebrew/opt/veclibfort/lib -lvecLibFort -framework Accelerate   -L/opt/homebrew/opt/veclibfort/lib -lvecLibFort -framework Accelerate     
mpif90 -g -o kpoints.x \
		kpoints.o ../src/libpw.a ../../KS_Solvers/libks_solvers.a ../../dft-d3/libdftd3qe.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//Modules/libqemod.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//upflib/libupf.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//XClib/xc_lib.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//FFTXlib/src/libqefft.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//LAXlib/libqela.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//UtilXlib/libutil.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//MBD/libmbd.a  -L/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -ldevXlib  -L/opt/homebrew/opt/veclibfort/lib -lvecLibFort -framework Accelerate   -L/opt/homebrew/opt/veclibfort/lib -lvecLibFort -framework Accelerate     
ld: warning: ignoring duplicate libraries: '-lvecLibFort'
ld: warning: ignoring duplicate libraries: '-lvecLibFort'
ld: warning: ignoring duplicate libraries: '-lvecLibFort'
( cd ../../bin ; ln -fs ../PW/tools/scan_ibrav.x . )
( cd ../../bin ; ln -fs ../PW/tools/kpoints.x . )
( cd ../../bin ; ln -fs ../PW/tools/pwi2xsf.x . )
mpif90 -g -o ev.x \
		ev.o ../src/libpw.a ../../KS_Solvers/libks_solvers.a ../../dft-d3/libdftd3qe.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//Modules/libqemod.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//upflib/libupf.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//XClib/xc_lib.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//FFTXlib/src/libqefft.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//LAXlib/libqela.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//UtilXlib/libutil.a /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//MBD/libmbd.a  -L/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1//external/devxlib/src -ldevXlib  -L/opt/homebrew/opt/veclibfort/lib -lvecLibFort -framework Accelerate   -L/opt/homebrew/opt/veclibfort/lib -lvecLibFort -framework Accelerate     
ld: warning: ignoring duplicate libraries: '-lvecLibFort'
( cd ../../bin ; ln -fs ../PW/tools/ev.x . )

## Linkage
### otool -L artifacts/q-e-qe-7.4.1/bin/pw.x
artifacts/q-e-qe-7.4.1/bin/pw.x:
	/opt/homebrew/opt/veclibfort/lib/libvecLibFort.dylib (compatibility version 0.0.0, current version 0.0.0)
	/opt/homebrew/opt/open-mpi/lib/libmpi_usempif08.40.dylib (compatibility version 81.0.0, current version 81.3.0)
	/opt/homebrew/opt/open-mpi/lib/libmpi_usempi_ignore_tkr.40.dylib (compatibility version 81.0.0, current version 81.1.0)
	/opt/homebrew/opt/open-mpi/lib/libmpi_mpifh.40.dylib (compatibility version 81.0.0, current version 81.1.0)
	/opt/homebrew/opt/open-mpi/lib/libmpi.40.dylib (compatibility version 81.0.0, current version 81.7.0)
	/opt/homebrew/opt/gcc/lib/gcc/current/libgfortran.5.dylib (compatibility version 6.0.0, current version 6.0.0)
	/System/Library/Frameworks/Accelerate.framework/Versions/A/Accelerate (compatibility version 1.0.0, current version 4.0.0)
	/opt/homebrew/opt/gcc/lib/gcc/current/libquadmath.0.dylib (compatibility version 1.0.0, current version 1.0.0)
	/usr/lib/libSystem.B.dylib (compatibility version 1.0.0, current version 1351.0.0)

## Si SCF quick run
PP missing: place Si.pbe-n-rrkjus_psl.1.0.0.UPF under ./pp and re-run. See docs/PP.md
## Pseudopotential fetch
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
  0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0  0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0  2 1477k    2 39958    0     0  23718      0  0:01:03  0:00:01  0:01:02 23713 38 1477k   38  562k    0     0   212k      0  0:00:06  0:00:02  0:00:04  212k100 1477k  100 1477k    0     0   466k      0  0:00:03  0:00:03 --:--:--  466k

## Attempt B2 — Si SCF run
    -1.6023  -1.6023   3.3622   3.3622   6.9278   6.9278  16.3274  16.3274

          k = 0.6667-0.3333 1.0000 (   748 PWs)   bands (ev):

    -3.4584   0.5720   2.6444   3.9204   9.0732   9.9362  10.4559  13.2895

          k = 0.5000-0.1667 0.8333 (   738 PWs)   bands (ev):

    -2.4726  -0.6288   2.2041   3.4530   9.5765   9.7785  12.3248  12.7416

          k =-0.3333-1.0000 0.0000 (   742 PWs)   bands (ev):

    -1.4822  -1.4822   2.5688   2.5688   8.9691   8.9691  12.9869  12.9869

     the Fermi energy is     6.4576 ev

     WARNING: integrated charge=     7.99854241, expected=     8.00000000

!    total energy              =     -22.83849068 Ry
     estimated scf accuracy    <          7.0E-09 Ry
     smearing contrib. (-TS)   =       0.00010308 Ry
     internal energy E=F+TS    =     -22.83859376 Ry

     The total energy is F=E-TS. E is the sum of the following terms:
     one-electron contribution =       5.16878573 Ry
     hartree contribution      =       1.10442106 Ry
     xc contribution           =     -12.31087095 Ry
     ewald contribution        =     -16.80092961 Ry

     convergence has been achieved in   5 iterations

     Writing all to output data dir ./tmp/silicon.save/ :
     XML data file, charge density, pseudopotentials, collected wavefunctions

     init_run     :      0.06s CPU      0.08s WALL (       1 calls)
     electrons    :      0.34s CPU      0.36s WALL (       1 calls)

     Called by init_run:
     wfcinit      :      0.02s CPU      0.02s WALL (       1 calls)
     potinit      :      0.00s CPU      0.01s WALL (       1 calls)
     hinit0       :      0.04s CPU      0.04s WALL (       1 calls)

     Called by electrons:
     c_bands      :      0.25s CPU      0.27s WALL (       6 calls)
     sum_band     :      0.06s CPU      0.07s WALL (       6 calls)
     v_of_rho     :      0.01s CPU      0.01s WALL (       6 calls)
     newd         :      0.02s CPU      0.02s WALL (       6 calls)
     mix_rho      :      0.00s CPU      0.00s WALL (       6 calls)

     Called by c_bands:
     init_us_2    :      0.01s CPU      0.01s WALL (     208 calls)
     cegterg      :      0.24s CPU      0.25s WALL (      96 calls)

     Called by *egterg:
     cdiaghg      :      0.01s CPU      0.01s WALL (     366 calls)
     h_psi        :      0.20s CPU      0.21s WALL (     398 calls)
     s_psi        :      0.01s CPU      0.01s WALL (     398 calls)
     g_psi        :      0.00s CPU      0.00s WALL (     286 calls)

     Called by h_psi:
     h_psi:calbec :      0.01s CPU      0.01s WALL (     398 calls)
     vloc_psi     :      0.18s CPU      0.19s WALL (     398 calls)
     add_vuspsi   :      0.01s CPU      0.01s WALL (     398 calls)

     General routines
     calbec       :      0.01s CPU      0.02s WALL (     494 calls)
     fft          :      0.00s CPU      0.00s WALL (      67 calls)
     ffts         :      0.00s CPU      0.00s WALL (       6 calls)
     fftw         :      0.19s CPU      0.19s WALL (    5138 calls)

     Parallel routines

     PWSCF        :      0.45s CPU      0.52s WALL


   This run was terminated on:  15:21:36  30Oct2025            

=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=

## Attempt A2 — CMake rebuild
-- Performing Test Fortran_ISYSTEM_SUPPORTED - Success
-- Found OpenMP_Fortran: -fopenmp (found version "4.5")
-- Found OpenMP: TRUE (found version "4.5") found components: Fortran
-- Found MPI_Fortran: /opt/homebrew/bin/mpif90 (found version "3.1")
-- Found MPI: TRUE (found version "3.1") found components: Fortran
-- Selected the Fortran 'mpi' module. QE_ENABLE_MPI_MODULE=ON
-- MPI settings used by CTest
     MPIEXEC_EXECUTABLE : /opt/homebrew/bin/mpiexec
     MPIEXEC_NUMPROC_FLAG : -n
     MPIEXEC_PREFLAGS : 
   Tests run as : /opt/homebrew/bin/mpiexec -n <NUM_PROCS>  <EXECUTABLE>
-- Found Git: /opt/homebrew/bin/git (found suitable version "2.50.1", minimum required is "2.13")
-- Source files are not cloned from a git repository.
-- Trying to find LAPACK from ARM Performance Library
-- Found BLAS: /opt/homebrew/opt/openblas/lib/libopenblas.dylib
-- Found LAPACK: /opt/homebrew/opt/openblas/lib/libopenblas.dylib
-- Looking for Fortran zhpev
-- Looking for Fortran zhpev - found
-- Installing Wannier90 via submodule
-- Previous clone found at /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1/external/wannier90.
-- Installing MBD via submodule
-- Previous clone found at /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1/external/mbd.
-- Found Git: /opt/homebrew/bin/git (found version "2.50.1")
-- Setting version tag to  from Git
-- Installing DeviceXlib via submodule
-- Previous clone found at /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1/external/devxlib.
-- Could NOT find VendorFFTW (missing: VendorFFTW_LIBRARIES VendorFFTW_INCLUDE_DIRS VendorFFTW_ID) 
-- Found PkgConfig: /opt/homebrew/bin/pkg-config (found version "2.5.1")
-- Found FFTW3: /opt/homebrew/lib/libfftw3.dylib;/opt/homebrew/lib/libfftw3_omp.dylib
-- Looking for mallinfo
-- Looking for mallinfo - not found
-- Enabling tests in test-suite

Only pw and cp results from ctest are reliable, we are working on making the rest tests work reliably with ctest. To run non-pw/cp tests, make a softlink of the bin directory to the root of QE source tree and run tests in the test-suite directory under that root.

-- generating tests in pw category
-- generating tests in cp category
-- Configuring done (3.3s)
-- Generating done (0.7s)
-- Build files have been written to: /Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1/buildA

  645 |         CALL bcast_real( msg, 2 * msglen, source, gid )
      |                         1
......
  722 |         CALL bcast_real( msg, 2 * msglen, source, gid )
      |                         2
Warning: Rank mismatch between actual argument at (1) and actual argument at (2) (rank-1 and scalar)
/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1/UtilXlib/mp.f90:631:25:

  631 |         CALL bcast_real( msg, msglen, source, gid )
      |                         1
......
  722 |         CALL bcast_real( msg, 2 * msglen, source, gid )
      |                         2
Warning: Type mismatch between actual argument at (1) and actual argument at (2) (REAL(8)/COMPLEX(8)).
/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1/UtilXlib/mp.f90:454:28:

  454 |         CALL bcast_integer( msg, msglen, source, group )
      |                            1
......
  828 |         CALL bcast_integer( imsg, msglen, source, group )
      |                            2
Warning: Rank mismatch between actual argument at (1) and actual argument at (2) (rank-1 and scalar)
[ 14%] Building Fortran object external/mbd/src/CMakeFiles/mbd.dir/mbd_hamiltonian.F90.o
[ 14%] Building Fortran object external/mbd/src/CMakeFiles/mbd.dir/mbd_rpa.F90.o
[ 14%] Building Fortran object external/mbd/src/CMakeFiles/mbd.dir/mbd_scs.f90.o
[ 14%] Building Fortran object external/mbd/src/CMakeFiles/mbd.dir/mbd_coulomb.f90.o
[ 14%] Building Fortran object UtilXlib/CMakeFiles/qe_utilx.dir/error_handler.f90.o
[ 14%] Building Fortran object UtilXlib/CMakeFiles/qe_utilx.dir/mp_bands_util.f90.o
[ 14%] Building Fortran object UtilXlib/CMakeFiles/qe_utilx.dir/divide.f90.o
[ 14%] Building Fortran object UtilXlib/CMakeFiles/qe_utilx.dir/set_mpi_comm_4_solvers.f90.o
[ 14%] Building Fortran object UtilXlib/CMakeFiles/qe_utilx.dir/export_gstart_2_solvers.f90.o
[ 14%] Linking Fortran static library ../lib/libqe_utilx.a
[ 14%] Built target qe_utilx
[ 14%] Building Fortran object external/mbd/src/CMakeFiles/mbd.dir/mbd_methods.F90.o
[ 14%] Building Fortran object external/mbd/src/CMakeFiles/mbd.dir/mbd.F90.o
[ 14%] Linking Fortran static library ../../../lib/libmbd.a
[ 14%] Built target mbd
make[1]: *** [PW/CMakeFiles/pw.dir/rule] Error 2
make: *** [pw] Error 2
/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1/upflib/wxml.f90:367:15:

  367 |     real(DP_XML), intent(in) :: field(:,:)
      |               1
Error: Symbol 'dp_xml' at (1) has no IMPLICIT type
/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1/upflib/wxml.f90:127:45:

  127 |   subroutine xml_addattribute_r ( xf, name, value )
      |                                             1~~~~
Error: Symbol 'value' at (1) has no IMPLICIT type
/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1/upflib/wxml.f90:141:45:

  141 |   subroutine xml_addattribute_rv( xf, name, value )
      |                                             1~~~~
Error: Symbol 'value' at (1) has no IMPLICIT type; did you mean 'cvalue'?
/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1/upflib/wxml.f90:309:40:

  309 |   subroutine xml_addcharacters_r ( xf, field, fmt )
      |                                        1~~~~
Error: Symbol 'field' at (1) has no IMPLICIT type; did you mean 'cfield'?
/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1/upflib/wxml.f90:364:40:

  364 |   subroutine xml_addcharacters_rm( xf, field, fmt )
      |                                        1~~~~
Error: Symbol 'field' at (1) has no IMPLICIT type
/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1/upflib/wxml.f90:334:40:

  334 |   subroutine xml_addcharacters_rv( xf, field, fmt )
      |                                        1~~~~
Error: Symbol 'field' at (1) has no IMPLICIT type; did you mean 'cfield'?
/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1/upflib/wxml.f90:127:3:

  127 |   subroutine xml_addattribute_r ( xf, name, value )
      |   1~~~~~~~~~~~~~~~~~~~~~~~~~~~~
......
  141 |   subroutine xml_addattribute_rv( xf, name, value )
      |   2~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Error: Ambiguous interfaces in generic interface 'xml_addattribute' for 'xml_addattribute_r' at (1) and 'xml_addattribute_rv' at (2)
/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1/upflib/wxml.f90:334:3:

  334 |   subroutine xml_addcharacters_rv( xf, field, fmt )
      |   1~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
......
  364 |   subroutine xml_addcharacters_rm( xf, field, fmt )
      |   2~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Error: Ambiguous interfaces in generic interface 'xml_addcharacters' for 'xml_addcharacters_rv' at (1) and 'xml_addcharacters_rm' at (2)
/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1/upflib/wxml.f90:334:40:

  334 |   subroutine xml_addcharacters_rv( xf, field, fmt )
      |                                        1~~~~
Error: Symbol 'field' at (1) has no IMPLICIT type; did you mean 'cfield'?
/Users/pollob/qe_macm4_build/artifacts/q-e-qe-7.4.1/upflib/wxml.f90:127:45:

  127 |   subroutine xml_addattribute_r ( xf, name, value )
      |                                             1~~~~
Error: Symbol 'value' at (1) has no IMPLICIT type
make[3]: *** [upflib/CMakeFiles/qe_xml.dir/wxml.f90.o] Error 1
make[2]: *** [upflib/CMakeFiles/qe_xml.dir/all] Error 2
make[1]: *** [PW/CMakeFiles/pw.dir/rule] Error 2
make: *** [pw] Error 2
## Si band workflow
```
     wfcinit      :      0.00s CPU      0.00s WALL (       1 calls)
     potinit      :      0.00s CPU      0.00s WALL (       1 calls)
     hinit0       :      0.04s CPU      0.04s WALL (       1 calls)

     Called by electrons:
     c_bands      :      5.07s CPU      5.39s WALL (       1 calls)
     v_of_rho     :      0.00s CPU      0.00s WALL (       1 calls)
     newd         :      0.00s CPU      0.01s WALL (       1 calls)

     Called by c_bands:
     init_us_2    :      0.01s CPU      0.01s WALL (     201 calls)
     cegterg      :      4.85s CPU      5.15s WALL (     456 calls)

     Called by *egterg:
     cdiaghg      :      0.25s CPU      0.26s WALL (    7133 calls)
     h_psi        :      3.91s CPU      4.10s WALL (    7589 calls)
     s_psi        :      0.16s CPU      0.17s WALL (    7589 calls)
     g_psi        :      0.02s CPU      0.02s WALL (    6932 calls)

     Called by h_psi:
     h_psi:calbec :      0.21s CPU      0.27s WALL (    7589 calls)
     vloc_psi     :      3.51s CPU      3.62s WALL (    7589 calls)
     add_vuspsi   :      0.18s CPU      0.19s WALL (    7589 calls)

     General routines
     calbec       :      0.21s CPU      0.26s WALL (    7589 calls)
     fft          :      0.00s CPU      0.00s WALL (      12 calls)
     fftw         :      3.09s CPU      3.18s WALL (   82018 calls)
     davcio       :      0.00s CPU      0.01s WALL (     402 calls)

     Parallel routines

     PWSCF        :      5.18s CPU      5.56s WALL


   This run was terminated on:  15: 7:56  31Oct2025            

=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=
...
     e(  2 -  2) =     -0.70585  eV     1   --> A_1  L_1       
     e(  3 -  4) =      5.02288  eV     2   --> E    L_3       
     e(  5 -  5) =      7.76355  eV     1   --> A_1  L_1       
     e(  6 -  7) =      9.56300  eV     2   --> E    L_3       
     e(  8 -  8) =     13.96210  eV     1   --> A_1  L_1       

 **************************************************************************

 **************************************************************************

                    xk=(  -0.48750,   0.48750,   0.48750  )

     Band symmetry, C_3v (3m)   point group:

     e(  1 -  1) =     -3.42478  eV     1   --> A_1  L_1       
     e(  2 -  2) =     -0.74394  eV     1   --> A_1  L_1       
     e(  3 -  4) =      5.01951  eV     2   --> E    L_3       
     e(  5 -  5) =      7.75968  eV     1   --> A_1  L_1       
     e(  6 -  7) =      9.55909  eV     2   --> E    L_3       
     e(  8 -  8) =     13.95610  eV     1   --> A_1  L_1       

 **************************************************************************

 **************************************************************************

                    xk=(  -0.50000,   0.50000,   0.50000  )

     zone border point and non-symmorphic group 
     symmetry decomposition not available

 **************************************************************************

     BANDS        :      1.82s CPU      2.03s WALL


   This run was terminated on:  15: 8:50  31Oct2025            

=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=
```

Generated plot: analysis/Si/plots/si_band_structure.png
## Si DOS workflow
```
     wfcinit      :      0.00s CPU      0.00s WALL (       1 calls)
     potinit      :      0.00s CPU      0.00s WALL (       1 calls)
     hinit0       :      0.04s CPU      0.04s WALL (       1 calls)

     Called by electrons:
     c_bands      :      4.68s CPU      4.89s WALL (       1 calls)
     v_of_rho     :      0.00s CPU      0.00s WALL (       1 calls)
     newd         :      0.00s CPU      0.01s WALL (       1 calls)

     Called by c_bands:
     init_us_2    :      0.00s CPU      0.00s WALL (      72 calls)
     cegterg      :      4.53s CPU      4.71s WALL (     218 calls)

     Called by *egterg:
     cdiaghg      :      0.50s CPU      0.51s WALL (    3727 calls)
     h_psi        :      3.38s CPU      3.49s WALL (    3945 calls)
     s_psi        :      0.10s CPU      0.11s WALL (    3945 calls)
     g_psi        :      0.02s CPU      0.02s WALL (    3655 calls)

     Called by h_psi:
     h_psi:calbec :      0.12s CPU      0.14s WALL (    3945 calls)
     vloc_psi     :      3.14s CPU      3.22s WALL (    3945 calls)
     add_vuspsi   :      0.11s CPU      0.12s WALL (    3945 calls)

     General routines
     calbec       :      0.12s CPU      0.14s WALL (    3945 calls)
     fft          :      0.00s CPU      0.00s WALL (      12 calls)
     fftw         :      2.77s CPU      2.83s WALL (   72766 calls)
     davcio       :      0.00s CPU      0.00s WALL (     144 calls)

     Parallel routines

     PWSCF        :      4.82s CPU      5.10s WALL


   This run was terminated on:  19: 5:35  31Oct2025            

=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=
...
     http://www.quantum-espresso.org/quote

     Parallel version (MPI), running on     1 processors

     MPI processes distributed on     1 nodes
     0 MiB available memory on the printing compute node when the environment starts


     Reading xml data from directory:

     ./tmp/silicon.save/

     IMPORTANT: XC functional enforced from input :
     Exchange-correlation= PBE
                           (   1   4   3   4   0   0   0)
     Any further DFT definition will be discarded
     Please, verify this is what you really want


     G-vector sticks info
     --------------------
     sticks:   dense  smooth     PW     G-vecs:    dense   smooth      PW
     Sum         433     433    151                 5961     5961    1139

     Using Slab Decomposition


     Check: negative core charge=   -0.000004

     Gaussian broadening (default values): ngauss,degauss=   0    0.001470


     DOS          :      0.14s CPU      0.14s WALL


   This run was terminated on:  19: 6: 9  31Oct2025            

=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=
```
Plots: analysis/Si/plots/si_total_dos.png
## Si PDOS workflow
```
    |psi|^2 = 0.364
==== e(  11) =    19.26634 eV ==== 
     psi = 0.032*[#   1]+0.032*[#   5]+0.012*[#   2]+0.012*[#   3]+0.012*[#   4]
          +0.012*[#   6]+0.012*[#   7]+0.012*[#   8]
    |psi|^2 = 0.134
==== e(  12) =    19.26634 eV ==== 
     psi = 0.032*[#   1]+0.032*[#   5]+0.012*[#   2]+0.012*[#   3]+0.012*[#   4]
          +0.012*[#   6]+0.012*[#   7]+0.012*[#   8]
    |psi|^2 = 0.134
==== e(  13) =    22.67247 eV ==== 
     psi = 0.002*[#   2]+0.002*[#   3]+0.002*[#   4]+0.002*[#   6]+0.002*[#   7]
          +0.002*[#   8]
    |psi|^2 = 0.011
==== e(  14) =    22.67247 eV ==== 
     psi = 0.002*[#   2]+0.002*[#   3]+0.002*[#   4]+0.002*[#   6]+0.002*[#   7]
          +0.002*[#   8]
    |psi|^2 = 0.011
==== e(  15) =    24.82663 eV ==== 

    |psi|^2 = 0.005
==== e(  16) =    24.82663 eV ==== 

    |psi|^2 = 0.005

Lowdin Charges: 

     Atom #   1: total charge =   3.9638, s =  1.1614, 
     Atom #   1: total charge =   3.9638, p =  2.8024, pz=  0.9341, px=  0.9341, py=  0.9341, 
     Atom #   2: total charge =   3.9638, s =  1.1614, 
     Atom #   2: total charge =   3.9638, p =  2.8024, pz=  0.9341, px=  0.9341, py=  0.9341, 
     Spilling Parameter:   0.0091

     PROJWFC      :      0.19s CPU      0.28s WALL


   This run was terminated on:  19:32:26  31Oct2025            

=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=
```
Plots: analysis/Si/plots/si_pdos.png
## Si band summary
```
# Silicon band summary (derived from silicon.bands.dat.gnu)
Fermi level (from silicon.dos)  :   6.2200 eV
Valence band maximum            :   6.2198 eV at k-index 0 (s = 0.0000)
Conduction band minimum         :   6.7897 eV at k-index 34 (s = 0.8500)
Indirect gap (Cmin - Vmax)      :   0.5699 eV
Direct gap (min over k)         :   2.5598 eV at k-index 0 (s = 0.0000)
```
