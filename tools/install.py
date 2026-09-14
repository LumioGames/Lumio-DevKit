#!/usr/bin/env python3
"""Install the complete DevKit payload and link its skills. Standard library only."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile


def exists(path):
    return os.path.lexists(path)


def digest(root):
    value = hashlib.sha256()
    for path in sorted(root.rglob('*')):
        if path.is_symlink():
            raise ValueError(f'package symlink is not supported: {path}')
        if path.is_file():
            name = path.relative_to(root).as_posix().encode()
            data = path.read_bytes()
            value.update(len(name).to_bytes(8, 'big') + name)
            value.update(len(data).to_bytes(8, 'big') + data)
    return value.hexdigest()


def overlaps(a, b):
    return a == b or a in b.parents or b in a.parents


def owned_link(path, expected):
    return path.is_symlink() and os.readlink(path) == str(expected)


def install(source, data, target, dry_run=False):
    source, data, target = (Path(p).expanduser().resolve() for p in (source, data, target))
    for a, b in [(source, data), (source, target), (data, target)]:
        if overlaps(a, b):
            raise ValueError(f'source, data and skill directories must not overlap: {a}, {b}')
    checksum = digest(source)
    meta = json.loads((source/'plugin.json').read_text(encoding='utf-8'))
    if meta.get('name') != 'lumio-devkit':
        raise ValueError('source is not a lumio-devkit plugin')
    names = []
    for folder in sorted((source/'skills').iterdir()):
        if (not re.fullmatch(r'lumio-[a-z0-9]+(?:-[a-z0-9]+)*', folder.name)
                or not (folder/'SKILL.md').is_file()):
            raise ValueError(f'invalid skill entry: {folder}')
        names.append(folder.name)
    if not names:
        raise ValueError('source contains no skills')
    current, releases, state_path = data/'plugin', data/'releases', data/'install-state.json'
    for p in [releases, state_path]:
        if p.is_symlink():
            raise ValueError(f'install conflict: unexpected symlink {p}')
    state = json.loads(state_path.read_text()) if state_path.exists() else {'targets': {}}
    targets = state.get('targets')
    if not isinstance(targets, dict):
        raise ValueError('invalid installation state; no files changed')
    targets = dict(targets)
    targets.setdefault(str(target), [])
    if exists(current) and (not current.is_symlink() or current.resolve().parent != releases
                            or not state_path.exists()):
        raise ValueError(f'install conflict: unmanaged payload {current}')
    if current.is_symlink() and digest(current.resolve()) != state.get('digest'):
        raise ValueError('current installed payload was modified; preserve your edits before updating')
    # All registered target roots share this payload; preflight before switching it.
    for root_name, old_names in targets.items():
        folder = Path(root_name)
        if (not folder.is_absolute() or folder.resolve() != folder
                or overlaps(folder, source) or overlaps(folder, data)
                or not isinstance(old_names, list)
                or any(not isinstance(n, str) or not re.fullmatch(r'lumio-[a-z0-9]+(?:-[a-z0-9]+)*', n) for n in old_names)):
            raise ValueError('invalid or overlapping installation target in state')
        for name in set(names) | set(old_names):
            link = folder/name
            if exists(link) and not owned_link(link, current/'skills'/name):
                raise ValueError(f'install conflict: {link}; move it yourself before installing')
    release = releases/checksum
    if release.exists() and digest(release) != checksum:
        raise ValueError('installed release was modified; preserve your edits before reinstalling')
    if dry_run:
        return {'version': meta.get('version'), 'skills': names, 'payload': str(current), 'dryRun': True}

    data.mkdir(parents=True, exist_ok=True)
    lock = data/'.install-lock'
    try:
        lock.mkdir()
    except FileExistsError:
        raise ValueError(f'install already running (or interrupted): {lock}; inspect before removing') from None
    added, removed = [], []
    old_current = None
    switched = False
    temp = None
    try:
        # A competing installer may have finished after preflight.
        if state_path.exists() and json.loads(state_path.read_text()) != state:
            raise ValueError('installation changed during preflight; rerun')
        old_current = os.readlink(current) if current.is_symlink() else None
        releases.mkdir(exist_ok=True)
        if not release.exists():
            temp = Path(tempfile.mkdtemp(prefix='.stage-', dir=data))
            shutil.copytree(source, temp/'payload')
            if digest(temp/'payload') != checksum:
                raise ValueError('source changed during copy; rerun against a stable checkout')
            (temp/'payload').rename(release)
        for root_name, old_names in targets.items():
            folder = Path(root_name)
            folder.mkdir(parents=True, exist_ok=True)
            for name in names:
                link = folder/name
                if exists(link) and not owned_link(link, current/'skills'/name):
                    raise ValueError(f'install conflict during update: {link}')
                if not exists(link):
                    link.symlink_to(current/'skills'/name, target_is_directory=True)
                    added.append(link)
            for name in set(old_names) - set(names):
                link = folder/name
                if owned_link(link, current/'skills'/name):
                    link.unlink()
                    removed.append((link, current/'skills'/name))
        switch = data/'.plugin-next'
        if exists(switch):
            raise ValueError(f'previous installation left {switch}; inspect before removing')
        switch.symlink_to(release, target_is_directory=True)
        os.replace(switch, current)
        switched = True
        new_state = {'version': meta.get('version'), 'digest': checksum,
                     'targets': {root_name: names for root_name in targets}}
        temporary_state = data/'.install-state-next.json'
        temporary_state.write_text(json.dumps(new_state, indent=2)+'\n', encoding='utf-8')
        os.replace(temporary_state, state_path)
    except Exception:
        for link in added:
            if owned_link(link, current/'skills'/link.name):
                link.unlink()
        for link, dest in removed:
            if not exists(link):
                link.symlink_to(dest, target_is_directory=True)
        if switched and old_current is not None:
            rollback = data/'.plugin-rollback'
            rollback.symlink_to(old_current, target_is_directory=True)
            os.replace(rollback, current)
        elif switched and current.is_symlink():
            current.unlink()
        raise
    finally:
        if temp is not None:
            shutil.rmtree(temp)
        lock.rmdir()
    return {'version': meta.get('version'), 'skills': names, 'payload': str(current), 'target': str(target)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path(__file__).resolve().parents[1]/'plugin')
    parser.add_argument('--target', type=Path, default=Path.home()/'.codex/skills')
    parser.add_argument('--data-dir', type=Path,
                        default=Path(os.environ.get('XDG_DATA_HOME') or Path.home()/'.local/share')/'lumio-devkit')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    try:
        result = install(args.source, args.data_dir, args.target, args.dry_run)
    except Exception as error:
        print(f'INSTALL_FAILED: {error}', file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print('Start a new agent session to discover the six skills. No account, hooks or credentials changed.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
