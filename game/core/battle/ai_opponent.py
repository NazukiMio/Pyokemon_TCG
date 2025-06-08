"""
AI对手系统
实现不同难度的AI对手逻辑
"""

import random
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from game.core.battle.battle_actions import ActionType, ActionRequest, create_action_request
from game.core.cards.card_data import Card

class AIDifficulty(Enum):
    """AI难度枚举"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

@dataclass
class AIPersonality:
    """AI个性配置"""
    name: str
    difficulty: AIDifficulty
    aggression: float      # 攻击倾向 (0.0-1.0)
    risk_tolerance: float  # 风险承受度 (0.0-1.0)
    strategy_focus: str    # 策略重点 ("offensive", "defensive", "balanced")
    thinking_time: float   # 思考时间（秒）
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'difficulty': self.difficulty.value,
            'aggression': self.aggression,
            'risk_tolerance': self.risk_tolerance,
            'strategy_focus': self.strategy_focus,
            'thinking_time': self.thinking_time
        }

class AIDecisionMaker:
    """AI决策制定器"""
    
    def __init__(self, personality: AIPersonality):
        """
        初始化AI决策器
        
        Args:
            personality: AI个性配置
        """
        self.personality = personality
        self.decision_history: List[Dict[str, Any]] = []
        self.turn_count = 0
        
        print(f"🤖 AI对手初始化: {personality.name} ({personality.difficulty.value})")
        print(f"   特征: 攻击性 {personality.aggression:.1f}, 风险承受 {personality.risk_tolerance:.1f}")
    
    def make_decision(self, battle_state, ai_player_state, opponent_player_state) -> Optional[ActionRequest]:
        """
        制定AI决策
        
        Args:
            battle_state: 战斗状态
            ai_player_state: AI玩家状态
            opponent_player_state: 对手玩家状态
        
        Returns:
            AI行动请求
        """
        from game.core.battle.battle_state import BattlePhase
        
        # 模拟思考时间
        if self.personality.thinking_time > 0:
            time.sleep(min(self.personality.thinking_time, 2.0))  # 最多2秒
        
        # 根据当前阶段决定行动
        if battle_state.current_phase == BattlePhase.DRAW:
            return self._decide_draw_phase(battle_state, ai_player_state)
        elif battle_state.current_phase == BattlePhase.ENERGY:
            return self._decide_energy_phase(battle_state, ai_player_state)
        elif battle_state.current_phase == BattlePhase.ACTION:
            return self._decide_action_phase(battle_state, ai_player_state, opponent_player_state)
        
        return None
    
    def _decide_draw_phase(self, battle_state, ai_player_state) -> ActionRequest:
        """决定抽卡阶段的行动"""
        return create_action_request(
            action_type="draw_card",
            player_id=ai_player_state.player_id,
            parameters={'count': 1}
        )
    
    def _decide_energy_phase(self, battle_state, ai_player_state) -> ActionRequest:
        """决定能量阶段的行动"""
        return create_action_request(
            action_type="gain_energy",
            player_id=ai_player_state.player_id,
            parameters={'amount': ai_player_state.max_energy_per_turn}
        )
    
    def _decide_action_phase(self, battle_state, ai_player_state, opponent_player_state) -> ActionRequest:
        """决定行动阶段的行动"""
        # 评估当前局面
        situation = self._evaluate_situation(ai_player_state, opponent_player_state)
        
        # 根据难度和局面选择策略
        if self.personality.difficulty == AIDifficulty.EASY:
            return self._easy_strategy(battle_state, ai_player_state, opponent_player_state, situation)
        elif self.personality.difficulty == AIDifficulty.MEDIUM:
            return self._medium_strategy(battle_state, ai_player_state, opponent_player_state, situation)
        else:  # HARD
            return self._hard_strategy(battle_state, ai_player_state, opponent_player_state, situation)
    
    def _evaluate_situation(self, ai_player_state, opponent_player_state) -> Dict[str, Any]:
        """评估当前战斗局面"""
        situation = {
            'ai_advantages': 0,
            'opponent_advantages': 0,
            'urgency': 0.0,
            'should_attack': False,
            'should_defend': False,
            'should_setup': False
        }
        
        # HP优势评估
        ai_total_hp = sum(p.current_hp for p in ai_player_state.field_pokemon)
        opponent_total_hp = sum(p.current_hp for p in opponent_player_state.field_pokemon)
        
        if ai_total_hp > opponent_total_hp:
            situation['ai_advantages'] += 1
        elif opponent_total_hp > ai_total_hp:
            situation['opponent_advantages'] += 1
        
        # 场上Pokemon数量
        ai_pokemon_count = len(ai_player_state.field_pokemon)
        opponent_pokemon_count = len(opponent_player_state.field_pokemon)
        
        if ai_pokemon_count > opponent_pokemon_count:
            situation['ai_advantages'] += 1
        elif opponent_pokemon_count > ai_pokemon_count:
            situation['opponent_advantages'] += 1
        
        # 奖励卡进度
        ai_prizes = ai_player_state.prize_cards_taken
        opponent_prizes = opponent_player_state.prize_cards_taken
        
        if ai_prizes > opponent_prizes:
            situation['ai_advantages'] += 2
        elif opponent_prizes > ai_prizes:
            situation['opponent_advantages'] += 2
        
        # 紧急程度评估
        if opponent_prizes >= 2:  # 对手接近获胜
            situation['urgency'] = 0.8
        elif ai_pokemon_count <= 1:  # AI Pokemon很少
            situation['urgency'] = 0.6
        elif ai_player_state.active_pokemon and ai_player_state.active_pokemon.current_hp <= 20:
            situation['urgency'] = 0.4
        
        # 策略建议
        if situation['ai_advantages'] > situation['opponent_advantages']:
            situation['should_attack'] = True
        elif situation['opponent_advantages'] > situation['ai_advantages']:
            situation['should_defend'] = True
        else:
            situation['should_setup'] = True
        
        return situation
    
    def _easy_strategy(self, battle_state, ai_player_state, opponent_player_state, situation) -> ActionRequest:
        """简单AI策略：随机但基本合理的行动"""
        available_actions = []
        
        # 检查可以放置Pokemon
        hand_pokemon = ai_player_state.get_hand_pokemon()
        if hand_pokemon and ai_player_state.can_play_pokemon():
            available_actions.append(('play_pokemon', random.choice(hand_pokemon)))
        
        # 检查可以攻击
        if ai_player_state.can_attack() and opponent_player_state.active_pokemon:
            available_actions.append(('attack', None))
        
        # 总是可以结束回合
        available_actions.append(('end_turn', None))
        
        # 随机选择行动
        if available_actions:
            action_type, target = random.choice(available_actions)
            
            if action_type == 'play_pokemon':
                return create_action_request(
                    action_type="play_pokemon",
                    player_id=ai_player_state.player_id,
                    source_id=target.instance_id
                )
            elif action_type == 'attack':
                # 选择第一个攻击技能
                return create_action_request(
                    action_type="attack",
                    player_id=ai_player_state.player_id,
                    parameters={'attack_index': 0}
                )
            else:  # end_turn
                return create_action_request(
                    action_type="end_turn",
                    player_id=ai_player_state.player_id
                )
        
        # 默认结束回合
        return create_action_request(
            action_type="end_turn",
            player_id=ai_player_state.player_id
        )
    
    def _medium_strategy(self, battle_state, ai_player_state, opponent_player_state, situation) -> ActionRequest:
        """中等AI策略：考虑基本战术的决策"""
        # 优先级决策
        priorities = []
        
        # 1. 如果没有前排Pokemon，必须放置
        if not ai_player_state.active_pokemon:
            hand_pokemon = ai_player_state.get_hand_pokemon()
            if hand_pokemon:
                best_pokemon = max(hand_pokemon, key=lambda p: p.card.hp or 0)
                return create_action_request(
                    action_type="play_pokemon",
                    player_id=ai_player_state.player_id,
                    source_id=best_pokemon.instance_id
                )
        
        # 2. 攻击决策
        if ai_player_state.can_attack() and opponent_player_state.active_pokemon:
            attack_priority = self._calculate_attack_priority(
                ai_player_state, opponent_player_state, situation
            )
            priorities.append(('attack', attack_priority, None))
        
        # 3. 放置Pokemon决策
        hand_pokemon = ai_player_state.get_hand_pokemon()
        if hand_pokemon and ai_player_state.can_play_pokemon():
            pokemon_priority = self._calculate_pokemon_priority(
                hand_pokemon, ai_player_state, situation
            )
            if pokemon_priority > 0:
                best_pokemon = max(hand_pokemon, key=lambda p: self._evaluate_pokemon_value(p.card))
                priorities.append(('play_pokemon', pokemon_priority, best_pokemon))
        
        # 4. 撤退决策
        if (ai_player_state.active_pokemon and 
            ai_player_state.active_pokemon.can_retreat() and 
            len(ai_player_state.bench_pokemon) > 0):
            retreat_priority = self._calculate_retreat_priority(
                ai_player_state, opponent_player_state, situation
            )
            if retreat_priority > 0:
                best_replacement = max(ai_player_state.bench_pokemon, 
                                     key=lambda p: p.current_hp)
                priorities.append(('retreat', retreat_priority, best_replacement))
        
        # 5. 结束回合
        priorities.append(('end_turn', 1.0, None))
        
        # 选择优先级最高的行动
        if priorities:
            priorities.sort(key=lambda x: x[1], reverse=True)
            action_type, _, target = priorities[0]
            
            return self._create_action_from_priority(action_type, target, ai_player_state)
        
        # 默认结束回合
        return create_action_request(
            action_type="end_turn",
            player_id=ai_player_state.player_id
        )
    
    def _hard_strategy(self, battle_state, ai_player_state, opponent_player_state, situation) -> ActionRequest:
        """困难AI策略：深度分析和最优决策"""
        # 使用更复杂的决策树
        decision_tree = self._build_decision_tree(
            battle_state, ai_player_state, opponent_player_state, situation
        )
        
        # 评估每个可能的行动
        best_action = None
        best_score = -float('inf')
        
        for action_type, candidates in decision_tree.items():
            for candidate in candidates:
                score = self._evaluate_action_outcome(
                    action_type, candidate, ai_player_state, opponent_player_state, situation
                )
                
                if score > best_score:
                    best_score = score
                    best_action = (action_type, candidate)
        
        if best_action:
            action_type, target = best_action
            return self._create_action_from_priority(action_type, target, ai_player_state)
        
        # 默认结束回合
        return create_action_request(
            action_type="end_turn",
            player_id=ai_player_state.player_id
        )
    
    def _calculate_attack_priority(self, ai_player_state, opponent_player_state, situation) -> float:
        """计算攻击优先级"""
        if not ai_player_state.active_pokemon or not opponent_player_state.active_pokemon:
            return 0.0
        
        priority = 0.5  # 基础优先级
        
        # 根据伤害潜力调整
        target = opponent_player_state.active_pokemon
        available_attacks = ai_player_state.active_pokemon.get_available_attacks(
            ai_player_state.energy_points
        )
        
        max_damage = 0
        for attack_info in available_attacks:
            if attack_info['can_use']:
                damage = ai_player_state.active_pokemon._parse_damage(attack_info['damage'])
                max_damage = max(max_damage, damage)
        
        # 如果能击倒对手，大幅提高优先级
        if max_damage >= target.current_hp:
            priority += 1.5
        elif max_damage >= target.current_hp * 0.7:  # 能造成重大伤害
            priority += 0.8
        
        # 根据AI个性调整
        priority += self.personality.aggression * 0.5
        
        # 根据局面紧急程度调整
        priority += situation['urgency'] * 0.3
        
        return min(priority, 2.0)
    
    def _calculate_pokemon_priority(self, hand_pokemon, ai_player_state, situation) -> float:
        """计算放置Pokemon的优先级"""
        if not hand_pokemon:
            return 0.0
        
        priority = 0.3  # 基础优先级
        
        # 如果场上Pokemon很少，提高优先级
        if len(ai_player_state.field_pokemon) <= 1:
            priority += 0.8
        elif len(ai_player_state.field_pokemon) <= 2:
            priority += 0.4
        
        # 如果有强力Pokemon，提高优先级
        best_pokemon = max(hand_pokemon, key=lambda p: self._evaluate_pokemon_value(p.card))
        if self._evaluate_pokemon_value(best_pokemon.card) > 100:
            priority += 0.3
        
        return priority
    
    def _calculate_retreat_priority(self, ai_player_state, opponent_player_state, situation) -> float:
        """计算撤退优先级"""
        if not ai_player_state.active_pokemon:
            return 0.0
        
        priority = 0.0
        active = ai_player_state.active_pokemon
        
        # 如果前排Pokemon HP很低，考虑撤退
        hp_percentage = active.current_hp / active.max_hp
        if hp_percentage < 0.3:
            priority += 0.7
        elif hp_percentage < 0.5:
            priority += 0.3
        
        # 如果后备区有更强的Pokemon，考虑撤退
        if ai_player_state.bench_pokemon:
            best_bench = max(ai_player_state.bench_pokemon, 
                           key=lambda p: self._evaluate_pokemon_battle_value(p))
            active_value = self._evaluate_pokemon_battle_value(active)
            bench_value = self._evaluate_pokemon_battle_value(best_bench)
            
            if bench_value > active_value * 1.2:
                priority += 0.4
        
        # 根据风险承受度调整
        priority *= self.personality.risk_tolerance
        
        return priority
    
    def _build_decision_tree(self, battle_state, ai_player_state, opponent_player_state, situation) -> Dict[str, List]:
        """构建决策树"""
        tree = {
            'attack': [],
            'play_pokemon': [],
            'retreat': [],
            'end_turn': [None]
        }
        
        # 攻击选项
        if ai_player_state.can_attack() and opponent_player_state.active_pokemon:
            available_attacks = ai_player_state.active_pokemon.get_available_attacks(
                ai_player_state.energy_points
            )
            for i, attack_info in enumerate(available_attacks):
                if attack_info['can_use']:
                    tree['attack'].append(i)
        
        # 放置Pokemon选项
        hand_pokemon = ai_player_state.get_hand_pokemon()
        if hand_pokemon and ai_player_state.can_play_pokemon():
            tree['play_pokemon'] = hand_pokemon
        
        # 撤退选项
        if (ai_player_state.active_pokemon and 
            ai_player_state.active_pokemon.can_retreat() and 
            len(ai_player_state.bench_pokemon) > 0):
            tree['retreat'] = ai_player_state.bench_pokemon
        
        return tree
    
    def _evaluate_action_outcome(self, action_type, target, ai_player_state, opponent_player_state, situation) -> float:
        """评估行动结果的分数"""
        score = 0.0
        
        if action_type == 'attack':
            # 评估攻击效果
            if isinstance(target, int):  # 攻击技能索引
                attack = ai_player_state.active_pokemon.attacks[target]
                damage = ai_player_state.active_pokemon._parse_damage(attack.damage)
                
                # 基础伤害分数
                score += damage * 0.1
                
                # 击倒奖励
                if damage >= opponent_player_state.active_pokemon.current_hp:
                    score += 50  # 高分奖励
                
        elif action_type == 'play_pokemon':
            # 评估Pokemon价值
            pokemon_value = self._evaluate_pokemon_value(target.card)
            score += pokemon_value * 0.01
            
        elif action_type == 'retreat':
            # 评估撤退效果
            if ai_player_state.active_pokemon:
                current_value = self._evaluate_pokemon_battle_value(ai_player_state.active_pokemon)
                new_value = self._evaluate_pokemon_battle_value(target)
                score += (new_value - current_value) * 0.1
        
        elif action_type == 'end_turn':
            # 结束回合的基础分数
            score = 10.0
        
        return score
    
    def _evaluate_pokemon_value(self, card: Card) -> float:
        """评估Pokemon卡牌的价值"""
        value = 0.0
        
        # HP价值
        if card.hp:
            value += card.hp * 0.5
        
        # 攻击力价值
        for attack in card.attacks:
            damage = self._parse_damage_for_evaluation(attack.damage)
            value += damage * 0.8
        
        # 稀有度价值
        rarity_values = {
            'Common': 10,
            'Uncommon': 20,
            'Rare': 40,
            'Ultra Rare': 80
        }
        value += rarity_values.get(card.rarity, 10)
        
        return value
    
    def _evaluate_pokemon_battle_value(self, pokemon_instance) -> float:
        """评估Pokemon实例的战斗价值"""
        if not pokemon_instance:
            return 0.0
        
        value = 0.0
        
        # 当前HP价值
        value += pokemon_instance.current_hp * 0.6
        
        # 攻击潜力
        for attack in pokemon_instance.attacks:
            damage = self._parse_damage_for_evaluation(attack.damage)
            value += damage * 0.9
        
        # 状态效果影响
        if pokemon_instance.status_effects:
            value *= 0.7  # 有负面状态效果时降低价值
        
        return value
    
    def _parse_damage_for_evaluation(self, damage_string: str) -> float:
        """为评估解析伤害值"""
        if not damage_string:
            return 0.0
        
        import re
        numbers = re.findall(r'\d+', damage_string)
        return float(numbers[0]) if numbers else 0.0
    
    def _create_action_from_priority(self, action_type: str, target: Any, ai_player_state) -> ActionRequest:
        """根据优先级结果创建行动请求"""
        if action_type == 'attack':
            attack_index = target if isinstance(target, int) else 0
            return create_action_request(
                action_type="attack",
                player_id=ai_player_state.player_id,
                parameters={'attack_index': attack_index}
            )
        elif action_type == 'play_pokemon':
            return create_action_request(
                action_type="play_pokemon",
                player_id=ai_player_state.player_id,
                source_id=target.instance_id
            )
        elif action_type == 'retreat':
            return create_action_request(
                action_type="retreat",
                player_id=ai_player_state.player_id,
                target_id=target.instance_id,
                parameters={'energy_cost': 1}
            )
        else:  # end_turn
            return create_action_request(
                action_type="end_turn",
                player_id=ai_player_state.player_id
            )
    
    def record_decision(self, action_request: ActionRequest, action_response):
        """记录决策历史"""
        decision_record = {
            'turn': self.turn_count,
            'action': action_request.to_dict(),
            'result': action_response.to_dict() if action_response else None,
            'timestamp': time.time()
        }
        
        self.decision_history.append(decision_record)
        
        # 限制历史记录数量
        if len(self.decision_history) > 100:
            self.decision_history.pop(0)
    
    def get_ai_status(self) -> Dict[str, Any]:
        """获取AI状态信息"""
        return {
            'personality': self.personality.to_dict(),
            'turn_count': self.turn_count,
            'decision_count': len(self.decision_history),
            'last_decision': self.decision_history[-1] if self.decision_history else None
        }

# 预定义的AI对手配置
AI_OPPONENTS = {
    'rookie_trainer': AIPersonality(
        name="Entrenador Novato",
        difficulty=AIDifficulty.EASY,
        aggression=0.3,
        risk_tolerance=0.8,
        strategy_focus="balanced",
        thinking_time=0.5
    ),
    
    'gym_leader': AIPersonality(
        name="Líder de Gimnasio",
        difficulty=AIDifficulty.MEDIUM,
        aggression=0.6,
        risk_tolerance=0.5,
        strategy_focus="offensive",
        thinking_time=1.0
    ),
    
    'elite_four': AIPersonality(
        name="Alto Mando",
        difficulty=AIDifficulty.HARD,
        aggression=0.8,
        risk_tolerance=0.3,
        strategy_focus="offensive",
        thinking_time=1.5
    ),
    
    'champion': AIPersonality(
        name="Campeón",
        difficulty=AIDifficulty.HARD,
        aggression=0.7,
        risk_tolerance=0.2,
        strategy_focus="balanced",
        thinking_time=2.0
    )
}

def get_ai_opponent(opponent_id: str) -> Optional[AIPersonality]:
    """获取AI对手配置"""
    return AI_OPPONENTS.get(opponent_id)

def get_random_ai_opponent(difficulty: AIDifficulty = None) -> AIPersonality:
    """获取随机AI对手"""
    if difficulty:
        opponents = [ai for ai in AI_OPPONENTS.values() if ai.difficulty == difficulty]
        return random.choice(opponents) if opponents else list(AI_OPPONENTS.values())[0]
    else:
        return random.choice(list(AI_OPPONENTS.values()))