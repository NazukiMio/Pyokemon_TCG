"""
Pokemon TCG 对战引擎
简化版的Pokemon TCG对战逻辑实现
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple, Any, Callable
import random
import time
from game.cards.card_types import PokemonCard, TrainerCard, EnergyCard, CardType, PokemonType, StatusCondition
from game.cards.deck_manager import Deck

class GamePhase(Enum):
    """游戏阶段"""
    SETUP = "setup"
    DRAW = "draw"
    MAIN = "main"
    ATTACK = "attack"
    END = "end"

class BattleState(Enum):
    """对战状态"""
    WAITING = "waiting"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"
    PAUSED = "paused"

class Player:
    """玩家类"""
    
    def __init__(self, player_id: int, name: str, deck: Deck):
        """
        初始化玩家
        
        Args:
            player_id: 玩家ID
            name: 玩家名称
            deck: 玩家卡组
        """
        self.player_id = player_id
        self.name = name
        self.deck = deck.clone()  # 克隆卡组避免修改原卡组
        
        # 游戏区域
        self.hand = []  # 手牌
        self.active_pokemon = None  # 战斗场Pokemon
        self.bench = []  # 后备Pokemon（最多5只）
        self.prize_cards = []  # 奖励卡
        self.discard_pile = []  # 弃牌堆
        
        # 游戏状态
        self.has_drawn = False  # 本回合是否已抽牌
        self.has_attacked = False  # 本回合是否已攻击
        self.energy_played_this_turn = False  # 本回合是否已使用能量
        
        # 对战记录
        self.prizes_taken = 0
        self.pokemon_knocked_out = 0
        
    def reset_turn_state(self):
        """重置回合状态"""
        self.has_drawn = False
        self.has_attacked = False
        self.energy_played_this_turn = False
        
        # 清除Pokemon的回合效果
        all_pokemon = [self.active_pokemon] + self.bench
        for pokemon in all_pokemon:
            if pokemon:
                # 清除回合特效
                pokemon.effects = {k: v for k, v in pokemon.effects.items() 
                                 if not k.startswith('turn_')}
    
    def draw_card(self, count: int = 1) -> List[Any]:
        """
        抽牌
        
        Args:
            count: 抽牌数量
            
        Returns:
            抽到的牌
        """
        drawn_cards = []
        for _ in range(count):
            if self.deck.cards:
                card = self.deck.draw_card()
                if card:
                    self.hand.append(card)
                    drawn_cards.append(card)
        return drawn_cards
    
    def can_play_card(self, card: Any) -> bool:
        """
        检查是否可以打出卡片
        
        Args:
            card: 要检查的卡片
            
        Returns:
            是否可以打出
        """
        if card not in self.hand:
            return False
        
        if card.card_type == CardType.POKEMON:
            return self._can_play_pokemon(card)
        elif card.card_type == CardType.ENERGY:
            return self._can_play_energy(card)
        elif card.card_type == CardType.TRAINER:
            return self._can_play_trainer(card)
        
        return False
    
    def _can_play_pokemon(self, pokemon: PokemonCard) -> bool:
        """检查是否可以打出Pokemon"""
        if pokemon.evolution_stage == "basic":
            # 基础Pokemon可以放到战斗场或后备区
            if not self.active_pokemon:
                return True  # 可以放到战斗场
            return len(self.bench) < 5  # 可以放到后备区
        else:
            # 进化Pokemon需要检查进化条件
            return self._can_evolve_pokemon(pokemon)
    
    def _can_evolve_pokemon(self, evolution: PokemonCard) -> bool:
        """检查是否可以进化Pokemon"""
        if not evolution.evolves_from:
            return False
        
        # 检查战斗场Pokemon
        if (self.active_pokemon and 
            self.active_pokemon.name == evolution.evolves_from):
            return True
        
        # 检查后备区Pokemon
        for bench_pokemon in self.bench:
            if bench_pokemon and bench_pokemon.name == evolution.evolves_from:
                return True
        
        return False
    
    def _can_play_energy(self, energy: EnergyCard) -> bool:
        """检查是否可以打出能量"""
        # 每回合只能使用一次能量（基础规则）
        if self.energy_played_this_turn:
            return False
        
        # 需要有Pokemon可以附加能量
        return self.active_pokemon is not None or len(self.bench) > 0
    
    def _can_play_trainer(self, trainer: TrainerCard) -> bool:
        """检查是否可以打出训练师卡"""
        # 简化：大部分训练师卡都可以在主要阶段使用
        return True
    
    def play_pokemon_to_active(self, pokemon: PokemonCard) -> bool:
        """将Pokemon放到战斗场"""
        if pokemon in self.hand and pokemon.evolution_stage == "basic":
            if not self.active_pokemon:
                self.hand.remove(pokemon)
                pokemon.reset_battle_state()
                pokemon.is_active = True
                self.active_pokemon = pokemon
                return True
        return False
    
    def play_pokemon_to_bench(self, pokemon: PokemonCard) -> bool:
        """将Pokemon放到后备区"""
        if (pokemon in self.hand and 
            pokemon.evolution_stage == "basic" and 
            len(self.bench) < 5):
            
            self.hand.remove(pokemon)
            pokemon.reset_battle_state()
            pokemon.is_benched = True
            self.bench.append(pokemon)
            return True
        return False
    
    def evolve_pokemon(self, evolution: PokemonCard, target_pokemon: PokemonCard) -> bool:
        """进化Pokemon"""
        if evolution in self.hand and self._can_evolve_pokemon(evolution):
            # 检查目标Pokemon
            if target_pokemon == self.active_pokemon:
                # 进化战斗场Pokemon
                self.hand.remove(evolution)
                evolution.current_hp = target_pokemon.current_hp  # 保留伤害
                evolution.attached_energies = target_pokemon.attached_energies.copy()
                evolution.status_conditions = target_pokemon.status_conditions.copy()
                evolution.is_active = True
                
                # 替换Pokemon
                self.discard_pile.append(target_pokemon)
                self.active_pokemon = evolution
                return True
            
            elif target_pokemon in self.bench:
                # 进化后备区Pokemon
                bench_index = self.bench.index(target_pokemon)
                self.hand.remove(evolution)
                evolution.current_hp = target_pokemon.current_hp
                evolution.attached_energies = target_pokemon.attached_energies.copy()
                evolution.status_conditions = target_pokemon.status_conditions.copy()
                evolution.is_benched = True
                
                # 替换Pokemon
                self.discard_pile.append(target_pokemon)
                self.bench[bench_index] = evolution
                return True
        
        return False
    
    def attach_energy(self, energy: EnergyCard, target_pokemon: PokemonCard) -> bool:
        """给Pokemon附加能量"""
        if (energy in self.hand and 
            not self.energy_played_this_turn and
            target_pokemon in [self.active_pokemon] + self.bench):
            
            self.hand.remove(energy)
            target_pokemon.attach_energy(energy.energy_type)
            self.energy_played_this_turn = True
            
            # 基础能量卡不进入弃牌堆，特殊能量卡需要
            if not energy.is_basic:
                self.discard_pile.append(energy)
            
            return True
        return False
    
    def retreat_pokemon(self, new_active: PokemonCard) -> bool:
        """Pokemon撤退"""
        if (self.active_pokemon and 
            self.active_pokemon.can_retreat() and
            new_active in self.bench):
            
            # 支付撤退费用
            retreat_cost = self.active_pokemon.retreat_cost
            removed_energy = 0
            
            # 移除能量作为撤退费用
            for energy_type in list(self.active_pokemon.attached_energies):
                if removed_energy >= retreat_cost:
                    break
                self.active_pokemon.remove_energy(energy_type, 1)
                removed_energy += 1
            
            # 交换Pokemon
            self.active_pokemon.is_active = False
            self.active_pokemon.is_benched = True
            
            bench_index = self.bench.index(new_active)
            self.bench[bench_index] = self.active_pokemon
            
            new_active.is_active = True
            new_active.is_benched = False
            self.active_pokemon = new_active
            
            return True
        return False
    
    def get_basic_pokemon_count(self) -> int:
        """获取手牌中基础Pokemon的数量"""
        return sum(1 for card in self.hand 
                  if (card.card_type == CardType.POKEMON and 
                      hasattr(card, 'evolution_stage') and 
                      card.evolution_stage == "basic"))
    
    def has_valid_active_pokemon(self) -> bool:
        """检查是否有有效的战斗场Pokemon"""
        return (self.active_pokemon is not None and 
                not self.active_pokemon.is_knocked_out())
    
    def get_available_pokemon_for_active(self) -> List[PokemonCard]:
        """获取可以作为战斗场Pokemon的后备Pokemon"""
        return [pokemon for pokemon in self.bench 
                if pokemon and not pokemon.is_knocked_out()]

class BattleEngine:
    """对战引擎"""
    
    def __init__(self, player1: Player, player2: Player):
        """
        初始化对战引擎
        
        Args:
            player1: 玩家1
            player2: 玩家2
        """
        self.player1 = player1
        self.player2 = player2
        self.current_player = player1
        self.opponent_player = player2
        
        # 游戏状态
        self.battle_state = BattleState.WAITING
        self.current_phase = GamePhase.SETUP
        self.turn_number = 0
        self.winner = None
        
        # 对战历史
        self.battle_log = []
        self.start_time = None
        self.end_time = None
        
        # 事件回调
        self.on_turn_start: Optional[Callable[[Player], None]] = None
        self.on_turn_end: Optional[Callable[[Player], None]] = None
        self.on_pokemon_knocked_out: Optional[Callable[[PokemonCard, Player], None]] = None
        self.on_battle_end: Optional[Callable[[Player], None]] = None
        
        print(f"⚔️ 对战开始: {player1.name} vs {player2.name}")
    
    def setup_game(self) -> bool:
        """
        设置游戏初始状态
        
        Returns:
            设置是否成功
        """
        self.battle_state = BattleState.IN_PROGRESS
        self.start_time = time.time()
        
        # 洗牌
        self.player1.deck.shuffle()
        self.player2.deck.shuffle()
        
        # 设置奖励卡（简化为3张）
        for _ in range(3):
            if self.player1.deck.cards:
                self.player1.prize_cards.append(self.player1.deck.draw_card())
            if self.player2.deck.cards:
                self.player2.prize_cards.append(self.player2.deck.draw_card())
        
        # 抽起手牌
        self.player1.draw_card(7)
        self.player2.draw_card(7)
        
        # 检查起手牌中是否有基础Pokemon
        p1_has_basic = self.player1.get_basic_pokemon_count() > 0
        p2_has_basic = self.player2.get_basic_pokemon_count() > 0
        
        if not p1_has_basic or not p2_has_basic:
            # 重新发牌（实际规则更复杂）
            self._redraw_hands()
        
        # 放置初始Pokemon（自动选择第一个基础Pokemon）
        self._auto_place_initial_pokemon()
        
        # 决定先攻（随机）
        if random.choice([True, False]):
            self.current_player = self.player1
            self.opponent_player = self.player2
        else:
            self.current_player = self.player2
            self.opponent_player = self.player1
        
        self.current_phase = GamePhase.DRAW
        self.turn_number = 1
        
        self.log_event(f"游戏开始，{self.current_player.name}先攻")
        return True
    
    def _redraw_hands(self):
        """重新发牌"""
        # 将手牌放回牌库
        for player in [self.player1, self.player2]:
            for card in player.hand:
                player.deck.put_card_on_bottom(card)
            player.hand.clear()
            player.deck.shuffle()
            player.draw_card(7)
    
    def _auto_place_initial_pokemon(self):
        """自动放置初始Pokemon"""
        for player in [self.player1, self.player2]:
            # 找到第一个基础Pokemon放到战斗场
            for card in player.hand[:]:
                if (card.card_type == CardType.POKEMON and 
                    hasattr(card, 'evolution_stage') and 
                    card.evolution_stage == "basic"):
                    player.play_pokemon_to_active(card)
                    break
    
    def start_turn(self):
        """开始回合"""
        self.current_player.reset_turn_state()
        self.current_phase = GamePhase.DRAW
        
        if self.on_turn_start:
            self.on_turn_start(self.current_player)
        
        self.log_event(f"{self.current_player.name}的回合开始")
        
        # 抽牌阶段（除了第一回合先攻玩家）
        if not (self.turn_number == 1 and self.current_player == self.player1):
            drawn_cards = self.current_player.draw_card(1)
            if drawn_cards:
                self.log_event(f"{self.current_player.name}抽了1张牌")
            else:
                # 牌库空了，游戏结束
                self.end_battle(self.opponent_player, "对手牌库用尽")
                return
        
        self.current_player.has_drawn = True
        self.current_phase = GamePhase.MAIN
    
    def play_card(self, card: Any, target: Any = None) -> bool:
        """
        打出卡片
        
        Args:
            card: 要打出的卡片
            target: 目标（如Pokemon、位置等）
            
        Returns:
            是否成功打出
        """
        if not self.current_player.can_play_card(card):
            return False
        
        success = False
        
        if card.card_type == CardType.POKEMON:
            success = self._play_pokemon_card(card, target)
        elif card.card_type == CardType.ENERGY:
            success = self._play_energy_card(card, target)
        elif card.card_type == CardType.TRAINER:
            success = self._play_trainer_card(card, target)
        
        if success:
            self.log_event(f"{self.current_player.name}使用了{card.name}")
        
        return success
    
    def _play_pokemon_card(self, pokemon: PokemonCard, target: str) -> bool:
        """打出Pokemon卡"""
        if pokemon.evolution_stage == "basic":
            if target == "active" and not self.current_player.active_pokemon:
                return self.current_player.play_pokemon_to_active(pokemon)
            elif target == "bench":
                return self.current_player.play_pokemon_to_bench(pokemon)
        else:
            # 进化Pokemon
            if isinstance(target, PokemonCard):
                return self.current_player.evolve_pokemon(pokemon, target)
        
        return False
    
    def _play_energy_card(self, energy: EnergyCard, target: PokemonCard) -> bool:
        """打出能量卡"""
        if isinstance(target, PokemonCard):
            return self.current_player.attach_energy(energy, target)
        return False
    
    def _play_trainer_card(self, trainer: TrainerCard, target: Any = None) -> bool:
        """打出训练师卡"""
        # 简化的训练师卡效果处理
        if trainer.name == "Professor Oak":
            # 弃掉所有手牌，抽7张新牌
            self.current_player.discard_pile.extend(self.current_player.hand)
            self.current_player.hand.clear()
            self.current_player.draw_card(7)
        elif trainer.name == "Bill":
            # 抽2张牌
            self.current_player.draw_card(2)
        elif trainer.name == "Potion":
            # 回复目标Pokemon 20 HP
            if isinstance(target, PokemonCard) and target.current_hp < target.hp:
                target.heal(20)
        
        # 训练师卡使用后进入弃牌堆
        self.current_player.hand.remove(trainer)
        self.current_player.discard_pile.append(trainer)
        return True
    
    def attack(self, attack_index: int, target: PokemonCard = None) -> bool:
        """
        发动攻击
        
        Args:
            attack_index: 攻击技能索引
            target: 攻击目标（默认对手战斗场Pokemon）
            
        Returns:
            攻击是否成功
        """
        if (self.current_phase != GamePhase.MAIN or 
            self.current_player.has_attacked or
            not self.current_player.active_pokemon):
            return False
        
        attacker = self.current_player.active_pokemon
        
        if not attacker.can_attack(attack_index):
            return False
        
        if target is None:
            target = self.opponent_player.active_pokemon
        
        if not target:
            return False
        
        attack = attacker.attacks[attack_index]
        
        # 计算伤害
        base_damage = attack.damage
        actual_damage = target.take_damage(base_damage, attacker.pokemon_type)
        
        self.log_event(f"{attacker.name}使用{attack.name}对{target.name}造成{actual_damage}点伤害")
        
        # 检查目标是否被击倒
        if target.is_knocked_out():
            self._handle_pokemon_knockout(target, self.opponent_player)
        
        # 处理攻击效果
        self._process_attack_effects(attack, attacker, target)
        
        self.current_player.has_attacked = True
        return True
    
    def _handle_pokemon_knockout(self, knocked_out_pokemon: PokemonCard, owner: Player):
        """处理Pokemon被击倒"""
        self.log_event(f"{knocked_out_pokemon.name}被击倒了！")
        
        # 移除被击倒的Pokemon
        if owner.active_pokemon == knocked_out_pokemon:
            owner.active_pokemon = None
            owner.discard_pile.append(knocked_out_pokemon)
        elif knocked_out_pokemon in owner.bench:
            owner.bench.remove(knocked_out_pokemon)
            owner.discard_pile.append(knocked_out_pokemon)
        
        # 攻击方获得奖励卡
        attacking_player = self.current_player
        if attacking_player.prize_cards:
            prize = attacking_player.prize_cards.pop(0)
            attacking_player.hand.append(prize)
            attacking_player.prizes_taken += 1
            self.log_event(f"{attacking_player.name}获得了1张奖励卡")
        
        # 增加击倒计数
        self.current_player.pokemon_knocked_out += 1
        
        # 回调事件
        if self.on_pokemon_knocked_out:
            self.on_pokemon_knocked_out(knocked_out_pokemon, owner)
        
        # 检查胜利条件
        if self._check_win_conditions():
            return
        
        # 如果战斗场Pokemon被击倒，需要选择新的战斗场Pokemon
        if not owner.has_valid_active_pokemon():
            available_pokemon = owner.get_available_pokemon_for_active()
            if available_pokemon:
                # 自动选择第一个可用的Pokemon（实际游戏中由玩家选择）
                new_active = available_pokemon[0]
                owner.bench.remove(new_active)
                new_active.is_benched = False
                new_active.is_active = True
                owner.active_pokemon = new_active
                self.log_event(f"{new_active.name}成为新的战斗场Pokemon")
            else:
                # 没有可用的Pokemon，游戏结束
                self.end_battle(self.current_player, "对手没有可用的Pokemon")
    
    def _process_attack_effects(self, attack, attacker: PokemonCard, target: PokemonCard):
        """处理攻击的特殊效果"""
        for effect in attack.effects:
            if effect == "burn":
                target.add_status_condition(StatusCondition.BURN)
            elif effect == "poison":
                target.add_status_condition(StatusCondition.POISON)
            elif effect == "paralysis":
                target.add_status_condition(StatusCondition.PARALYSIS)
            elif effect == "sleep":
                target.add_status_condition(StatusCondition.SLEEP)
            elif effect.startswith("heal_"):
                # 回复效果，格式: "heal_30"
                heal_amount = int(effect.split("_")[1])
                attacker.heal(heal_amount)
    
    def end_turn(self):
        """结束回合"""
        if self.on_turn_end:
            self.on_turn_end(self.current_player)
        
        # 处理状态异常
        self._process_status_conditions()
        
        # 切换玩家
        self.current_player, self.opponent_player = self.opponent_player, self.current_player
        self.turn_number += 1
        
        self.log_event(f"回合结束")
        
        # 开始下一回合
        self.start_turn()
    
    def _process_status_conditions(self):
        """处理状态异常效果"""
        for player in [self.player1, self.player2]:
            all_pokemon = [player.active_pokemon] + player.bench
            
            for pokemon in all_pokemon:
                if not pokemon:
                    continue
                
                # 处理中毒
                if pokemon.has_status_condition(StatusCondition.POISON):
                    damage = pokemon.take_damage(10)  # 中毒每回合10点伤害
                    self.log_event(f"{pokemon.name}受到中毒伤害{damage}点")
                    
                    if pokemon.is_knocked_out():
                        self._handle_pokemon_knockout(pokemon, player)
                
                # 处理灼伤
                if pokemon.has_status_condition(StatusCondition.BURN):
                    # 投硬币，正面则灼伤解除，反面则受到20点伤害
                    if random.choice([True, False]):
                        pokemon.remove_status_condition(StatusCondition.BURN)
                        self.log_event(f"{pokemon.name}的灼伤状态解除了")
                    else:
                        damage = pokemon.take_damage(20)
                        self.log_event(f"{pokemon.name}受到灼伤伤害{damage}点")
                        
                        if pokemon.is_knocked_out():
                            self._handle_pokemon_knockout(pokemon, player)
    
    def _check_win_conditions(self) -> bool:
        """
        检查胜利条件
        
        Returns:
            是否有玩家胜利
        """
        # 条件1：获得所有奖励卡
        if len(self.player1.prize_cards) == 0:
            self.end_battle(self.player1, "获得所有奖励卡")
            return True
        elif len(self.player2.prize_cards) == 0:
            self.end_battle(self.player2, "获得所有奖励卡")
            return True
        
        # 条件2：对手没有可用的Pokemon
        if not self.player1.has_valid_active_pokemon() and not self.player1.get_available_pokemon_for_active():
            self.end_battle(self.player2, "对手没有可用的Pokemon")
            return True
        elif not self.player2.has_valid_active_pokemon() and not self.player2.get_available_pokemon_for_active():
            self.end_battle(self.player1, "对手没有可用的Pokemon")
            return True
        
        # 条件3：对手无法抽牌（牌库空）
        if len(self.player1.deck.cards) == 0:
            self.end_battle(self.player2, "对手牌库用尽")
            return True
        elif len(self.player2.deck.cards) == 0:
            self.end_battle(self.player1, "对手牌库用尽")
            return True
        
        return False
    
    def end_battle(self, winner: Player, reason: str):
        """
        结束对战
        
        Args:
            winner: 获胜玩家
            reason: 胜利原因
        """
        self.battle_state = BattleState.FINISHED
        self.winner = winner
        self.end_time = time.time()
        
        self.log_event(f"对战结束！{winner.name}获胜，原因：{reason}")
        
        if self.on_battle_end:
            self.on_battle_end(winner)
    
    def get_battle_duration(self) -> float:
        """获取对战持续时间（秒）"""
        if self.start_time:
            end_time = self.end_time or time.time()
            return end_time - self.start_time
        return 0
    
    def get_battle_summary(self) -> Dict[str, Any]:
        """获取对战摘要"""
        duration = self.get_battle_duration()
        
        return {
            'winner': self.winner.name if self.winner else None,
            'loser': (self.player2 if self.winner == self.player1 else self.player1).name if self.winner else None,
            'duration': duration,
            'turns': self.turn_number,
            'player1_stats': {
                'name': self.player1.name,
                'prizes_taken': self.player1.prizes_taken,
                'pokemon_knocked_out': self.player1.pokemon_knocked_out,
                'cards_remaining': len(self.player1.deck.cards),
                'hand_size': len(self.player1.hand)
            },
            'player2_stats': {
                'name': self.player2.name,
                'prizes_taken': self.player2.prizes_taken,
                'pokemon_knocked_out': self.player2.pokemon_knocked_out,
                'cards_remaining': len(self.player2.deck.cards),
                'hand_size': len(self.player2.hand)
            },
            'battle_log': self.battle_log.copy()
        }
    
    def log_event(self, message: str):
        """记录对战事件"""
        timestamp = time.time()
        log_entry = {
            'timestamp': timestamp,
            'turn': self.turn_number,
            'phase': self.current_phase.value,
            'current_player': self.current_player.name,
            'message': message
        }
        self.battle_log.append(log_entry)
        print(f"[回合{self.turn_number}] {message}")
    
    def get_game_state(self) -> Dict[str, Any]:
        """获取当前游戏状态"""
        return {
            'battle_state': self.battle_state.value,
            'current_phase': self.current_phase.value,
            'current_player': self.current_player.name,
            'turn_number': self.turn_number,
            'player1': self._serialize_player_state(self.player1),
            'player2': self._serialize_player_state(self.player2)
        }
    
    def _serialize_player_state(self, player: Player) -> Dict[str, Any]:
        """序列化玩家状态"""
        return {
            'name': player.name,
            'hand_count': len(player.hand),
            'deck_count': len(player.deck.cards),
            'prize_count': len(player.prize_cards),
            'discard_count': len(player.discard_pile),
            'active_pokemon': player.active_pokemon.to_dict() if player.active_pokemon else None,
            'bench_pokemon': [p.to_dict() if p else None for p in player.bench],
            'has_drawn': player.has_drawn,
            'has_attacked': player.has_attacked,
            'energy_played_this_turn': player.energy_played_this_turn
        }

# AI玩家类（简单的AI逻辑）
class AIPlayer(Player):
    """AI玩家类"""
    
    def __init__(self, player_id: int, name: str, deck: Deck, difficulty: str = "normal"):
        """
        初始化AI玩家
        
        Args:
            player_id: 玩家ID
            name: AI名称
            deck: AI卡组
            difficulty: 难度级别 (easy, normal, hard)
        """
        super().__init__(player_id, name, deck)
        self.difficulty = difficulty
        self.thinking_time = {"easy": 0.5, "normal": 1.0, "hard": 1.5}.get(difficulty, 1.0)
    
    def make_turn_decisions(self, battle_engine: BattleEngine) -> List[Dict[str, Any]]:
        """
        AI做出回合决策
        
        Args:
            battle_engine: 对战引擎
            
        Returns:
            行动列表
        """
        actions = []
        
        # 简单的AI逻辑
        
        # 1. 尝试使用能量
        if not self.energy_played_this_turn:
            energy_action = self._decide_energy_play()
            if energy_action:
                actions.append(energy_action)
        
        # 2. 尝试使用训练师卡
        trainer_action = self._decide_trainer_play()
        if trainer_action:
            actions.append(trainer_action)
        
        # 3. 尝试放置Pokemon
        pokemon_action = self._decide_pokemon_play()
        if pokemon_action:
            actions.append(pokemon_action)
        
        # 4. 决定是否攻击
        if not self.has_attacked:
            attack_action = self._decide_attack()
            if attack_action:
                actions.append(attack_action)
        
        return actions
    
    def _decide_energy_play(self) -> Optional[Dict[str, Any]]:
        """决定能量使用"""
        # 找到手牌中的能量卡
        energy_cards = [card for card in self.hand if card.card_type == CardType.ENERGY]
        
        if not energy_cards:
            return None
        
        # 优先给战斗场Pokemon附加能量
        if self.active_pokemon:
            return {
                'action': 'play_energy',
                'card': energy_cards[0],
                'target': self.active_pokemon
            }
        
        # 否则给后备区Pokemon附加
        if self.bench:
            return {
                'action': 'play_energy',
                'card': energy_cards[0],
                'target': self.bench[0]
            }
        
        return None
    
    def _decide_trainer_play(self) -> Optional[Dict[str, Any]]:
        """决定训练师卡使用"""
        trainer_cards = [card for card in self.hand if card.card_type == CardType.TRAINER]
        
        # 简单策略：优先使用抽牌类训练师卡
        for trainer in trainer_cards:
            if trainer.name in ["Professor Oak", "Bill"]:
                return {
                    'action': 'play_trainer',
                    'card': trainer,
                    'target': None
                }
        
        return None
    
    def _decide_pokemon_play(self) -> Optional[Dict[str, Any]]:
        """决定Pokemon使用"""
        pokemon_cards = [card for card in self.hand if card.card_type == CardType.POKEMON]
        
        for pokemon in pokemon_cards:
            if pokemon.evolution_stage == "basic":
                # 如果没有战斗场Pokemon，优先放置
                if not self.active_pokemon:
                    return {
                        'action': 'play_pokemon',
                        'card': pokemon,
                        'target': 'active'
                    }
                # 否则放到后备区
                elif len(self.bench) < 5:
                    return {
                        'action': 'play_pokemon',
                        'card': pokemon,
                        'target': 'bench'
                    }
        
        return None
    
    def _decide_attack(self) -> Optional[Dict[str, Any]]:
        """决定攻击行动"""
        if not self.active_pokemon:
            return None
        
        # 检查所有可用的攻击
        for i, attack in enumerate(self.active_pokemon.attacks):
            if self.active_pokemon.can_attack(i):
                return {
                    'action': 'attack',
                    'attack_index': i,
                    'target': None  # 默认攻击对手战斗场Pokemon
                }
        
        return None

# 对战工厂函数
def create_battle(player1_data: Dict, player2_data: Dict, 
                 player2_is_ai: bool = False) -> BattleEngine:
    """
    创建对战
    
    Args:
        player1_data: 玩家1数据 {'id', 'name', 'deck'}
        player2_data: 玩家2数据 {'id', 'name', 'deck'}
        player2_is_ai: 玩家2是否为AI
        
    Returns:
        对战引擎实例
    """
    player1 = Player(
        player1_data['id'],
        player1_data['name'],
        player1_data['deck']
    )
    
    if player2_is_ai:
        player2 = AIPlayer(
            player2_data['id'],
            player2_data['name'],
            player2_data['deck'],
            player2_data.get('difficulty', 'normal')
        )
    else:
        player2 = Player(
            player2_data['id'],
            player2_data['name'],
            player2_data['deck']
        )
    
    battle_engine = BattleEngine(player1, player2)
    return battle_engine