#!/usr/bin/env python3

import os
import sys
import subprocess
from pathlib import Path


def usr_path() -> str:
    if sys.platform == 'win32':
        return os.path.expandvars('%APPDATA%\\Hex-Rays\\IDA Pro')
    return os.path.expanduser('~/.idapro')


def make_env(prefered=None) -> Path:
    if prefered is None:
        cwd = Path(__file__).parent / '.idapro'
    else:
        cwd = Path(prefered)

    if not cwd.is_dir():
        cwd.mkdir()

    reg = 'ida.reg'
    local = cwd / reg

    if not local.is_symlink():
        local.symlink_to(Path(usr_path()) / reg)

    return cwd


def main(filename: str):
    # disable ida plugins
    env = {'IDAUSR': make_env()}
    env.update(os.environ)
    py = Path(__file__).parent / 'auto.py'
    basename = os.path.basename(filename)
    output = basename + '.i64'
    log = basename + '.log'
    subprocess.run(['idat64', '-c', '-A', '-S%s' % py, '-L%s' %
                   log, '-o%s' % output, filename])


if __name__ == '__main__':
    # time idat64 -c -A -Sauto.py -Lcache2.log -odscmac.i64 /System/Library/dyld/dyld_shared_cache_arm64e
    # todo: argparse
    if len(sys.argv) < 2:
        print('usage: run.py dyld_shared_cache')

    main(sys.argv[1])
