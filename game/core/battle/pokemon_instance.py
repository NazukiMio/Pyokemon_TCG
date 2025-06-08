"""
Pokemon实例管理
管理场上Pokemon的状态和行为
"""

import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from game.core.cards.card_data import Card, Attack

@dataclass
class StatusEffect:
    """状态效果数据类"""
    effect_type: str      # 效果类型 (poison, burn, sleep, paralysis, confusion)
    duration: int         # 持续回合数 (-1表示永久)
    power: int = 0        # 效果强度
    applied_turn: int = 0 # 施加的回合
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'effect_type': self.effect_type,
            'duration': self.duration,
            'power': self.power,
            'applied_turn': self.applied_turn
        }

@dataclass
class DamageRecord:
    """伤害记录"""
    damage: int
    source_pokemon: str
    attack_name: str
    timestamp: float
    is_critical: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'damage': self.damage,
            'source_pokemon': self.source_pokemon,
            'attack_name': self.attack_name,
            'timestamp': self.timestamp,
            'is_critical': self.is_critical
        }

class PokemonInstance:
    """Pokemon实例类"""
    
    def __init__(self, card: Card, instance_id: str):
        """
        初始化Pokemon实例
        
        Args:
            card: Pokemon卡牌数据
            instance_id: 实例唯一ID
        """
        self.card = card
        self.instance_id = instance_id
        
        # 基础属性
        self.max_hp = card.hp or 50
        self.current_hp = self.max_hp
        self.types = card.types.copy() if card.types else []
        
        # 位置和所有者
        self.position = "bench"  # "active", "bench", "knockout"
        self.owner_id: Optional[int] = None
        
        # 能量和攻击
        self.attached_energy = 0  # 附加的能量数量
        self.attacks = card.attacks.copy() if card.attacks else []
        self.can_attack_this_turn = True
        
        # 状态效果
        self.status_effects: List[StatusEffect] = []
        self.is_evolved = False
        self.evolution_stage = 0
        self.previous_evolution = None
        
        # 战斗记录
        self.damage_taken_history: List[DamageRecord] = []
        self.damage_dealt_history: List[DamageRecord] = []
        self.times_attacked = 0
        self.times_been_attacked = 0
        
        # 特殊状态
        self.is_asleep = False
        self.is_paralyzed = False
        self.is_confused = False
        self.is_poisoned = False
        self.is_burned = False
        
        # 时间戳
        self.created_at = time.time()
        self.last_action_time = time.time()
        
        print(f"🎯 Pokemon实例创建: {card.name} (ID: {instance_id})")
        print(f"   HP: {self.current_hp}/{self.max_hp}")
        print(f"   类型: {', '.join(self.types)}")
    
    def take_damage(self, damage: int, source_pokemon: str = "unknown", attack_name: str = "", is_critical: bool = False) -> bool:
        """
        承受伤害
        
        Args:
            damage: 伤害值
            source_pokemon: 伤害来源Pokemon
            attack_name: 攻击技能名称
            is_critical: 是否暴击
        
        Returns:
            是否被击倒
        """
        if damage <= 0:
            return False
        
        # 记录伤害
        damage_record = DamageRecord(
            damage=damage,
            source_pokemon=source_pokemon,
            attack_name=attack_name,
            timestamp=time.time(),
            is_critical=is_critical
        )
        self.damage_taken_history.append(damage_record)
        
        # 应用伤害
        self.current_hp -= damage
        self.times_been_attacked += 1
        self.last_action_time = time.time()
        
        print(f"💥 {self.card.name} 受到 {damage} 点伤害")
        print(f"   HP: {max(0, self.current_hp)}/{self.max_hp}")
        
        # 检查是否被击倒
        is_knocked_out = self.current_hp <= 0
        if is_knocked_out:
            self.current_hp = 0
            self.position = "knockout"
            print(f"💀 {self.card.name} 被击倒!")
        
        return is_knocked_out
    
    def heal(self, amount: int) -> int:
        """
        治疗
        
        Args:
            amount: 治疗量
        
        Returns:
            实际治疗量
        """
        if self.is_knocked_out():
            return 0
        
        old_hp = self.current_hp
        self.current_hp = min(self.max_hp, self.current_hp + amount)
        actual_heal = self.current_hp - old_hp
        
        if actual_heal > 0:
            print(f"💚 {self.card.name} 恢复 {actual_heal} HP")
            print(f"   HP: {self.current_hp}/{self.max_hp}")
        
        return actual_heal
    
    def add_energy(self, amount: int = 1):
        """增加附加能量"""
        self.attached_energy += amount
        print(f"⚡ {self.card.name} 获得 {amount} 点附加能量 (总计: {self.attached_energy})")
    
    def remove_energy(self, amount: int = 1) -> bool:
        """
        移除附加能量
        
        Args:
            amount: 移除数量
        
        Returns:
            是否成功移除
        """
        if self.attached_energy >= amount:
            self.attached_energy -= amount
            print(f"⚡ {self.card.name} 失去 {amount} 点附加能量 (剩余: {self.attached_energy})")
            return True
        return False
    
    def perform_attack(self, attack_index: int, target: 'PokemonInstance', player_energy: int) -> Dict[str, Any]:
        """
        执行攻击
        
        Args:
            attack_index: 攻击技能索引
            target: 目标Pokemon
            player_energy: 玩家可用能量
        
        Returns:
            攻击结果
        """
        if not self.can_attack():
            return {'success': False, 'reason': 'Pokemon无法攻击'}
        
        if attack_index >= len(self.attacks):
            return {'success': False, 'reason': '攻击技能不存在'}
        
        attack = self.attacks[attack_index]
        
        # 检查能量需求（简化版本）
        energy_cost = self._get_attack_energy_cost(attack)
        if player_energy < energy_cost:
            return {'success': False, 'reason': '能量不足'}
        
        # 解析伤害
        damage = self._parse_damage(attack.damage)
        
        # 计算实际伤害（类型相性等）
        actual_damage = self._calculate_damage(damage, target)
        
        # 执行攻击
        is_knocked_out = target.take_damage(
            actual_damage, 
            self.instance_id, 
            attack.name,
            is_critical=False  # 暴击系统可以后续实现
        )
        
        # 记录攻击
        damage_record = DamageRecord(
            damage=actual_damage,
            source_pokemon=target.instance_id,
            attack_name=attack.name,
            timestamp=time.time()
        )
        self.damage_dealt_history.append(damage_record)
        self.times_attacked += 1
        self.can_attack_this_turn = False
        self.last_action_time = time.time()
        
        # 处理攻击效果
        effects = self._process_attack_effects(attack, target)
        
        print(f"⚔️ {self.card.name} 使用 {attack.name} 攻击 {target.card.name}")
        print(f"   造成 {actual_damage} 点伤害")
        
        return {
            'success': True,
            'attack_name': attack.name,
            'damage_dealt': actual_damage,
            'target_knocked_out': is_knocked_out,
            'energy_cost': energy_cost,
            'effects': effects
        }
    
    def _parse_damage(self, damage_string: str) -> int:
        """解析伤害字符串"""
        if not damage_string:
            return 0
        
        # 移除所有非数字字符，提取数字
        import re
        numbers = re.findall(r'\d+', damage_string)
        return int(numbers[0]) if numbers else 0
    
    def _calculate_damage(self, base_damage: int, target: 'PokemonInstance') -> int:
        """
        计算实际伤害（类型相性、抗性等）
        
        Args:
            base_damage: 基础伤害
            target: 目标Pokemon
        
        Returns:
            实际伤害
        """
        if base_damage <= 0:
            return 0
        
        actual_damage = base_damage
        
        # 类型相性计算（简化版本）
        if self.types and target.types:
            attacker_type = self.types[0]
            defender_type = target.types[0]
            
            # 简化的类型相性表
            effectiveness = self._get_type_effectiveness(attacker_type, defender_type)
            actual_damage = int(actual_damage * effectiveness)
        
        # 确保至少造成1点伤害
        return max(1, actual_damage)
    
    def _get_type_effectiveness(self, attacker_type: str, defender_type: str) -> float:
        """
        获取类型相性倍率
        
        Args:
            attacker_type: 攻击方类型
            defender_type: 防守方类型
        
        Returns:
            相性倍率
        """
        # 简化的类型相性表
        effectiveness_chart = {
            'Fire': {'Grass': 2.0, 'Water': 0.5, 'Fire': 0.5},
            'Water': {'Fire': 2.0, 'Grass': 0.5, 'Water': 0.5},
            'Grass': {'Water': 2.0, 'Fire': 0.5, 'Grass': 0.5},
            'Lightning': {'Water': 2.0, 'Grass': 0.5},
            'Fighting': {'Colorless': 2.0, 'Psychic': 0.5},
            'Psychic': {'Fighting': 2.0, 'Psychic': 0.5},
            'Darkness': {'Psychic': 2.0, 'Fighting': 0.5},
            'Metal': {'Fairy': 2.0, 'Fire': 0.5, 'Lightning': 0.5},
            'Fairy': {'Darkness': 2.0, 'Metal': 0.5},
            'Dragon': {'Dragon': 2.0},
        }
        
        if attacker_type in effectiveness_chart:
            return effectiveness_chart[attacker_type].get(defender_type, 1.0)
        
        return 1.0  # 默认正常效果
    
    def _process_attack_effects(self, attack: Attack, target: 'PokemonInstance') -> List[str]:
        """
        处理攻击的附加效果
        
        Args:
            attack: 攻击技能
            target: 目标Pokemon
        
        Returns:
            效果列表
        """
        effects = []
        
        if not attack.text:
            return effects
        
        text = attack.text.lower()
        
        # 检查状态效果
        if 'poison' in text:
            target.apply_status_effect('poison', 3, 10)
            effects.append('中毒')
        
        if 'burn' in text:
            target.apply_status_effect('burn', 3, 20)
            effects.append('烧伤')
        
        if 'sleep' in text:
            target.apply_status_effect('sleep', 2)
            effects.append('睡眠')
        
        if 'paralyze' in text:
            target.apply_status_effect('paralysis', 2)
            effects.append('麻痹')
        
        if 'confuse' in text:
            target.apply_status_effect('confusion', 3)
            effects.append('混乱')
        
        return effects
    
    def apply_status_effect(self, effect_type: str, duration: int, power: int = 0):
        """
        应用状态效果
        
        Args:
            effect_type: 效果类型
            duration: 持续时间
            power: 效果强度
        """
        # 移除相同类型的旧效果
        self.status_effects = [e for e in self.status_effects if e.effect_type != effect_type]
        
        # 添加新效果
        effect = StatusEffect(
            effect_type=effect_type,
            duration=duration,
            power=power,
            applied_turn=0  # 应该从战斗管理器获取当前回合
        )
        self.status_effects.append(effect)
        
        # 更新状态标志
        if effect_type == 'poison':
            self.is_poisoned = True
        elif effect_type == 'burn':
            self.is_burned = True
        elif effect_type == 'sleep':
            self.is_asleep = True
        elif effect_type == 'paralysis':
            self.is_paralyzed = True
        elif effect_type == 'confusion':
            self.is_confused = True
        
        print(f"🌟 {self.card.name} 受到状态效果: {effect_type}")
    
    def remove_status_effect(self, effect_type: str):
        """移除状态效果"""
        self.status_effects = [e for e in self.status_effects if e.effect_type != effect_type]
        
        # 更新状态标志
        if effect_type == 'poison':
            self.is_poisoned = False
        elif effect_type == 'burn':
            self.is_burned = False
        elif effect_type == 'sleep':
            self.is_asleep = False
        elif effect_type == 'paralysis':
            self.is_paralyzed = False
        elif effect_type == 'confusion':
            self.is_confused = False
        
        print(f"✨ {self.card.name} 移除状态效果: {effect_type}")
    
    def process_status_effects(self) -> List[str]:
        """
        处理状态效果（每回合调用）
        
        Returns:
            处理结果列表
        """
        results = []
        effects_to_remove = []
        
        for effect in self.status_effects:
            if effect.effect_type == 'poison':
                self.take_damage(effect.power, "poison", "中毒")
                results.append(f"{self.card.name} 因中毒受到 {effect.power} 点伤害")
            
            elif effect.effect_type == 'burn':
                self.take_damage(effect.power, "burn", "烧伤")
                results.append(f"{self.card.name} 因烧伤受到 {effect.power} 点伤害")
            
            # 减少持续时间
            if effect.duration > 0:
                effect.duration -= 1
                if effect.duration <= 0:
                    effects_to_remove.append(effect.effect_type)
        
        # 移除过期效果
        for effect_type in effects_to_remove:
            self.remove_status_effect(effect_type)
            results.append(f"{self.card.name} 的 {effect_type} 效果结束")
        
        return results
    
    def can_attack(self) -> bool:
        """检查是否可以攻击"""
        if self.is_knocked_out():
            return False
        
        if not self.can_attack_this_turn:
            return False
        
        if self.is_asleep or self.is_paralyzed:
            return False
        
        if len(self.attacks) == 0:
            return False
        
        return True
    
    def can_retreat(self) -> bool:
        """检查是否可以撤退"""
        if self.is_knocked_out():
            return False
        
        if self.is_asleep or self.is_paralyzed:
            return False
        
        return True
    
    def reset_turn_status(self):
        """重置回合状态"""
        self.can_attack_this_turn = True
        
        # 处理睡眠状态（有机会自然醒来）
        if self.is_asleep:
            import random
            if random.random() < 0.5:  # 50%概率醒来
                self.remove_status_effect('sleep')
    
    def is_knocked_out(self) -> bool:
        """检查是否被击倒"""
        return self.current_hp <= 0 or self.position == "knockout"
    
    def evolve_to(self, evolution_card: Card) -> bool:
        """
        进化到指定Pokemon
        
        Args:
            evolution_card: 进化后的Pokemon卡
        
        Returns:
            是否成功进化
        """
        if self.is_knocked_out():
            return False
        
        # 保存原有状态
        old_hp_percentage = self.current_hp / self.max_hp
        
        # 更新卡牌信息
        self.previous_evolution = self.card
        self.card = evolution_card
        self.is_evolved = True
        self.evolution_stage += 1
        
        # 更新HP（按比例保持）
        self.max_hp = evolution_card.hp or self.max_hp
        self.current_hp = int(self.max_hp * old_hp_percentage)
        
        # 更新攻击技能
        self.attacks = evolution_card.attacks.copy() if evolution_card.attacks else []
        
        # 更新类型
        self.types = evolution_card.types.copy() if evolution_card.types else self.types
        
        print(f"🌟 {self.previous_evolution.name} 进化为 {self.card.name}!")
        print(f"   新HP: {self.current_hp}/{self.max_hp}")
        
        return True
    
    def get_available_attacks(self, player_energy: int) -> List[Dict[str, Any]]:
        """
        获取可用的攻击技能
        
        Args:
            player_energy: 玩家可用能量
        
        Returns:
            可用攻击列表
        """
        available_attacks = []
        
        for i, attack in enumerate(self.attacks):
            energy_cost = self._get_attack_energy_cost(attack)
            can_use = (player_energy >= energy_cost and 
                      self.can_attack())
            
            available_attacks.append({
                'index': i,
                'name': attack.name,
                'damage': attack.damage,
                'text': attack.text,
                'energy_cost': energy_cost,
                'can_use': can_use
            })
        
        return available_attacks
    
    def _get_attack_energy_cost(self, attack) -> int:
        """获取攻击能量消耗（TCG Pocket版本）"""
        if hasattr(attack, 'cost') and attack.cost:
            return len(attack.cost)
        
        # Pocket版本：根据伤害推算能量消耗
        damage = self._parse_damage(attack.damage)
        if damage == 0:
            return 0  # 无伤害技能（如搜索）不消耗能量
        elif damage <= 30:
            return 1
        elif damage <= 60:
            return 2
        else:
            return 3

    def get_status_summary(self) -> Dict[str, Any]:
        """获取状态摘要"""
        return {
            'instance_id': self.instance_id,
            'card_name': self.card.name,
            'position': self.position,
            'hp': {
                'current': self.current_hp,
                'max': self.max_hp,
                'percentage': round((self.current_hp / self.max_hp) * 100, 1) if self.max_hp > 0 else 0
            },
            'energy': {
                'attached': self.attached_energy
            },
            'status_effects': [effect.to_dict() for effect in self.status_effects],
            'conditions': {
                'is_asleep': self.is_asleep,
                'is_paralyzed': self.is_paralyzed,
                'is_confused': self.is_confused,
                'is_poisoned': self.is_poisoned,
                'is_burned': self.is_burned,
                'can_attack': self.can_attack(),
                'can_retreat': self.can_retreat(),
                'is_knocked_out': self.is_knocked_out()
            },
            'evolution': {
                'is_evolved': self.is_evolved,
                'stage': self.evolution_stage,
                'previous': self.previous_evolution.name if self.previous_evolution else None
            },
            'battle_stats': {
                'times_attacked': self.times_attacked,
                'times_been_attacked': self.times_been_attacked,
                'total_damage_dealt': sum(record.damage for record in self.damage_dealt_history),
                'total_damage_taken': sum(record.damage for record in self.damage_taken_history)
            }
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'instance_id': self.instance_id,
            'card': self.card.to_dict(),
            'current_hp': self.current_hp,
            'max_hp': self.max_hp,
            'position': self.position,
            'owner_id': self.owner_id,
            'attached_energy': self.attached_energy,
            'status_effects': [effect.to_dict() for effect in self.status_effects],
            'is_evolved': self.is_evolved,
            'evolution_stage': self.evolution_stage,
            'can_attack_this_turn': self.can_attack_this_turn,
            'created_at': self.created_at,
            'last_action_time': self.last_action_time
        }
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"{self.card.name} ({self.current_hp}/{self.max_hp} HP) [{self.position}]"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return f"PokemonInstance(id={self.instance_id}, name={self.card.name}, hp={self.current_hp}/{self.max_hp})"