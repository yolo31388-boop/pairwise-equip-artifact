"""装备神器与养成系统"""
import random
from dataclasses import dataclass, field

EQUIP_MAX_LEVEL = 10
LEGENDARY_QUALITY = "legendary"
LEGACY_RATE = 0.70
BASE_BREAKTHROUGH_RATE = 0.95
BREAKTHROUGH_RATE_DECAY = 0.07
PITY_FAILS = 3

# 神器类型 -> 专属技能
ARTIFACT_SKILLS = {
    "fire": "flame_burst",
    "ice": "frost_nova",
    "thunder": "thunder_strike",
    "wind": "wind_slash",
    "earth": "earth_guard",
    "holy": "holy_judgement",
    "shadow": "shadow_raid",
}

# 突破等级 -> 稀有材料
BREAKTHROUGH_SPECIAL_MATERIALS = {
    1: "refined_ore",
    2: "refined_ore",
    3: "mystic_crystal",
    4: "mystic_crystal",
    5: "mystic_crystal",
    6: "void_essence",
    7: "void_essence",
    8: "void_essence",
    9: "divine_fragment",
    10: "divine_fragment",
}

VALID_SLOTS = ("weapon", "helmet", "armor", "boots", "accessory")


@dataclass
class Equipment:
    eid: str
    name: str
    level: int = 1
    quality: str = "common"
    slot: str = "weapon"
    is_artifact: bool = False
    artifact_level: int = 0
    artifact_type: str = ""
    artifact_slot: str = ""
    artifact_skill: str = ""
    breakthrough_fails: int = 0


class ArtifactSystem:
    def __init__(self):
        self.equipment: dict[str, Equipment] = {}
        # 已解锁的幻化ID（通过活动/成就解锁）
        self.unlocked_illusions: set[str] = set()

    # ---- 觉醒条件：传说品质且满级 ----
    def can_awaken(self, eid: str) -> bool:
        equip = self.equipment.get(eid)
        if equip is None:
            return False
        if equip.is_artifact:
            return False
        return equip.quality == LEGENDARY_QUALITY and equip.level >= EQUIP_MAX_LEVEL

    def awaken(self, eid: str, artifact_type: str = "fire") -> Equipment:
        """觉醒为神器：需满足等级、品质、部位限制。"""
        equip = self.equipment.get(eid)
        if not self.can_awaken(eid):
            raise ValueError("equipment does not meet awaken conditions")
        if not self.can_awaken_slot(equip.slot, equip.slot):
            raise ValueError("slot restriction: artifact type cannot awaken this slot")
        equip.is_artifact = True
        equip.artifact_level = 1
        equip.artifact_type = artifact_type
        equip.artifact_slot = equip.slot
        equip.artifact_skill = self.get_artifact_skill(artifact_type)
        return equip

    # ---- 神器技能：按类型（及属性）区分 ----
    def get_artifact_skill(self, artifact_type: str, element: str = "") -> str:
        if element:
            return f"{ARTIFACT_SKILLS.get(artifact_type, 'arcane_power')}_{element}"
        return ARTIFACT_SKILLS.get(artifact_type, "arcane_power")

    # ---- 升级成长：边际递减 ----
    def get_level_growth(self, level: int) -> float:
        """累计成长，每级增量随等级衰减：increment = 10 * 0.85**(level-1)。"""
        base = 10.0
        decay = 0.85
        if level <= 1:
            return base
        return base * (1.0 - decay ** level) / (1.0 - decay)

    def get_level_increment(self, level: int) -> float:
        """从 level 升到 level+1 的单级属性增量。"""
        return 10.0 * 0.85 ** (level - 1)

    # ---- 突破材料：金币 + 突破石 + 等级对应的稀有材料 ----
    def get_breakthrough_materials(self, level: int) -> dict:
        materials = {
            "gold": 1000 * level,
            "breakthrough_stone": level,
        }
        special = BREAKTHROUGH_SPECIAL_MATERIALS.get(level)
        if special:
            materials[special] = max(1, level // 2)
        return materials

    # ---- 共鸣：按神器ID分组计数 ----
    def check_resonance(self, artifacts: list) -> dict:
        counts: dict[str, int] = {}
        for art in artifacts:
            aid = art["id"] if isinstance(art, dict) else getattr(art, "id")
            counts[aid] = counts.get(aid, 0) + 1
        for aid, count in counts.items():
            if count >= 3:
                return {"bonus": "3piece", "artifact_id": aid}
        return {}

    # ---- 传承：按比例继承，有损耗衰减 ----
    def get_legacy_rate(self) -> float:
        return LEGACY_RATE

    def inherit_legacy(self, source: Equipment, target: Equipment) -> Equipment:
        """把源神器的养成度按70%继承给目标，源神器清零（传承损耗）。"""
        if not source.is_artifact:
            raise ValueError("source is not an artifact")
        target.is_artifact = True
        target.artifact_level = max(1, int(source.artifact_level * LEGACY_RATE))
        target.artifact_type = source.artifact_type
        target.artifact_slot = source.artifact_slot
        target.artifact_skill = source.artifact_skill
        source.is_artifact = False
        source.artifact_level = 0
        source.artifact_skill = ""
        return target

    # ---- 幻化：需通过活动/成就解锁 ----
    def unlock_illusion(self, illusion_id: str) -> None:
        self.unlocked_illusions.add(illusion_id)

    def is_illusion_unlocked(self, illusion_id: str) -> bool:
        return illusion_id in self.unlocked_illusions

    # ---- 部位限制：同部位才能觉醒 ----
    def can_awaken_slot(self, artifact_slot: str, target_slot: str) -> bool:
        return (
            artifact_slot in VALID_SLOTS
            and target_slot in VALID_SLOTS
            and artifact_slot == target_slot
        )

    # ---- 突破成功率：随等级降低，失败降级，连续失败有保底 ----
    def get_breakthrough_rate(self, level: int) -> float:
        rate = BASE_BREAKTHROUGH_RATE - BREAKTHROUGH_RATE_DECAY * (level - 1)
        return max(0.1, round(rate, 4))

    def breakthrough(self, eid: str, rng: random.Random | None = None) -> bool:
        """尝试突破。成功则升1级；失败降1级；连续失败达到保底次数则必成。"""
        rng = rng or random
        equip = self.equipment.get(eid)
        if equip is None or not equip.is_artifact:
            raise ValueError("equipment is not an artifact")

        if equip.breakthrough_fails >= PITY_FAILS:
            equip.artifact_level += 1
            equip.breakthrough_fails = 0
            return True

        if rng.random() < self.get_breakthrough_rate(equip.artifact_level):
            equip.artifact_level += 1
            equip.breakthrough_fails = 0
            return True

        equip.breakthrough_fails += 1
        equip.artifact_level = max(1, equip.artifact_level - 1)
        return False
