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

    if not local.exists():
        local.symlink_to(Path(usr_path()) / reg)

    return cwd


def arch(filename: str):
    with open(filename, 'rb') as fp:
        magic = fp.read(16)

    if magic.startswith(b'dyld_v1') and magic.endswith(b'\x00'):
        return magic.rstrip(b'\x00').split(' ').pop()

    raise ValueError('invalid file %s' % filename)


def main(filename: str):
    # disable ida plugins
    env = {'IDAUSR': make_env()}
    env.update(os.environ)

    py = Path(__file__).parent / 'auto.py'
    basename = os.path.basename(filename)
    output = basename + '.i64'
    log = basename + '.log'

    args = ['idat64', '-c', '-A', '-S%s' % py, '-L%s' % log]

    PREFIX = 'dyld_shared_cache_'
    if basename.startswith(PREFIX):
        arch = basename[len(PREFIX):]
        args += ['-TApple DYLD cache for %s (complete image)' % arch]

    args += ['-o%s' % output, filename]

    subprocess.run(args, env=env)


if __name__ == '__main__':
    # time idat64 -c -A -Sauto.py -Lcache2.log -odscmac.i64 /System/Library/dyld/dyld_shared_cache_arm64e
    # todo: argparse
    if len(sys.argv) < 2:
        print('usage: run.py dyld_shared_cache')

    main(sys.argv[1])
