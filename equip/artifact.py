"""装备神器与养成系统"""
import math
import random
from dataclasses import dataclass, field

MAX_EQUIP_LEVEL = 100
AWAKEN_QUALITY = "legendary"
LEGACY_RATE = 0.7
RESONANCE_PIECES = 3
BREAKTHROUGH_PITY = 5
ILLUSION_UNLOCK_SOURCES = ("activity", "achievement")

ARTIFACT_SKILLS = {
    "fire": "flame_burst",
    "ice": "frost_nova",
    "thunder": "thunder_strike",
    "holy": "divine_light",
    "dark": "shadow_devour",
}

@dataclass
class Equipment:
    eid: str
    name: str
    level: int = 1
    quality: str = "common"
    slot: str = "weapon"
    is_artifact: bool = False
    artifact_level: int = 0
    artifact_skill: str = ""
    breakthrough_failures: int = 0

class ArtifactSystem:
    def __init__(self):
        self.equipment: dict[str, Equipment] = {}
        self.unlocked_illusions: set[str] = set()

    def can_awaken(self, eid: str) -> bool:
        # 只有传说品质且满级的装备才能觉醒为神器
        equip = self.equipment.get(eid)
        if equip is None:
            return False
        return equip.quality == AWAKEN_QUALITY and equip.level >= MAX_EQUIP_LEVEL

    def get_artifact_skill(self, artifact_type: str) -> str:
        # 按神器类型区分专属技能
        return ARTIFACT_SKILLS.get(artifact_type, f"{artifact_type}_skill")

    def get_level_growth(self, level: int) -> float:
        # 边际递减：等级越高，每级属性增量越小
        if level <= 0:
            return 0.0
        return 10.0 * math.sqrt(level)

    def get_breakthrough_materials(self, level: int) -> dict:
        # 突破需要金币+突破石，等级越高材料越稀有
        materials = {"gold": 1000 * max(1, level)}
        if level >= 3:
            materials["breakthrough_stone"] = level - 2
        if level >= 6:
            materials["rare_essence"] = level - 5
        if level >= 9:
            materials["dragon_crystal"] = level - 8
        return materials

    def check_resonance(self, artifacts: list) -> dict:
        # 按神器ID分组，同ID凑够件数才触发共鸣
        counts: dict[str, int] = {}
        for artifact in artifacts:
            aid = artifact.get("id")
            counts[aid] = counts.get(aid, 0) + 1
        for aid, count in counts.items():
            if count >= RESONANCE_PIECES:
                return {"bonus": f"{RESONANCE_PIECES}piece", "id": aid}
        return {}

    def get_legacy_rate(self) -> float:
        # 传承按比例继承，有损耗
        return LEGACY_RATE

    def unlock_illusion(self, illusion_id: str, source: str) -> bool:
        # 幻化需通过活动或成就解锁
        if source not in ILLUSION_UNLOCK_SOURCES:
            return False
        self.unlocked_illusions.add(illusion_id)
        return True

    def is_illusion_unlocked(self, illusion_id: str) -> bool:
        return illusion_id in self.unlocked_illusions

    def can_awaken_slot(self, artifact_slot: str, target_slot: str) -> bool:
        # 部位限制：武器神器只能觉醒武器
        return artifact_slot == target_slot

    def get_breakthrough_rate(self, level: int) -> float:
        # 突破成功率随等级递减，保底下限5%
        return max(0.05, 0.95 - 0.09 * max(0, level - 1))

    def attempt_breakthrough(self, eid: str, roll: float = None) -> bool:
        # 突破尝试：失败降级，连续失败触发保底必成
        equip = self.equipment[eid]
        if equip.breakthrough_failures >= BREAKTHROUGH_PITY:
            success = True
        else:
            if roll is None:
                roll = random.random()
            success = roll < self.get_breakthrough_rate(equip.artifact_level)
        if success:
            equip.artifact_level += 1
            equip.breakthrough_failures = 0
        else:
            equip.artifact_level = max(0, equip.artifact_level - 1)
            equip.breakthrough_failures += 1
        return success
