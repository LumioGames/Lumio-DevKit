import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

MODULE = Path(__file__).resolve().parents[1] / 'tools/install.py'
spec = importlib.util.spec_from_file_location('devkit_install', MODULE)
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class InstallChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.source, self.data, self.target = root/'source', root/'data', root/'skills'
        (self.source/'skills/lumio-development').mkdir(parents=True)
        (self.source/'plugin.json').write_text(json.dumps({'name': 'lumio-devkit', 'version': '0.2.0'}))
        (self.source/'skills/lumio-development/SKILL.md').write_text('entry')
        (self.source/'guide.md').write_text('guide v1')

    def test_installs_complete_package_and_skill_links(self):
        installer.install(self.source, self.data, self.target)
        self.assertTrue((self.data/'plugin').is_symlink())
        self.assertEqual((self.data/'plugin/guide.md').read_text(), 'guide v1')
        self.assertTrue((self.target/'lumio-development').is_symlink())
        self.assertEqual((self.target/'lumio-development/SKILL.md').read_text(), 'entry')

    def test_repeat_and_update_preserve_old_payload(self):
        installer.install(self.source, self.data, self.target)
        self.assertTrue((self.data/'plugin').is_symlink())
        first = (self.data/'plugin').resolve()
        installer.install(self.source, self.data, self.target)
        self.assertEqual(first, (self.data/'plugin').resolve())
        (self.source/'guide.md').write_text('guide v2')
        installer.install(self.source, self.data, self.target)
        self.assertNotEqual(first, (self.data/'plugin').resolve())
        self.assertEqual((first/'guide.md').read_text(), 'guide v1')
        self.assertEqual((self.data/'plugin/guide.md').read_text(), 'guide v2')

    def test_conflict_does_not_modify_installed_package(self):
        installer.install(self.source, self.data, self.target)
        self.assertTrue((self.data/'plugin').is_symlink())
        first = (self.data/'plugin').resolve()
        (self.source/'skills/lumio-server').mkdir()
        (self.source/'skills/lumio-server/SKILL.md').write_text('server')
        (self.target/'lumio-server').mkdir()
        (self.target/'lumio-server/mine.txt').write_text('keep')
        with self.assertRaisesRegex(ValueError, 'conflict'):
            installer.install(self.source, self.data, self.target)
        self.assertEqual(first, (self.data/'plugin').resolve())
        self.assertEqual((self.target/'lumio-server/mine.txt').read_text(), 'keep')

    def test_foreign_symlink_is_not_overwritten(self):
        self.target.mkdir()
        (self.target/'lumio-development').symlink_to(self.source/'skills/lumio-development')
        with self.assertRaisesRegex(ValueError, 'conflict'):
            installer.install(self.source, self.data, self.target)
        self.assertFalse(self.data.exists())

    def test_package_escape_is_rejected_before_writing(self):
        (self.source/'escaped').symlink_to(self.source.parent)
        with self.assertRaisesRegex(ValueError, 'symlink'):
            installer.install(self.source, self.data, self.target)
        self.assertFalse(self.data.exists())

    def test_overlap_with_source_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'overlap'):
            installer.install(self.source, self.source/'data', self.target)
        self.assertFalse((self.source/'data').exists())

    def test_dry_run_does_not_write(self):
        installer.install(self.source, self.data, self.target, dry_run=True)
        self.assertFalse(self.data.exists())
        self.assertFalse(self.target.exists())

    def test_tampered_existing_release_is_rejected(self):
        installer.install(self.source, self.data, self.target)
        self.assertTrue((self.data/'plugin/guide.md').is_file())
        (self.data/'plugin/guide.md').write_text('tampered')
        with self.assertRaisesRegex(ValueError, 'modified'):
            installer.install(self.source, self.data, self.target)

    def test_update_removes_retired_owned_skill_link(self):
        (self.source/'skills/lumio-server').mkdir()
        (self.source/'skills/lumio-server/SKILL.md').write_text('server')
        installer.install(self.source, self.data, self.target)
        self.assertTrue((self.target/'lumio-server').is_symlink())
        (self.source/'skills/lumio-server/SKILL.md').unlink()
        (self.source/'skills/lumio-server').rmdir()
        installer.install(self.source, self.data, self.target)
        self.assertFalse((self.target/'lumio-server').is_symlink())

class MultiTargetChecks(unittest.TestCase):
    setUp = InstallChecks.setUp

    def test_multi_target_update_keeps_all_links_live(self):
        other = self.target.parent/'other-skills'
        installer.install(self.source, self.data, self.target)
        installer.install(self.source, self.data, other)
        (self.source/'skills/lumio-server').mkdir()
        (self.source/'skills/lumio-server/SKILL.md').write_text('server')
        installer.install(self.source, self.data, other)
        for folder in [self.target, other]:
            self.assertEqual((folder/'lumio-server/SKILL.md').read_text(), 'server')

    def test_unmanaged_payload_is_not_replaced(self):
        (self.data/'plugin').mkdir(parents=True)
        (self.data/'plugin/mine.txt').write_text('keep')
        with self.assertRaisesRegex(ValueError, 'conflict'):
            installer.install(self.source, self.data, self.target)
        self.assertEqual((self.data/'plugin/mine.txt').read_text(), 'keep')

if __name__ == '__main__':
    unittest.main()
