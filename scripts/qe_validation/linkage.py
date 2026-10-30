"""Resolve Mach-O non-system dependency closure instead of guessing from otool text."""
from pathlib import Path
import platform
import re
import subprocess
from .core import ValidationError, sha256

def inspect_binary(exe: Path) -> dict:
    root=exe.resolve()
    closure={}
    def inspect(path, inherited):
        path=path.resolve()
        if str(path) in closure:return
        file=subprocess.run(['file',str(path)],capture_output=True,text=True,check=True)
        if platform.machine()=='arm64' and 'arm64' not in file.stdout:
            raise ValidationError('ARCHITECTURE_MISMATCH',str(path),'BLOCKED')
        listing=subprocess.run(['otool','-L',str(path)],capture_output=True,text=True,check=True).stdout
        load=subprocess.run(['otool','-l',str(path)],capture_output=True,text=True,check=True).stdout
        raw_rpaths=re.findall(r'cmd LC_RPATH\s+cmdsize \d+\s+path (.+?) \(offset',load)
        expand=lambda name:name.replace('@loader_path',str(path.parent)).replace('@executable_path',str(root.parent))
        rpaths=[Path(expand(p)) for p in raw_rpaths]+inherited
        deps=[]
        closure[str(path)]={'sha256':sha256(path),'architecture':file.stdout.strip(),'dependencies':deps}
        for line in listing.splitlines()[1:]:
            name=line.strip().split(' (compatibility')[0]
            if not name:continue
            # Apple system libraries may reside only in the dyld shared cache.
            if name.startswith(('/usr/lib/','/System/Library/')):
                deps.append({'install_name':name,'resolution':'system shared cache'});continue
            if name.startswith('@rpath/'):
                candidates=[p/name[len('@rpath/'):] for p in rpaths]
            else:candidates=[Path(expand(name))]
            resolved=next((p.resolve() for p in candidates if p.is_file()),None)
            if resolved is None:
                raise ValidationError('DYLIB_UNRESOLVED',f'{path}: {name}','BLOCKED')
            deps.append({'install_name':name,'resolved':str(resolved)})
            inspect(resolved,rpaths)
    inspect(root,[])
    return {'executable':str(root),'closure':closure,'scope':'Resolved architecture/dependency identity; real numerical loader proof is a separate case'}
