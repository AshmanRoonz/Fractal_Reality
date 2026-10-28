"""Rebuild φ-Entrainment's two pages: docs/phi_resonance.html and docs/phi_resonance_composer.html.

Created: 2026-10-28
Last updated: 2026-10-28
Version: 1.0

Usage, from anywhere:

    python tools/phi_resonance_build/build.py

Both pages are built in a temporary folder and copied into docs/ only when every step passes:
1. The base page (phi_resonance_before_redesign.html: docs/phi_resonance.html at commit 60e3fae5,
   the lab page before its redesign) is copied in as phi_resonance.html.
2. redesign_patch.py gives it the Last Ship Sailing interface and every later change, section by
   section. Each anchor must match exactly, or the build stops.
3. build_composer.py makes the Composer edition, phi_resonance_composer.html.
4. check_page.py checks each page's script (node --check) and the element ids it looks up.

Both pages are rewritten from scratch, so change them here, never by hand.

Revision history:
- 2026-10-28 v1.0: initial (the pipeline moved here from a session's temporary folder)
"""
import os
import shutil
import subprocess
import sys
import tempfile

here = os.path.dirname(os.path.abspath(__file__))
docs = os.path.join(os.path.dirname(os.path.dirname(here)), 'docs')
names = ('phi_resonance.html', 'phi_resonance_composer.html')
work = tempfile.mkdtemp(prefix='phi_resonance_build_')
plain, composer = [os.path.join(work, n) for n in names]


def run(script, *args):
    if subprocess.run([sys.executable, os.path.join(here, script), *args]).returncode:
        sys.exit('%s stopped the build; docs/ is unchanged, and the work so far is in %s' % (script, work))


shutil.copyfile(os.path.join(here, 'phi_resonance_before_redesign.html'), plain)
run('redesign_patch.py', plain)
run('build_composer.py', plain, composer)
for page in (plain, composer):
    print('check', os.path.basename(page), flush=True)
    run('check_page.py', page, work)
for n in names:
    shutil.copyfile(os.path.join(work, n), os.path.join(docs, n))
    print('wrote docs/' + n)
shutil.rmtree(work)
