"""装备神器与养成系统 - 红态测试"""
import pytest, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from equip.artifact import ArtifactSystem, Equipment

class TestAwakenCondition:
    def test_low_level_cannot_awaken(self):
        asys = ArtifactSystem()
        asys.equipment["e1"] = Equipment("e1", "sword", level=1, quality="common")
        assert asys.can_awaken("e1") == False

class TestArtifactSkill:
    def test_different_artifact_types_different_skills(self):
        asys = ArtifactSystem()
        s1 = asys.get_artifact_skill("fire")
        s2 = asys.get_artifact_skill("ice")
        assert s1 != s2

class TestLevelGrowth:
    def test_high_level_growth_is_diminishing(self):
        asys = ArtifactSystem()
        g1 = asys.get_level_growth(1)
        g10 = asys.get_level_growth(10)
        # 边际递减：10级增长应该小于1级的10倍
        assert g10 < g1 * 10

class TestBreakthroughMaterials:
    def test_high_level_needs_special_materials(self):
        asys = ArtifactSystem()
        m1 = asys.get_breakthrough_materials(1)
        m10 = asys.get_breakthrough_materials(10)
        assert "breakthrough_stone" in m10 or len(m10) > len(m1)

class TestResonanceById:
    def test_mixed_artifacts_dont_trigger_resonance(self):
        asys = ArtifactSystem()
        arts = [{"id": "A"}, {"id": "A"}, {"id": "B"}]
        result = asys.check_resonance(arts)
        assert result == {}

class TestLegacyRate:
    def test_legacy_is_not_full(self):
        asys = ArtifactSystem()
        rate = asys.get_legacy_rate()
        assert rate < 1.0

class TestIllusionUnlock:
    def test_special_illusion_not_default_unlocked(self):
        asys = ArtifactSystem()
        assert asys.is_illusion_unlocked("legendary_illusion") == False

class TestSlotRestriction:
    def test_weapon_artifact_cannot_awaken_armor(self):
        asys = ArtifactSystem()
        assert asys.can_awaken_slot("weapon", "armor") == False

class TestBreakthroughRate:
    def test_high_level_breakthrough_can_fail(self):
        asys = ArtifactSystem()
        r1 = asys.get_breakthrough_rate(1)
        r10 = asys.get_breakthrough_rate(10)
        assert r10 < r1
