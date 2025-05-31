"""
卡片类型定义系统
Pokemon TCG的卡片类型、属性和基础数据结构
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

class CardType(Enum):
    """卡片类型枚举"""
    POKEMON = "pokemon"
    TRAINER = "trainer"
    ENERGY = "energy"

class PokemonType(Enum):
    """Pokemon属性类型"""
    FIRE = "fire"
    WATER = "water"
    GRASS = "grass"
    ELECTRIC = "electric"
    PSYCHIC = "psychic"
    FIGHTING = "fighting"
    DARKNESS = "darkness"
    METAL = "metal"
    FAIRY = "fairy"
    DRAGON = "dragon"
    NORMAL = "normal"
    COLORLESS = "colorless"
    POISON = "poison"
    UNKNOWN = "unknown"  # 用于未知或特殊情况

class Rarity(Enum):
    """稀有度枚举"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    PROMO = "promo"

class TrainerType(Enum):
    """训练师卡类型"""
    SUPPORTER = "supporter"
    ITEM = "item"
    STADIUM = "stadium"
    TOOL = "tool"

class StatusCondition(Enum):
    """状态异常"""
    BURN = "burn"
    POISON = "poison"
    PARALYSIS = "paralysis"
    SLEEP = "sleep"
    CONFUSION = "confusion"
    FREEZE = "freeze"

@dataclass
class Weakness:
    """弱点数据"""
    type: PokemonType
    multiplier: float = 2.0

@dataclass
class Resistance:
    """抗性数据"""
    type: PokemonType
    reduction: int = 20

@dataclass
class Attack:
    """攻击技能数据"""
    name: str
    cost: List[PokemonType]  # 能量消耗
    damage: int
    description: str = ""
    effects: List[str] = None  # 特殊效果
    
    def __post_init__(self):
        if self.effects is None:
            self.effects = []

@dataclass
class Ability:
    """特性数据"""
    name: str
    description: str
    ability_type: str = "passive"  # passive, active, triggered
    effects: List[str] = None
    
    def __post_init__(self):
        if self.effects is None:
            self.effects = []

class PokemonCard:
    """Pokemon卡片类"""
    
    def __init__(self, card_id: str, name: str, pokemon_type: PokemonType,
                 hp: int, rarity: Rarity, attacks: List[Attack] = None,
                 weakness: Weakness = None, resistance: Resistance = None,
                 retreat_cost: int = 0, ability: Ability = None,
                 evolution_stage: str = "basic", evolves_from: str = None,
                 image_url: str = "", pokedex_number: int = 0):
        """
        初始化Pokemon卡片
        
        Args:
            card_id: 卡片唯一ID
            name: Pokemon名称
            pokemon_type: Pokemon属性
            hp: 生命值
            rarity: 稀有度
            attacks: 攻击技能列表
            weakness: 弱点
            resistance: 抗性
            retreat_cost: 撤退消耗
            ability: 特性
            evolution_stage: 进化阶段 (basic, stage1, stage2, ex, gx, vmax等)
            evolves_from: 进化前形态
            image_url: 图片URL
            pokedex_number: 图鉴编号
        """
        self.card_id = card_id
        self.name = name
        self.card_type = CardType.POKEMON
        self.pokemon_type = pokemon_type
        self.hp = hp
        self.current_hp = hp  # 当前HP（对战中使用）
        self.rarity = rarity
        self.attacks = attacks or []
        self.weakness = weakness
        self.resistance = resistance
        self.retreat_cost = retreat_cost
        self.ability = ability
        self.evolution_stage = evolution_stage
        self.evolves_from = evolves_from
        self.image_url = image_url
        self.pokedex_number = pokedex_number
        
        # 对战状态
        self.is_active = False
        self.is_benched = False
        self.status_conditions = []
        self.attached_energies = []
        self.tools = []
        self.damage_counters = 0
        
        # 特效标记
        self.effects = {}  # 临时效果
        self.markers = {}   # 持久标记
    
    def reset_battle_state(self):
        """重置对战状态"""
        self.current_hp = self.hp
        self.is_active = False
        self.is_benched = False
        self.status_conditions.clear()
        self.attached_energies.clear()
        self.tools.clear()
        self.damage_counters = 0
        self.effects.clear()
        self.markers.clear()
    
    def take_damage(self, damage: int, source_type: PokemonType = None) -> int:
        """
        受到伤害
        
        Args:
            damage: 基础伤害
            source_type: 伤害来源属性
            
        Returns:
            实际造成的伤害
        """
        actual_damage = damage
        
        # 计算弱点
        if self.weakness and source_type == self.weakness.type:
            actual_damage = int(actual_damage * self.weakness.multiplier)
        
        # 计算抗性
        if self.resistance and source_type == self.resistance.type:
            actual_damage = max(0, actual_damage - self.resistance.reduction)
        
        # 应用伤害
        self.current_hp = max(0, self.current_hp - actual_damage)
        self.damage_counters += actual_damage
        
        return actual_damage
    
    def heal(self, amount: int) -> int:
        """
        回复HP
        
        Args:
            amount: 回复量
            
        Returns:
            实际回复的HP
        """
        old_hp = self.current_hp
        self.current_hp = min(self.hp, self.current_hp + amount)
        healed = self.current_hp - old_hp
        self.damage_counters = max(0, self.damage_counters - healed)
        return healed
    
    def is_knocked_out(self) -> bool:
        """是否被击倒"""
        return self.current_hp <= 0
    
    def can_attack(self, attack_index: int) -> bool:
        """
        检查是否可以使用指定攻击
        
        Args:
            attack_index: 攻击索引
            
        Returns:
            是否可以攻击
        """
        if attack_index < 0 or attack_index >= len(self.attacks):
            return False
        
        attack = self.attacks[attack_index]
        
        # 检查能量需求
        energy_count = {}
        for energy in self.attached_energies:
            energy_count[energy] = energy_count.get(energy, 0) + 1
        
        # 检查无色能量需求
        colorless_needed = attack.cost.count(PokemonType.COLORLESS)
        total_energy = sum(energy_count.values())
        
        # 检查特定属性能量需求
        for required_type in attack.cost:
            if required_type != PokemonType.COLORLESS:
                if energy_count.get(required_type, 0) < attack.cost.count(required_type):
                    return False
        
        # 检查总能量是否足够（包括无色）
        specific_energy_used = sum(attack.cost.count(t) for t in attack.cost if t != PokemonType.COLORLESS)
        if total_energy < len(attack.cost):
            return False
        
        return True
    
    def can_retreat(self) -> bool:
        """检查是否可以撤退"""
        if not self.is_active:
            return False
        
        # 检查撤退费用
        energy_count = {}
        for energy in self.attached_energies:
            energy_count[energy] = energy_count.get(energy, 0) + 1
        
        total_energy = sum(energy_count.values())
        return total_energy >= self.retreat_cost
    
    def add_status_condition(self, condition: StatusCondition):
        """添加状态异常"""
        if condition not in self.status_conditions:
            self.status_conditions.append(condition)
    
    def remove_status_condition(self, condition: StatusCondition):
        """移除状态异常"""
        if condition in self.status_conditions:
            self.status_conditions.remove(condition)
    
    def has_status_condition(self, condition: StatusCondition) -> bool:
        """检查是否有指定状态异常"""
        return condition in self.status_conditions
    
    def attach_energy(self, energy_type: PokemonType):
        """附加能量"""
        self.attached_energies.append(energy_type)
    
    def remove_energy(self, energy_type: PokemonType, count: int = 1) -> int:
        """
        移除能量
        
        Args:
            energy_type: 能量类型
            count: 移除数量
            
        Returns:
            实际移除的数量
        """
        removed = 0
        for _ in range(count):
            if energy_type in self.attached_energies:
                self.attached_energies.remove(energy_type)
                removed += 1
        return removed
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'card_id': self.card_id,
            'name': self.name,
            'card_type': self.card_type.value,
            'pokemon_type': self.pokemon_type.value,
            'hp': self.hp,
            'current_hp': self.current_hp,
            'rarity': self.rarity.value,
            'attacks': [
                {
                    'name': attack.name,
                    'cost': [t.value for t in attack.cost],
                    'damage': attack.damage,
                    'description': attack.description,
                    'effects': attack.effects
                }
                for attack in self.attacks
            ],
            'weakness': {
                'type': self.weakness.type.value,
                'multiplier': self.weakness.multiplier
            } if self.weakness else None,
            'resistance': {
                'type': self.resistance.type.value,
                'reduction': self.resistance.reduction
            } if self.resistance else None,
            'retreat_cost': self.retreat_cost,
            'ability': {
                'name': self.ability.name,
                'description': self.ability.description,
                'ability_type': self.ability.ability_type,
                'effects': self.ability.effects
            } if self.ability else None,
            'evolution_stage': self.evolution_stage,
            'evolves_from': self.evolves_from,
            'image_url': self.image_url,
            'pokedex_number': self.pokedex_number,
            'is_active': self.is_active,
            'is_benched': self.is_benched,
            'status_conditions': [c.value for c in self.status_conditions],
            'attached_energies': [e.value for e in self.attached_energies],
            'damage_counters': self.damage_counters
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PokemonCard':
        """从字典创建Pokemon卡片"""
        # 解析攻击
        attacks = []
        for attack_data in data.get('attacks', []):
            attack = Attack(
                name=attack_data['name'],
                cost=[PokemonType(t) for t in attack_data['cost']],
                damage=attack_data['damage'],
                description=attack_data.get('description', ''),
                effects=attack_data.get('effects', [])
            )
            attacks.append(attack)
        
        # 解析弱点
        weakness = None
        if data.get('weakness'):
            weakness = Weakness(
                type=PokemonType(data['weakness']['type']),
                multiplier=data['weakness']['multiplier']
            )
        
        # 解析抗性
        resistance = None
        if data.get('resistance'):
            resistance = Resistance(
                type=PokemonType(data['resistance']['type']),
                reduction=data['resistance']['reduction']
            )
        
        # 解析特性
        ability = None
        if data.get('ability'):
            ability = Ability(
                name=data['ability']['name'],
                description=data['ability']['description'],
                ability_type=data['ability'].get('ability_type', 'passive'),
                effects=data['ability'].get('effects', [])
            )
        
        # 创建卡片
        card = cls(
            card_id=data['card_id'],
            name=data['name'],
            pokemon_type=PokemonType(data['pokemon_type']),
            hp=data['hp'],
            rarity=Rarity(data['rarity']),
            attacks=attacks,
            weakness=weakness,
            resistance=resistance,
            retreat_cost=data.get('retreat_cost', 0),
            ability=ability,
            evolution_stage=data.get('evolution_stage', 'basic'),
            evolves_from=data.get('evolves_from'),
            image_url=data.get('image_url', ''),
            pokedex_number=data.get('pokedex_number', 0)
        )
        
        # 恢复对战状态
        card.current_hp = data.get('current_hp', card.hp)
        card.is_active = data.get('is_active', False)
        card.is_benched = data.get('is_benched', False)
        card.status_conditions = [StatusCondition(c) for c in data.get('status_conditions', [])]
        card.attached_energies = [PokemonType(e) for e in data.get('attached_energies', [])]
        card.damage_counters = data.get('damage_counters', 0)
        
        return card

class TrainerCard:
    """训练师卡片类"""
    
    def __init__(self, card_id: str, name: str, trainer_type: TrainerType,
                 rarity: Rarity, description: str = "", effects: List[str] = None,
                 image_url: str = ""):
        """
        初始化训练师卡片
        
        Args:
            card_id: 卡片ID
            name: 卡片名称
            trainer_type: 训练师卡类型
            rarity: 稀有度
            description: 描述
            effects: 效果列表
            image_url: 图片URL
        """
        self.card_id = card_id
        self.name = name
        self.card_type = CardType.TRAINER
        self.trainer_type = trainer_type
        self.rarity = rarity
        self.description = description
        self.effects = effects or []
        self.image_url = image_url
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'card_id': self.card_id,
            'name': self.name,
            'card_type': self.card_type.value,
            'trainer_type': self.trainer_type.value,
            'rarity': self.rarity.value,
            'description': self.description,
            'effects': self.effects,
            'image_url': self.image_url
        }

class EnergyCard:
    """能量卡片类"""
    
    def __init__(self, card_id: str, name: str, energy_type: PokemonType,
                 rarity: Rarity = Rarity.COMMON, is_basic: bool = True,
                 special_effects: List[str] = None, image_url: str = ""):
        """
        初始化能量卡片
        
        Args:
            card_id: 卡片ID
            name: 卡片名称
            energy_type: 能量类型
            rarity: 稀有度
            is_basic: 是否为基础能量
            special_effects: 特殊效果
            image_url: 图片URL
        """
        self.card_id = card_id
        self.name = name
        self.card_type = CardType.ENERGY
        self.energy_type = energy_type
        self.rarity = rarity
        self.is_basic = is_basic
        self.special_effects = special_effects or []
        self.image_url = image_url
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'card_id': self.card_id,
            'name': self.name,
            'card_type': self.card_type.value,
            'energy_type': self.energy_type.value,
            'rarity': self.rarity.value,
            'is_basic': self.is_basic,
            'special_effects': self.special_effects,
            'image_url': self.image_url
        }

# 工厂函数
def create_card_from_data(card_data: Dict[str, Any]):
    """从数据创建卡片对象"""
    card_type = CardType(card_data['card_type'])
    
    if card_type == CardType.POKEMON:
        return PokemonCard.from_dict(card_data)
    elif card_type == CardType.TRAINER:
        return TrainerCard(
            card_id=card_data['card_id'],
            name=card_data['name'],
            trainer_type=TrainerType(card_data['trainer_type']),
            rarity=Rarity(card_data['rarity']),
            description=card_data.get('description', ''),
            effects=card_data.get('effects', []),
            image_url=card_data.get('image_url', '')
        )
    elif card_type == CardType.ENERGY:
        return EnergyCard(
            card_id=card_data['card_id'],
            name=card_data['name'],
            energy_type=PokemonType(card_data['energy_type']),
            rarity=Rarity(card_data['rarity']),
            is_basic=card_data.get('is_basic', True),
            special_effects=card_data.get('special_effects', []),
            image_url=card_data.get('image_url', '')
        )
    else:
        raise ValueError(f"Unknown card type: {card_type}")

# 预定义的类型弱点关系
TYPE_EFFECTIVENESS = {
    PokemonType.FIRE: [PokemonType.GRASS, PokemonType.METAL],
    PokemonType.WATER: [PokemonType.FIRE],
    PokemonType.GRASS: [PokemonType.WATER, PokemonType.FIGHTING],
    PokemonType.ELECTRIC: [PokemonType.WATER],
    PokemonType.PSYCHIC: [PokemonType.FIGHTING, PokemonType.POISON],
    PokemonType.FIGHTING: [PokemonType.DARKNESS, PokemonType.METAL],
    PokemonType.DARKNESS: [PokemonType.PSYCHIC],
    PokemonType.METAL: [PokemonType.FAIRY],
    PokemonType.FAIRY: [PokemonType.DARKNESS, PokemonType.DRAGON],
    PokemonType.DRAGON: [PokemonType.DRAGON]
}

def get_type_effectiveness(attacking_type: PokemonType, defending_type: PokemonType) -> float:
    """
    获取属性相克倍率
    
    Args:
        attacking_type: 攻击方属性
        defending_type: 防御方属性
        
    Returns:
        伤害倍率
    """
    if defending_type in TYPE_EFFECTIVENESS.get(attacking_type, []):
        return 2.0  # 弱点
    return 1.0  # 正常