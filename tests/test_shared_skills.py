"""Shared package ownership and recovery, using isolated synthetic sources."""
from __future__ import annotations

import copy
import hashlib
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from test_installer import hbt


def put_skill(root, name, body="original"):
    path = root / name
    path.mkdir(parents=True, exist_ok=True)
    (path / "SKILL.md").write_text(f"---\nname: {name}\ndescription: fixture\n---\n{body}\n")
    (path / "support.txt").write_text("support")
    return path


def origin(path):
    return hashlib.sha256(hbt.json.dumps(hbt.package_hashes(path), sort_keys=True).encode()).hexdigest()


class SharedSkills(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.env = patch.dict(os.environ, {"HOME": str(self.home), "HERMES_HOME": str(self.home / ".hermes")})
        self.env.start()
        self.addCleanup(self.env.stop)
        self.tpl = copy.deepcopy(hbt.load_template("creator"))
        self.tpl.path = self.home / "template"
        self.role = copy.deepcopy(self.tpl.roles[2])
        self.role.stock_skills = ["stock"]
        self.tpl.roles = [self.role]
        self.prof = hbt.hermes_home() / "profiles" / self.role.key
        self.prof.mkdir(parents=True)
        self.authored = put_skill(self.tpl.path / "roles" / self.role.key / "skills", "authored")
        stock = put_skill(self.home / "native" / "category", "stock")
        self.native = {"root": self.home / "native", "packages": {"stock": stock}, "source": "synthetic-native",
                       "matches": lambda p, expected: bool(expected) and origin(p) == expected}
        self.rec = {"version": "0.3.2", "profiles": [self.role.key], "hermes_version": "synthetic"}
        self.local_stock = self.prof / "skills" / "category" / "stock"
        shutil.copytree(stock, self.local_stock)
        (self.prof / "skills" / ".bundled_manifest").write_text("stock:" + origin(self.local_stock) + "\n")
        shutil.copytree(self.authored, self.prof / "skills" / "authored")
        stage = hbt.record_dir(self.tpl.name) / "dist" / self.role.key
        shutil.copytree(self.tpl.path / "roles" / self.role.key, stage)
        (stage / "distribution.yaml").write_text("version: 0.3.2\n")
        (self.prof / "distribution.yaml").write_text(hbt.yaml.safe_dump({"version": "0.3.2", "source": str(stage)}))
        self.settings = {"model": {"default": "test"}, "skills": {"external_dirs": [], "disabled": ["stock"],
                         "platform_disabled": {"slack": ["authored"]}, "auto_load": [], "create_dir": "my-skills"}}
        (self.prof / "config.yaml").write_text(hbt.yaml.safe_dump(self.settings))

    def plan(self, fresh=False):
        return hbt.plan_shared_skills(self.tpl, [self.role], self.rec, self.native, fresh=fresh)

    def apply(self, fresh=False):
        plan = self.plan(fresh)
        hbt.apply_shared_skills(self.tpl, self.rec, plan)
        return plan

    def test_dry_planning_zero_writes(self):
        before = hbt.package_hashes(self.home)
        self.plan()
        self.assertEqual(before, hbt.package_hashes(self.home))

    def test_support_script_is_installed_with_package(self):
        source = put_skill(self.home / "fixture", "support-example")
        (source / "scripts").mkdir()
        (source / "scripts/check.py").write_text("print('fixture')\n")
        target = self.tpl.path / "roles" / self.role.key / "skills" / source.name
        shutil.copytree(source, target)
        self.apply(fresh=True)
        installed = Path(self.rec["shared_skills"]["root"]) / "template" / self.role.key / source.name
        self.assertEqual(hbt.package_hashes(installed), hbt.package_hashes(source))
        self.assertEqual((installed / "scripts/check.py").read_bytes(),
                         (source / "scripts/check.py").read_bytes())
        self.assertIn(str(installed), hbt._profile_cfg(self.role.key)["skills"]["external_dirs"])

    def test_pristine_migration_and_repeat_preserve_settings(self):
        self.apply()
        cfg = hbt._profile_cfg(self.role.key)
        expected = copy.deepcopy(self.settings)
        expected["skills"]["external_dirs"] = self.rec["shared_skills"]["profiles"][self.role.key]["managed"]
        self.assertEqual(cfg, expected)
        self.assertFalse(self.local_stock.exists())
        self.assertFalse((self.prof / "skills" / "authored").exists())
        first = copy.deepcopy(self.rec["shared_skills"]["profiles"])
        self.apply()
        self.assertEqual(self.rec["shared_skills"]["profiles"], first)
        self.assertEqual(hbt._profile_cfg(self.role.key), expected)

    def test_support_file_addition_stays_local_and_is_archived(self):
        (self.local_stock / "extra.txt").write_bytes(b"custom\x00data")
        before = hbt.package_hashes(self.local_stock)
        self.apply()
        entry = self.rec["shared_skills"]["profiles"][self.role.key]
        self.assertFalse(any(p.endswith("/stock") for p in entry["managed"]))
        self.assertTrue(self.rec["shared_skills"]["conflicts"])
        self.assertEqual(hbt.package_hashes(self.local_stock), before)
        archive = Path(self.rec["shared_skills"]["backups"][-1])
        self.assertEqual(hbt.package_hashes(archive / "profiles" / self.role.key / "skills/category/stock"), before)
        self.apply()
        self.assertEqual(hbt.package_hashes(self.local_stock), before)

    def test_uninstall_archives_internal_external_and_creation_packages(self):
        self.apply()
        external = put_skill(self.prof / "custom-external", "owner-only", "external bytes")
        created = put_skill(self.prof / "my-skills", "owner-created", "creation bytes")
        outside = put_skill(self.home / "outside", "untouched", "outside bytes")
        (external / "binary.dat").write_bytes(b"\x00\xffowner")
        (external.parent / "unrelated-secret").write_text("do not archive")
        expected = {p.relative_to(self.prof): hbt.package_hashes(p) for p in [external, created]}
        outside_before = hbt.package_hashes(outside)
        cfg = hbt._profile_cfg(self.role.key)
        cfg["skills"]["external_dirs"] += ["${HERMES_HOME}/custom-external", str(outside)]
        (self.prof / "config.yaml").write_text(hbt.yaml.safe_dump(cfg))
        hbt.uninstall_shared_skills(self.tpl.name, self.rec, False)
        archive = Path(self.rec["skill_uninstall_archives"][-1]) / "profiles" / self.role.key
        shutil.rmtree(self.prof)  # Model native whole-profile deletion.
        for rel, hashes in expected.items():
            self.assertEqual(hbt.package_hashes(archive / rel), hashes)
        self.assertFalse((archive / "custom-external/unrelated-secret").exists())
        self.assertEqual(hbt.package_hashes(outside), outside_before)

    def test_uninstall_archives_ancestor_root_packages_only_in_removed_profiles(self):
        self.apply()
        custom = put_skill(self.prof / "custom-external", "ancestor-owner", "unique owner bytes")
        (custom / "binary.dat").write_bytes(b"\x00\xffowner")
        (custom.parent / "unrelated-secret").write_text("do not archive")
        outside = put_skill(self.prof.parent / "unrelated-profile", "outside-owner")
        second = self.prof.parent / "second-removed"
        second_package = put_skill(second / "skills", "second-owner")
        second_before = hbt.package_hashes(second_package)
        self.rec["profiles"].append(second.name)
        expected = hbt.package_hashes(custom)
        outside_before = hbt.package_hashes(outside)
        cfg = hbt._profile_cfg(self.role.key)
        cfg["skills"]["external_dirs"].insert(0, str(self.prof.parent))
        (self.prof / "config.yaml").write_text(hbt.yaml.safe_dump(cfg))
        self.apply()
        self.apply()
        hbt.uninstall_shared_skills(self.tpl.name, self.rec, False)
        archive = Path(self.rec["skill_uninstall_archives"][-1])
        shutil.rmtree(self.prof)  # Model native whole-profile deletion.
        self.assertEqual(hbt.package_hashes(archive / "profiles" / self.role.key /
                                            "custom-external/ancestor-owner"), expected)
        self.assertFalse((archive / "profiles" / self.role.key /
                          "custom-external/unrelated-secret").exists())
        self.assertFalse((archive / "profiles/unrelated-profile").exists())
        self.assertEqual(hbt.package_hashes(archive / "profiles/second-removed/skills/second-owner"),
                         second_before)
        self.assertEqual(hbt.package_hashes(outside), outside_before)

    def test_profile_scoped_external_collision_and_diagnostics(self):
        self.apply()
        custom = put_skill(self.prof / "custom-external", "stock", "owner bytes")
        before = hbt.package_hashes(custom)
        for raw in ["${HERMES_HOME}/custom-external", "$HERMES_HOME/custom-external", "custom-external"]:
            with self.subTest(raw=raw):
                cfg = hbt._profile_cfg(self.role.key)
                shared = str(Path(self.rec["shared_skills"]["root"]) / "bundled/category/stock")
                cfg["skills"]["external_dirs"] = [raw, shared]
                (self.prof / "config.yaml").write_text(hbt.yaml.safe_dump(cfg))
                self.assertIn("duplicate/ambiguous", "\n".join(hbt.shared_gaps(self.tpl.name, self.rec)))
                self.apply()
                ext = hbt._profile_cfg(self.role.key)["skills"]["external_dirs"]
                self.assertEqual(ext[0], raw)
                self.assertNotIn(shared, ext)
                self.assertTrue(any("custom external" in c for c in self.rec["shared_skills"]["conflicts"]))
                self.assertEqual(hbt.package_hashes(custom), before)
                # Restore recorded ownership for the next independent string variant.
                self.rec["shared_skills"]["profiles"][self.role.key]["managed"].append(shared)

    def test_partial_deletion_recovery_restores_bytes_and_selection(self):
        path = self.prof / "skills/authored"
        before = hbt.package_hashes(path)
        original = shutil.rmtree
        def partial(target, *args, **kwargs):
            if Path(target) == path:
                (path / "SKILL.md").unlink()
                raise OSError("injected partial deletion")
            return original(target, *args, **kwargs)
        with patch.object(hbt.shutil, "rmtree", side_effect=partial):
            with self.assertRaisesRegex(OSError, "partial deletion"):
                self.apply()
        self.assertTrue(path.is_dir())
        hbt.recover_shared_skills(self.tpl.name, self.rec, False)
        self.assertEqual(hbt.package_hashes(path), before)
        self.apply()
        self.assertIn("template/engineer/authored", self.rec["shared_skills"]["profiles"][self.role.key]["selected"])
        self.assertEqual(self.rec["shared_skills"]["migration"], "active")

    def test_recovery_keeps_journal_and_owner_edits(self):
        path = self.prof / "skills/authored"
        with patch.object(hbt, "atomic_yaml", side_effect=OSError("injected")):
            with self.assertRaises(OSError):
                self.apply()
        put_skill(path.parent, path.name, "new owner edit")
        before = hbt.package_hashes(path)
        with self.assertRaisesRegex(SystemExit, "owner edits"):
            hbt.recover_shared_skills(self.tpl.name, self.rec, False)
        self.assertIn("pending", self.rec["shared_skills"])
        self.assertEqual(hbt.package_hashes(path), before)

    def test_unknown_authored_baseline_is_not_permission(self):
        shutil.rmtree(hbt.record_dir(self.tpl.name) / "dist")
        self.apply()
        self.assertTrue((self.prof / "skills/authored/SKILL.md").exists())
        self.assertTrue(any("authored" in c for c in self.rec["shared_skills"]["conflicts"]))

    def test_deleted_packages_stay_deleted(self):
        shutil.rmtree(self.local_stock)
        shutil.rmtree(self.prof / "skills/authored")
        self.apply()
        self.assertEqual(self.rec["shared_skills"]["profiles"][self.role.key]["selected"], [])

    def test_custom_external_collision_omits_shared_root(self):
        custom = put_skill(self.home / "external", "stock", "custom")
        self.settings["skills"]["external_dirs"] = [str(custom)]
        (self.prof / "config.yaml").write_text(hbt.yaml.safe_dump(self.settings))
        shutil.rmtree(self.local_stock)
        self.apply(fresh=True)
        ext = hbt._profile_cfg(self.role.key)["skills"]["external_dirs"]
        self.assertEqual(ext[0], str(custom))
        self.assertEqual(sum(p.endswith("/stock") for p in ext), 1)
        self.assertIn("custom", (custom / "SKILL.md").read_text())

    def test_missing_shared_repaired_local_shadow_kept(self):
        self.apply()
        shared = Path(self.rec["shared_skills"]["root"]) / "bundled/category/stock"
        shutil.rmtree(shared)
        shadow = put_skill(self.prof / "skills", "stock", "owner")
        self.assertIn("missing/changed", "\n".join(hbt.shared_gaps(self.tpl.name, self.rec)))
        self.apply()
        self.assertTrue(shared.exists())
        self.assertIn("owner", (shadow / "SKILL.md").read_text())
        self.assertNotIn(str(shared), hbt._profile_cfg(self.role.key)["skills"]["external_dirs"])

    def test_modified_shared_package_never_overwritten(self):
        self.apply()
        shared = Path(self.rec["shared_skills"]["root"]) / "bundled/category/stock"
        (shared / "support.txt").write_text("edited shared support")
        before = hbt.package_hashes(shared)
        self.apply()
        self.assertEqual(hbt.package_hashes(shared), before)
        self.assertTrue(self.rec["shared_skills"]["conflicts"])

    def test_interrupted_activation_restore_and_retry(self):
        local_before = hbt.package_hashes(self.prof / "skills")
        plan = self.plan()
        with patch.object(hbt, "atomic_yaml", side_effect=OSError("injected activation failure")):
            with self.assertRaises(OSError):
                hbt.apply_shared_skills(self.tpl, self.rec, plan)
        self.assertEqual(self.rec["shared_skills"]["migration"], "activating")
        hbt.recover_shared_skills(self.tpl.name, self.rec, False)
        self.assertEqual(hbt.package_hashes(self.prof / "skills"), local_before)
        self.assertEqual(hbt._profile_cfg(self.role.key), self.settings)
        self.apply()
        self.assertEqual(self.rec["shared_skills"]["conflicts"], [])

    def test_uninstall_restores_owned_settings_and_retains_custom_data(self):
        self.apply()
        custom = put_skill(self.prof / "skills", "custom", "do not lose")
        before = hbt.package_hashes(custom)
        cfg = hbt._profile_cfg(self.role.key)
        cfg["skills"]["auto_load"] = ["custom"]
        cfg["skills"]["external_dirs"].append(str(self.home / "unrelated"))
        (self.prof / "config.yaml").write_text(hbt.yaml.safe_dump(cfg))
        root = Path(self.rec["shared_skills"]["root"])
        changed = root / "bundled/category/stock"
        (changed / "support.txt").write_text("shared edit")
        hbt.uninstall_shared_skills(self.tpl.name, self.rec, False)
        result = hbt._profile_cfg(self.role.key)["skills"]
        self.assertEqual(result["external_dirs"], [str(self.home / "unrelated")])
        self.assertEqual(result["auto_load"], ["custom"])
        self.assertFalse((self.prof / ".no-bundled-skills").exists())
        self.assertTrue(changed.exists())
        self.assertFalse((root / "template/engineer/authored").exists())
        archive = Path(self.rec["skill_uninstall_archives"][-1])
        self.assertEqual(hbt.package_hashes(archive / "profiles/engineer/skills/custom"), before)

    def test_schema_and_symlink_rejected_before_mutation(self):
        target = self.home / "owner-config.yaml"
        target.write_text("owner_setting: keep\n")
        link = self.home / "linked-config.yaml"
        link.symlink_to(target)
        with self.assertRaisesRegex(SystemExit, "symlink"):
            hbt.edit_main_config(link, [], True, False, self.home / "backup")
        self.assertEqual(target.read_text(), "owner_setting: keep\n")
        link.unlink()
        self.apply()
        before = hbt.package_hashes(self.home)
        self.rec["shared_skills"]["schema"] = 99
        with self.assertRaises(SystemExit):
            self.plan()
        self.assertEqual(before, hbt.package_hashes(self.home))
        self.rec["shared_skills"]["schema"] = 1
        shared = Path(self.rec["shared_skills"]["root"]) / "bundled/category/stock"
        shutil.rmtree(shared)
        shared.symlink_to(self.home / "native/category/stock", target_is_directory=True)
        with self.assertRaises(SystemExit):
            self.plan()

    def test_missing_required_stock_fails_preflight(self):
        self.native["packages"] = {}
        before = hbt.package_hashes(self.home)
        with self.assertRaisesRegex(SystemExit, "Upgrade Hermes"):
            self.plan()
        self.assertEqual(before, hbt.package_hashes(self.home))

    def test_source_duplicate_is_explicit_conflict(self):
        root = self.home / "duplicates"
        put_skill(root / "a", "same")
        put_skill(root / "b", "same")
        with self.assertRaisesRegex(SystemExit, "duplicate"):
            hbt.skill_packages(root)

    def test_stage_has_no_skill_payload(self):
        (self.tpl.path / "roles" / self.role.key / "distribution.yaml").write_text("version: 0.4.0\n")
        staged = hbt.stage_distribution(self.tpl, self.role)
        self.assertFalse((staged / "skills").exists())

    def test_missing_file_repaired_without_treating_it_as_an_edit(self):
        self.apply()
        shared = Path(self.rec["shared_skills"]["root"]) / "bundled/category/stock"
        (shared / "support.txt").unlink()
        self.apply()
        self.assertEqual((shared / "support.txt").read_text(), "support")
        self.assertEqual(self.rec["shared_skills"]["conflicts"], [])

    def test_recorded_managed_path_escape_is_rejected(self):
        self.apply()
        self.rec["shared_skills"]["profiles"][self.role.key]["managed"].append(str(self.home / "foreign"))
        with self.assertRaisesRegex(SystemExit, "outside the recorded selection"):
            self.plan()
        with self.assertRaisesRegex(SystemExit, "parent traversal"):
            hbt.checked_path(self.home / "inside/../outside", self.home / "inside")

    def test_original_marker_is_restored_once(self):
        marker = self.prof / ".no-bundled-skills"
        marker.write_text("owner marker\n")
        self.apply()
        self.apply()
        hbt.uninstall_shared_skills(self.tpl.name, self.rec, False)
        self.assertEqual(marker.read_text(), "owner marker\n")

    def test_owner_changes_to_main_settings_survive_uninstall(self):
        path = self.home / "main-config.yaml"
        path.write_text("kanban:\n  review_dispatch: false\n  dispatch_profiles: [original]\n")
        changed = hbt.edit_main_config(path, [], True, False, self.home / "backup", card_profiles=["engineer"])
        y, data = hbt.load_yaml_rt(path)
        data["kanban"]["dispatch_in_gateway"] = False
        data["kanban"]["dispatch_profiles"].append("later")
        hbt.atomic_yaml(path, y, data)
        hbt.revert_main_config(path, {"main_config": changed}, False)
        result = hbt.yaml.safe_load(path.read_text())["kanban"]
        self.assertFalse(result["dispatch_in_gateway"])
        self.assertEqual(result["dispatch_profiles"], ["original", "later"])

    def test_desk_gets_no_shared_roots_and_preserves_custom_settings(self):
        self.apply()
        desk = hbt.hermes_home() / "profiles/desk-editor-fixture"
        desk.mkdir()
        settings = {"terminal": {"backend": "docker", "docker_network": False}, "skills": {"disabled": ["fixture"]}}
        (desk / "config.yaml").write_text(hbt.yaml.safe_dump(settings))
        with patch.object(hbt, "seed_shared_manual") as seed:
            hbt.configure_desk_skills(self.tpl, self.rec, desk.name, self.native)
        self.assertEqual(hbt.yaml.safe_load((desk / "config.yaml").read_text()), settings)
        self.assertEqual(self.rec["shared_skills"]["profiles"][desk.name]["managed"], [])
        self.assertTrue((desk / ".no-bundled-skills").exists())
        seed.assert_called_once()


if __name__ == "__main__":
    unittest.main()
