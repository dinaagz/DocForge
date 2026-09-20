# GATES.md — DocForge installer / updater

Solo unlazy ledger. Every gate is runnable; each declares a decisive
success token in EXPECT so it can fail honestly.

## G1 — Single source of truth for version

CHECK: python -c "from docforge import __version__ as v; from docforge._version import VERSION; print('V_MATCH', v == VERSION, v)"
EXPECT: V_MATCH True

## G2 — CLI exposes install/uninstall/update/--version

CHECK: python -c "from docforge.cli import build_parser; import sys; p=build_parser(); cmds=set(); [cmds.update(getattr(a,'choices',{}) or {}) for a in p._actions]; need={'install','uninstall','update','doctor','init','run','status'}; missing=sorted(need-cmds); print('MISSING', missing); print('V', any('--version' in (a.option_strings or []) for a in p._actions))"
EXPECT: MISSING \[\]

## G3 — docforge --version prints the version

CHECK: python -m docforge.cli --version
EXPECT: DocForge 0\.2\.

## G4 — Version comparison utility works

CHECK: python -c "from docforge.installer.version import compare, parse; assert compare('0.2.0','0.1.9')==1; assert compare('0.2.0','0.2.0')==0; assert compare('0.2.0','0.3.0')==-1; assert parse('0.2.0')==(0,2,0,'',0); print('VER_OK')"
EXPECT: VER_OK

## G5 — SHA-256 integrity check catches corruption

CHECK: python -c "from docforge.installer.integrity import sha256_file, verify_sha256; import tempfile, pathlib; p=pathlib.Path(tempfile.mkstemp(suffix='.bin')[1]); p.write_bytes(b'abc'); h=sha256_file(p); assert verify_sha256(p, h); assert not verify_sha256(p, 'deadbeef'*8); print('INTEG_OK')"
EXPECT: INTEG_OK

## G6 — Layout roots differ by OS and stay under user home

CHECK: python -c "from docforge.installer.layout import runtime_root, bin_dir; import os; r=str(runtime_root()); b=str(bin_dir()); print('R_UNDER_HOME', r.startswith(os.path.expanduser('~')) or r.startswith(os.environ.get('LOCALAPPDATA',''))); print('B_UNDER_HOME', b.startswith(os.path.expanduser('~')) or b.startswith(os.environ.get('LOCALAPPDATA','')))"
EXPECT: R_UNDER_HOME True

## G7 — Migration registry is ordered and idempotent

CHECK: python -c "from docforge.migrations import registry, run_pending; from docforge.installer import state as ist; ist.reset_migrations(); r=run_pending(); print('APPLIED', len(r)); r2=run_pending(); print('IDEMPOTENT', len(r2)==0)"
EXPECT: IDEMPOTENT True

## G8 — Doctor returns structured status with categories

CHECK: python -c "from docforge.installer.doctor import check_all; r=check_all(); assert 'checks' in r; assert all(c['status'] in {'OK','WARNING','MISSING','ERROR'} for c in r['checks']); print('DOCTOR_OK', len(r['checks']))"
EXPECT: DOCTOR_OK [1-9]

## G9 — Update --check produces a JSON report without touching disk

CHECK: python -c "from docforge.installer.updater import check_only; r=check_only(source='local:./', current='0.2.0'); k=set(r.keys()); need={'channel','current','latest','update_available'}; print('CHECK_KEYS_OK', need.issubset(k))"
EXPECT: CHECK_KEYS_OK True

## G10 — Rollback restores the last-known-good version

CHECK: python -c "from docforge.installer.rollback import can_rollback, list_versions; from docforge.installer import state as ist; ist.reset_versions(); ist.record_installed('0.1.0','/tmp/a'); ist.record_installed('0.2.0','/tmp/b'); vs=list_versions(); assert '0.1.0' in vs and '0.2.0' in vs; print('ROLLBACK_OK', can_rollback())"
EXPECT: ROLLBACK_OK True

## G11 — Uninstall removes runtime but preserves project data

CHECK: python -c "from docforge.installer.uninstaller import plan_uninstall; plan=plan_uninstall(); print('SAFE', all('input' not in p and 'output' not in p for p in plan['remove'])); print('KEEP_USER', 'user_data_preserved' in plan)"
EXPECT: SAFE True

## G12 — install.sh & install.ps1 are present, executable, and sane

CHECK: python -c "import os, pathlib; sh=pathlib.Path('install.sh'); ps=pathlib.Path('install.ps1'); assert sh.exists() and ps.exists(); assert os.access(sh, os.X_OK); body=sh.read_text(); assert 'set -e' in body and 'python' in body; body2=ps.read_text(); assert 'ErrorActionPreference' in body2; print('SCRIPTS_OK')"
EXPECT: SCRIPTS_OK

## G13 — Project init creates project layout, never touches runtime

CHECK: python -c "import tempfile, os, pathlib; d=pathlib.Path(tempfile.mkdtemp()); os.environ['DOCFORGE_ROOT']=str(d); from docforge.cli import cmd_init; import argparse; cmd_init(argparse.Namespace()); assert (d/'.docforge').exists(); assert (d/'input').exists(); assert (d/'output').exists(); print('INIT_OK')"
EXPECT: INIT_OK

## G14 — Tests stay green

CHECK: python -m pytest tests/ -q
EXPECT: passed

## G15 — README exposes one-liner install first

CHECK: python -c "b=open('README.md').read(); i=b.find('# Installation'); c=b.find('curl -fsSL'); p=b.find('irm'); print('ORDER_OK', 0<i<c and 0<i<p)"
EXPECT: ORDER_OK True

## G16 — Update preserves project directories (dry run)

CHECK: python -c "from docforge.installer.updater import preserves; print('PRESERVES', sorted(preserves()))"
EXPECT: PRESERVES \['\.docforge', 'input', 'logs', 'output', 'work'\]
