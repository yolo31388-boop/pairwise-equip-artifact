"""装备神器与养成系统 - 含9个bug"""
from dataclasses import dataclass, field

@dataclass
class Equipment:
    eid: str
    name: str
    level: int = 1
    quality: str = "common"
    slot: str = "weapon"
    is_artifact: bool = False  # bug1: 无条件觉醒
    artifact_level: int = 0
    artifact_skill: str = ""  # bug2: 固定技能

class ArtifactSystem:
    def __init__(self):
        self.equipment: dict[str, Equipment] = {}

    def can_awaken(self, eid: str) -> bool:
        # bug1: 无条件
        return True

    def get_artifact_skill(self, artifact_type: str) -> str:
        # bug2: 固定技能
        return "ultimate_power"

    def get_level_growth(self, level: int) -> float:
        # bug3: 线性增长
        return level * 10.0

    def get_breakthrough_materials(self, level: int) -> dict:
        # bug4: 只耗金币
        return {"gold": 1000}

    def check_resonance(self, artifacts: list) -> dict:
        # bug5: 不看ID只看数量
        if len(artifacts) >= 3:
            return {"bonus": "3piece"}
        return {}

    def get_legacy_rate(self) -> float:
        # bug6: 全继承
        return 1.0

    def is_illusion_unlocked(self, illusion_id: str) -> bool:
        # bug7: 默认开放
        return True

    def can_awaken_slot(self, artifact_slot: str, target_slot: str) -> bool:
        # bug8: 跨部位
        return True

    def get_breakthrough_rate(self, level: int) -> float:
        # bug9: 100%成功
        return 1.0
