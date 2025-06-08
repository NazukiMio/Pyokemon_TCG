"""
战斗规则引擎
定义和验证Pokemon TCG Pocket的游戏规则
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

class RuleViolation(Enum):
    """规则违反类型"""
    INVALID_DECK = "invalid_deck"
    INVALID_ACTION = "invalid_action"
    RESOURCE_INSUFFICIENT = "resource_insufficient"
    TIMING_ERROR = "timing_error"
    GAME_STATE_ERROR = "game_state_error"

@dataclass
class RuleResult:
    """规则检查结果"""
    is_valid: bool
    violation_type: Optional[RuleViolation] = None
    message: str = ""
    suggestions: List[str] = None
    
    def __post_init__(self):
        if self.suggestions is None:
            self.suggestions = []

class BattleRules:
    """战斗规则引擎"""
    
    # 游戏常量
    MIN_DECK_SIZE = 20
    MAX_DECK_SIZE = 60
    INITIAL_HAND_SIZE = 5
    MAX_HAND_SIZE = 7
    MAX_BENCH_SIZE = 3
    PRIZE_CARDS_COUNT = 3
    MAX_TURNS = 50
    ENERGY_PER_TURN = 1
    MAX_CARD_COPIES = 4
    
    @classmethod
    def validate_deck_composition(cls, deck_cards: List[Any]) -> RuleResult:
        """
        验证卡组构成
        
        Args:
            deck_cards: 卡组卡牌列表
        
        Returns:
            验证结果
        """
        # 基础数量检查
        if len(deck_cards) < cls.MIN_DECK_SIZE:
            return RuleResult(
                is_valid=False,
                violation_type=RuleViolation.INVALID_DECK,
                message=f"卡组至少需要{cls.MIN_DECK_SIZE}张卡牌，当前只有{len(deck_cards)}张",
                suggestions=["添加更多卡牌到卡组中"]
            )
        
        if len(deck_cards) > cls.MAX_DECK_SIZE:
            return RuleResult(
                is_valid=False,
                violation_type=RuleViolation.INVALID_DECK,
                message=f"卡组最多{cls.MAX_DECK_SIZE}张卡牌，当前有{len(deck_cards)}张",
                suggestions=["移除多余的卡牌"]
            )
        
        # 统计卡牌数量
        card_counts = {}
        pokemon_count = 0
        
        for card in deck_cards:
            card_id = card.id if hasattr(card, 'id') else str(card)
            card_counts[card_id] = card_counts.get(card_id, 0) + 1
            
            # 统计Pokemon数量
            if hasattr(card, 'hp') and card.hp is not None:
                pokemon_count += 1
        
        # 检查单卡数量限制
        for card_id, count in card_counts.items():
            if count > cls.MAX_CARD_COPIES:
                return RuleResult(
                    is_valid=False,
                    violation_type=RuleViolation.INVALID_DECK,
                    message=f"卡牌{card_id}超过数量限制({count}/{cls.MAX_CARD_COPIES})",
                    suggestions=["减少重复卡牌的数量"]
                )
        
        # 检查Pokemon数量
        min_pokemon = max(5, len(deck_cards) // 4)  # 至少1/4是Pokemon
        if pokemon_count < min_pokemon:
            return RuleResult(
                is_valid=False,
                violation_type=RuleViolation.INVALID_DECK,
                message=f"卡组至少需要{min_pokemon}只Pokemon，当前只有{pokemon_count}只",
                suggestions=["添加更多Pokemon到卡组中"]
            )
        
        return RuleResult(is_valid=True, message="卡组构成有效")
    
    @classmethod
    def validate_initial_setup(cls, player_state) -> RuleResult:
        """
        验证初始设置
        
        Args:
            player_state: 玩家状态
        
        Returns:
            验证结果
        """
        # 检查起始手牌
        if len(player_state.hand) != cls.INITIAL_HAND_SIZE:
            return RuleResult(
                is_valid=False,
                violation_type=RuleViolation.GAME_STATE_ERROR,
                message=f"起始手牌应为{cls.INITIAL_HAND_SIZE}张，当前{len(player_state.hand)}张"
            )
        
        # 检查是否有Pokemon
        hand_pokemon = player_state.get_hand_pokemon()
        if not hand_pokemon:
            return RuleResult(
                is_valid=False,
                violation_type=RuleViolation.GAME_STATE_ERROR,
                message="起始手牌必须至少有1只Pokemon",
                suggestions=["执行Mulligan重新抽牌"]
            )
        
        # 检查奖励卡
        if len(player_state.prize_cards) != cls.PRIZE_CARDS_COUNT:
            return RuleResult(
                is_valid=False,
                violation_type=RuleViolation.GAME_STATE_ERROR,
                message=f"奖励卡应为{cls.PRIZE_CARDS_COUNT}张，当前{len(player_state.prize_cards)}张"
            )
        
        return RuleResult(is_valid=True, message="初始设置有效")
    
    @classmethod
    def validate_pokemon_placement(cls, player_state, pokemon_card) -> RuleResult:
        """
        验证Pokemon放置
        
        Args:
            player_state: 玩家状态
            pokemon_card: Pokemon卡牌
        
        Returns:
            验证结果
        """
        # 检查是否是Pokemon
        if not hasattr(pokemon_card, 'hp') or pokemon_card.hp is None:
            return RuleResult(
                is_valid=False,
                violation_type=RuleViolation.INVALID_ACTION,
                message="只能放置Pokemon卡牌"
            )
        
        # 检查卡牌是否在手牌中
        if pokemon_card not in player_state.hand:
            return RuleResult(
                is_valid=False,
                violation_type=RuleViolation.INVALID_ACTION,
                message="卡牌不在手牌中"
            )
        
        # 检查后备区空位
        if len(player_state.bench_pokemon) >= cls.MAX_BENCH_SIZE:
            return RuleResult(
                is_valid=False,
                violation_type=RuleViolation.GAME_STATE_ERROR,
                message=f"后备区已满({cls.MAX_BENCH_SIZE}只Pokemon)",
                suggestions=["先让一些Pokemon离场或进化"]
            )
        
        return RuleResult(is_valid=True, message="可以放置Pokemon")
    
    @classmethod
    def validate_attack(cls, attacker, defender, attack_index, player_energy) -> RuleResult:
        """
        验证攻击行动
        
        Args:
            attacker: 攻击方Pokemon
            defender: 防守方Pokemon
            attack_index: 攻击技能索引
            player_energy: 玩家可用能量
        
        Returns:
            验证结果
        """
        # 检查攻击方状态
        if not attacker or attacker.is_knocked_out():
            return RuleResult(
                is_valid=False,
                violation_type=RuleViolation.INVALID_ACTION,
                message="攻击方Pokemon不存在或已被击倒"
            )
        
        if not attacker.can_attack():
            reasons = []
            if attacker.is_asleep:
                reasons.append("Pokemon正在睡眠")
            if attacker.is_paralyzed:
                reasons.append("Pokemon被麻痹")
            if not attacker.can_attack_this_turn:
                reasons.append("本回合已经攻击过")
            
            return RuleResult(
                is_valid=False,
                violation_type=RuleViolation.INVALID_ACTION,
                message=f"Pokemon无法攻击: {', '.join(reasons)}"
            )
        
        # 检查攻击技能
        if attack_index >= len(attacker.attacks):
            return RuleResult(
                is_valid=False,
                violation_type=RuleViolation.INVALID_ACTION,
                message="攻击技能不存在"
            )
        
        attack = attacker.attacks[attack_index]
        
        # 检查能量需求
        energy_cost = len(attack.cost) if attack.cost else 1
        if player_energy < energy_cost:
            return RuleResult(
                is_valid=False,
                violation_type=RuleViolation.RESOURCE_INSUFFICIENT,
                message=f"能量不足，需要{energy_cost}点，当前{player_energy}点",
                suggestions=["等待下回合获得更多能量"]
            )
        
        # 检查目标
        if not defender or defender.is_knocked_out():
            return RuleResult(
                is_valid=False,
                violation_type=RuleViolation.INVALID_ACTION,
                message="目标Pokemon不存在或已被击倒"
            )
        
        return RuleResult(is_valid=True, message="可以执行攻击")
    
    @classmethod
    def validate_retreat(cls, player_state, retreating_pokemon, replacement_pokemon, energy_cost=1) -> RuleResult:
        """
        验证撤退行动
        
        Args:
            player_state: 玩家状态
            retreating_pokemon: 撤退的Pokemon
            replacement_pokemon: 替换的Pokemon
            energy_cost: 撤退消耗的能量
        
        Returns:
            验证结果
        """
        # 检查撤退的Pokemon
        if retreating_pokemon != player_state.active_pokemon:
            return RuleResult(
                is_valid=False,
                violation_type=RuleViolation.INVALID_ACTION,
                message="只能撤退前排Pokemon"
            )
        
        if not retreating_pokemon.can_retreat():
            reasons = []
            if retreating_pokemon.is_asleep:
                reasons.append("Pokemon正在睡眠")
            if retreating_pokemon.is_paralyzed:
                reasons.append("Pokemon被麻痹")
            
            return RuleResult(
                is_valid=False,
                violation_type=RuleViolation.INVALID_ACTION,
                message=f"Pokemon无法撤退: {', '.join(reasons)}"
            )
        
        # 检查替换Pokemon
        if replacement_pokemon not in player_state.bench_pokemon:
            return RuleResult(
                is_valid=False,
                violation_type=RuleViolation.INVALID_ACTION,
                message="替换Pokemon必须在后备区"
            )
        
        if replacement_pokemon.is_knocked_out():
            return RuleResult(
                is_valid=False,
                violation_type=RuleViolation.INVALID_ACTION,
                message="替换Pokemon已被击倒"
            )
        
        # 检查能量
        if player_state.energy_points < energy_cost:
            return RuleResult(
                is_valid=False,
                violation_type=RuleViolation.RESOURCE_INSUFFICIENT,
                message=f"能量不足，撤退需要{energy_cost}点",
                suggestions=["等待获得更多能量"]
            )
        
        return RuleResult(is_valid=True, message="可以执行撤退")
    
    @classmethod
    def validate_turn_action(cls, battle_state, player_state, action_type: str) -> RuleResult:
        """
        验证回合行动
        
        Args:
            battle_state: 战斗状态
            player_state: 玩家状态
            action_type: 行动类型
        
        Returns:
            验证结果
        """
        from game.core.battle.battle_state import BattlePhase
        
        # 检查回合
        if not battle_state.is_player_turn(player_state.player_id):
            return RuleResult(
                is_valid=False,
                violation_type=RuleViolation.TIMING_ERROR,
                message="不是你的回合"
            )
        
        # 检查战斗状态
        if battle_state.is_battle_over():
            return RuleResult(
                is_valid=False,
                violation_type=RuleViolation.GAME_STATE_ERROR,
                message="战斗已结束"
            )
        
        # 检查阶段限制
        phase_actions = {
            BattlePhase.DRAW: ["draw_card"],
            BattlePhase.ENERGY: ["gain_energy"],
            BattlePhase.ACTION: [
                "play_pokemon", "evolve_pokemon", "attack", 
                "retreat", "use_trainer", "end_turn"
            ],
            BattlePhase.END_TURN: ["end_turn"]
        }
        
        allowed_actions = phase_actions.get(battle_state.current_phase, [])
        if action_type not in allowed_actions:
            return RuleResult(
                is_valid=False,
                violation_type=RuleViolation.TIMING_ERROR,
                message=f"当前阶段({battle_state.current_phase.value})不能执行{action_type}",
                suggestions=[f"当前可执行: {', '.join(allowed_actions)}"]
            )
        
        return RuleResult(is_valid=True, message="行动时机正确")
    
    @classmethod
    def check_win_condition(cls, player_state) -> Tuple[bool, str]:
        """
        检查获胜条件
        
        Args:
            player_state: 玩家状态
        
        Returns:
            (是否获胜, 获胜原因)
        """
        # 奖励卡获胜
        if player_state.prize_cards_taken >= cls.PRIZE_CARDS_COUNT:
            return True, f"获得{cls.PRIZE_CARDS_COUNT}张奖励卡"
        
        return False, ""
    
    @classmethod
    def check_lose_condition(cls, player_state) -> Tuple[bool, str]:
        """
        检查失败条件
        
        Args:
            player_state: 玩家状态
        
        Returns:
            (是否失败, 失败原因)
        """
        # 无Pokemon可战斗
        if not player_state.has_pokemon_in_play():
            hand_pokemon = player_state.get_hand_pokemon()
            if not hand_pokemon:
                return True, "没有Pokemon可以战斗"
        
        # 卡组用尽（通常不会发生在Pocket版本中）
        if len(player_state.deck) == 0 and len(player_state.hand) == 0:
            return True, "无卡可抽"
        
        return False, ""
    
    @classmethod
    def get_type_effectiveness(cls, attacker_type: str, defender_type: str) -> float:
        """
        获取类型相性倍率
        
        Args:
            attacker_type: 攻击方类型
            defender_type: 防守方类型
        
        Returns:
            相性倍率 (0.5, 1.0, 2.0)
        """
        # Pokemon TCG 类型相性表
        effectiveness_chart = {
            'Fire': {
                'Grass': 2.0,
                'Water': 0.5,
                'Fire': 0.5
            },
            'Water': {
                'Fire': 2.0,
                'Lightning': 0.5,
                'Water': 0.5
            },
            'Grass': {
                'Water': 2.0,
                'Fire': 0.5,
                'Grass': 0.5
            },
            'Lightning': {
                'Water': 2.0,
                'Fighting': 0.5,
                'Lightning': 0.5
            },
            'Fighting': {
                'Lightning': 2.0,
                'Psychic': 0.5,
                'Fighting': 0.5
            },
            'Psychic': {
                'Fighting': 2.0,
                'Psychic': 0.5
            },
            'Darkness': {
                'Psychic': 2.0,
                'Fighting': 0.5
            },
            'Metal': {
                'Fairy': 2.0,
                'Fire': 0.5,
                'Lightning': 0.5,
                'Psychic': 0.5
            },
            'Fairy': {
                'Darkness': 2.0,
                'Metal': 0.5,
                'Fire': 0.5
            },
            'Dragon': {
                'Dragon': 2.0
            }
        }
        
        return effectiveness_chart.get(attacker_type, {}).get(defender_type, 1.0)
    
    @classmethod
    def calculate_damage(cls, base_damage: int, attacker_type: str, defender_type: str, 
                        modifiers: Dict[str, float] = None) -> int:
        """
        计算实际伤害
        
        Args:
            base_damage: 基础伤害
            attacker_type: 攻击方类型
            defender_type: 防守方类型
            modifiers: 伤害修正器
        
        Returns:
            实际伤害
        """
        if base_damage <= 0:
            return 0
        
        # 类型相性
        effectiveness = cls.get_type_effectiveness(attacker_type, defender_type)
        damage = int(base_damage * effectiveness)
        
        # 应用修正器
        if modifiers:
            for modifier_name, modifier_value in modifiers.items():
                damage = int(damage * modifier_value)
        
        # 确保至少造成1点伤害（如果基础伤害>0）
        return max(1, damage) if base_damage > 0 else 0
    
    @classmethod
    def get_status_effect_rules(cls) -> Dict[str, Dict[str, Any]]:
        """
        获取状态效果规则
        
        Returns:
            状态效果规则字典
        """
        return {
            'poison': {
                'damage_per_turn': 10,
                'can_retreat': True,
                'can_attack': True,
                'duration': -1  # 永久直到治愈
            },
            'burn': {
                'damage_per_turn': 20,
                'can_retreat': True,
                'can_attack': True,
                'duration': -1
            },
            'sleep': {
                'can_retreat': False,
                'can_attack': False,
                'wake_up_chance': 0.5,  # 每回合50%概率醒来
                'duration': -1
            },
            'paralysis': {
                'can_retreat': False,
                'can_attack': False,
                'duration': 1  # 下回合自动恢复
            },
            'confusion': {
                'can_retreat': True,
                'can_attack': True,
                'self_damage_chance': 0.5,  # 50%概率自残
                'self_damage': 30,
                'duration': 3
            }
        }
    
    @classmethod
    def validate_game_rules(cls, battle_state, player_states: Dict[int, Any]) -> List[RuleResult]:
        """
        验证整体游戏规则
        
        Args:
            battle_state: 战斗状态
            player_states: 玩家状态字典
        
        Returns:
            验证结果列表
        """
        violations = []
        
        # 检查回合限制
        if battle_state.turn_count > cls.MAX_TURNS:
            violations.append(RuleResult(
                is_valid=False,
                violation_type=RuleViolation.GAME_STATE_ERROR,
                message=f"超过最大回合数限制({cls.MAX_TURNS})"
            ))
        
        # 检查每个玩家状态
        for player_id, player_state in player_states.items():
            # 手牌数量检查
            if len(player_state.hand) > cls.MAX_HAND_SIZE:
                violations.append(RuleResult(
                    is_valid=False,
                    violation_type=RuleViolation.GAME_STATE_ERROR,
                    message=f"玩家{player_id}手牌超过上限({len(player_state.hand)}/{cls.MAX_HAND_SIZE})"
                ))
            
            # 后备区数量检查
            if len(player_state.bench_pokemon) > cls.MAX_BENCH_SIZE:
                violations.append(RuleResult(
                    is_valid=False,
                    violation_type=RuleViolation.GAME_STATE_ERROR,
                    message=f"玩家{player_id}后备区超过上限({len(player_state.bench_pokemon)}/{cls.MAX_BENCH_SIZE})"
                ))
        
        return violations

# 规则便捷函数
def is_valid_deck(deck_cards: List[Any]) -> bool:
    """检查卡组是否有效"""
    return BattleRules.validate_deck_composition(deck_cards).is_valid

def can_place_pokemon(player_state, pokemon_card) -> bool:
    """检查是否可以放置Pokemon"""
    return BattleRules.validate_pokemon_placement(player_state, pokemon_card).is_valid

def can_attack(attacker, defender, attack_index, player_energy) -> bool:
    """检查是否可以攻击"""
    return BattleRules.validate_attack(attacker, defender, attack_index, player_energy).is_valid

def can_retreat(player_state, retreating_pokemon, replacement_pokemon, energy_cost=1) -> bool:
    """检查是否可以撤退"""
    return BattleRules.validate_retreat(
        player_state, retreating_pokemon, replacement_pokemon, energy_cost
    ).is_valid

def get_damage_multiplier(attacker_type: str, defender_type: str) -> float:
    """获取伤害倍率"""
    return BattleRules.get_type_effectiveness(attacker_type, defender_type)