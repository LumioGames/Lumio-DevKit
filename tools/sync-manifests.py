#!/usr/bin/env python3
"""Generate host adapters from the portable plugin manifest; never copy skills."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def outputs():
    manifest = json.loads((ROOT/'plugin/plugin.json').read_text(encoding='utf-8'))
    shared = {key: value for key, value in manifest.items() if key != '$schema'}
    claude = dict(shared)
    codex = dict(shared, skills='./skills/', interface={
        'displayName': 'Lumio DevKit',
        'shortDescription': 'Lumio 游戏开发：双端、体素、配表与美术工作流',
        'longDescription': manifest['description'],
        'developerName': manifest['author']['name'],
        'category': 'Developer Tools',
        'capabilities': [],
        'websiteURL': manifest['repository'],
        'defaultPrompt': ['帮我检查 Lumio 项目的开发环境和目录', '定位 Lumio 客户端与服务器的同步问题'],
    })
    marketplace = {
        'name': manifest['name'],
        'description': manifest['description'],
        'owner': manifest['author'],
        'plugins': [{
            'name': manifest['name'], 'source': './plugin',
            'version': manifest['version'], 'description': manifest['description'],
            'homepage': manifest['homepage'], 'repository': manifest['repository'],
            'license': manifest['license'], 'keywords': manifest['keywords'],
        }],
    }
    return {
        'plugin/.claude-plugin/plugin.json': json.dumps(claude, ensure_ascii=False, indent=2)+'\n',
        'plugin/.codex-plugin/plugin.json': json.dumps(codex, ensure_ascii=False, indent=2)+'\n',
        '.claude-plugin/marketplace.json': json.dumps(marketplace, ensure_ascii=False, indent=2)+'\n',
        'plugin/LICENSE': (ROOT/'LICENSE').read_text(encoding='utf-8'),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    stale = []
    for name, content in outputs().items():
        path = ROOT/name
        if args.check:
            if not path.is_file() or path.read_text(encoding='utf-8') != content:
                stale.append(name)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8')
    if stale:
        print('Outdated generated adapters: '+', '.join(stale), file=sys.stderr)
        return 1
    print('Host adapters '+('match portable manifest' if args.check else 'generated'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
