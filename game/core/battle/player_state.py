"""
玩家战斗状态管理
管理单个玩家在战斗中的所有状态信息
"""

import random
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from game.core.cards.card_data import Card
from typing import TYPE_CHECKING
if TYPE_CHECKING:  # 只用于类型提示
    from game.core.battle.pokemon_instance import PokemonInstance
    
@dataclass
class CardInstance:
    """卡牌实例（区分同一张卡的不同副本）"""
    card: Card
    instance_id: str  # 唯一实例ID
    position: str = "deck"  # deck, hand, field, discard, prize
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'card': self.card.to_dict(),
            'instance_id': self.instance_id,
            'position': self.position
        }

class PlayerState:
    """玩家战斗状态类"""
    
    def __init__(self, player_id: int, deck_cards: List[Card], is_ai: bool = False):
        """
        初始化玩家状态
        
        Args:
            player_id: 玩家ID
            deck_cards: 卡组卡牌列表
            is_ai: 是否是AI玩家
        """
        self.player_id = player_id
        self.is_ai = is_ai
        
        # 创建卡牌实例
        self.all_cards: List[CardInstance] = []
        self._create_card_instances(deck_cards)
        
        # 游戏区域
        self.deck: List[CardInstance] = []
        self.hand: List[CardInstance] = []
        self.field_pokemon: List['PokemonInstance'] = []  # 场上Pokemon
        self.discard_pile: List[CardInstance] = []
        self.prize_cards: List[CardInstance] = []
        
        # 玩家状态
        self.energy_points = 0  # 当前能量点数
        self.max_energy_per_turn = 1  # 每回合获得的能量点数
        self.prize_cards_taken = 0  # 已获得的奖励卡数量
        
        # 场地状态
        self.active_pokemon: Optional['PokemonInstance'] = None  # 前排Pokemon
        self.bench_pokemon: List['PokemonInstance'] = []  # 后备Pokemon
        self.max_bench_size = 3  # 最大后备Pokemon数量
        
        # 特殊状态
        self.status_effects: List[str] = []  # 玩家级别的状态效果
        self.turn_actions_used: Dict[str, int] = {}  # 本回合已使用的行动
        
        # 初始化卡组
        self._setup_initial_deck()
        
        print(f"👤 玩家状态初始化完成: Player {player_id} ({'AI' if is_ai else 'Human'})")
        print(f"   卡组大小: {len(self.deck)}张")
    
    def _create_card_instances(self, deck_cards: List[Card]):
        """创建卡牌实例"""
        instance_counter = 0
        for card in deck_cards:
            instance = CardInstance(
                card=card,
                instance_id=f"{self.player_id}_{card.id}_{instance_counter}",
                position="deck"
            )
            self.all_cards.append(instance)
            instance_counter += 1
    
    def _setup_initial_deck(self):
        """设置初始卡组"""
        # 将所有卡牌放入卡组并洗牌
        self.deck = [card for card in self.all_cards]
        self.shuffle_deck()
        
        # 设置奖励卡（随机选择3张）
        for _ in range(3):
            if self.deck:
                prize_card = self.deck.pop()
                prize_card.position = "prize"
                self.prize_cards.append(prize_card)

        # # 检查起始手牌是否有Pokemon（添加保护）
        # for player_state in self.player_states.values():
        #     hand_pokemon = player_state.get_hand_pokemon()
        #     if not hand_pokemon:
        #         # 如果没有Pokemon，强制从卡组中找一张
        #         for card in player_state.deck[:]:
        #             if card.card.hp is not None:  # 是Pokemon
        #                 player_state.deck.remove(card)
        #                 card.position = "hand" 
        #                 player_state.hand.append(card)
        #                 break
    
    def shuffle_deck(self):
        """洗牌"""
        random.shuffle(self.deck)
        print(f"🔀 玩家 {self.player_id} 洗牌完成")
    
    def draw_card(self, count: int = 1) -> List[CardInstance]:
        """
        抽卡
        
        Args:
            count: 抽卡数量
        
        Returns:
            抽到的卡牌列表
        """
        drawn_cards = []
        for _ in range(count):
            if self.deck:
                card = self.deck.pop(0)
                card.position = "hand"
                self.hand.append(card)
                drawn_cards.append(card)
        
        if drawn_cards:
            print(f"📇 玩家 {self.player_id} 抽取 {len(drawn_cards)} 张卡")
        
        return drawn_cards
    
    def draw_initial_hand(self, hand_size: int = 5) -> List[CardInstance]:
        """
        抽取起始手牌
        
        Args:
            hand_size: 起始手牌数量
        
        Returns:
            起始手牌
        """
        initial_hand = self.draw_card(hand_size)
        print(f"🎯 玩家 {self.player_id} 抽取起始手牌 {len(initial_hand)} 张")
        return initial_hand
    
    def add_energy(self, amount: int = 1):
        """增加能量点数"""
        self.energy_points += amount
        print(f"⚡ 玩家 {self.player_id} 获得 {amount} 点能量 (总计: {self.energy_points})")
    
    def spend_energy(self, amount: int) -> bool:
        """
        消耗能量点数
        
        Args:
            amount: 消耗数量
        
        Returns:
            是否成功消耗
        """
        if self.energy_points >= amount:
            self.energy_points -= amount
            print(f"⚡ 玩家 {self.player_id} 消耗 {amount} 点能量 (剩余: {self.energy_points})")
            return True
        return False
    
    def can_afford_energy(self, amount: int) -> bool:
        """检查是否有足够能量"""
        return self.energy_points >= amount
    
    def play_pokemon_to_bench(self, card_instance: CardInstance) -> bool:
        """
        将Pokemon放置到后备区
        
        Args:
            card_instance: Pokemon卡牌实例
        
        Returns:
            是否成功放置
        """
        from game.core.battle.pokemon_instance import PokemonInstance
        
        # 检查是否是Pokemon卡
        if not card_instance.card.hp:
            return False
        
        # 检查后备区是否有空位
        if len(self.bench_pokemon) >= self.max_bench_size:
            return False
        
        # 检查卡牌是否在手牌中
        if card_instance not in self.hand:
            return False
        
        # 创建Pokemon实例并放置到后备区
        pokemon_instance = PokemonInstance(card_instance.card, card_instance.instance_id)
        pokemon_instance.position = "bench"
        pokemon_instance.owner_id = self.player_id
        
        self.bench_pokemon.append(pokemon_instance)
        self.field_pokemon.append(pokemon_instance)
        
        # 从手牌移除
        self.hand.remove(card_instance)
        card_instance.position = "field"
        
        print(f"🎯 玩家 {self.player_id} 将 {card_instance.card.name} 放置到后备区")
        return True
    
    def set_active_pokemon(self, pokemon_instance: 'PokemonInstance') -> bool:
        """
        设置前排Pokemon
        
        Args:
            pokemon_instance: Pokemon实例
        
        Returns:
            是否成功设置
        """
        if pokemon_instance not in self.field_pokemon:
            return False
        
        # 如果已有前排Pokemon，移动到后备区
        if self.active_pokemon:
            self.active_pokemon.position = "bench"
            if self.active_pokemon not in self.bench_pokemon:
                self.bench_pokemon.append(self.active_pokemon)
        
        # 设置新的前排Pokemon
        self.active_pokemon = pokemon_instance
        pokemon_instance.position = "active"
        
        # 从后备区移除（如果存在）
        if pokemon_instance in self.bench_pokemon:
            self.bench_pokemon.remove(pokemon_instance)
        
        print(f"⚔️ 玩家 {self.player_id} 设置前排Pokemon: {pokemon_instance.card.name}")
        return True
    
    def retreat_active_pokemon(self, new_active: 'PokemonInstance', energy_cost: int = 1) -> bool:
        """
        撤退前排Pokemon
        
        Args:
            new_active: 新的前排Pokemon
            energy_cost: 撤退消耗的能量
        
        Returns:
            是否成功撤退
        """
        if not self.active_pokemon or new_active not in self.bench_pokemon:
            return False
        
        if not self.can_afford_energy(energy_cost):
            return False
        
        # 消耗能量
        self.spend_energy(energy_cost)
        
        # 执行撤退
        old_active = self.active_pokemon
        self.set_active_pokemon(new_active)
        
        print(f"🏃 玩家 {self.player_id} 撤退 {old_active.card.name}，派出 {new_active.card.name}")
        return True
    
    def take_prize_card(self) -> Optional[CardInstance]:
        """
        获得奖励卡
        
        Returns:
            获得的奖励卡
        """
        if self.prize_cards:
            prize_card = self.prize_cards.pop(0)
            prize_card.position = "hand"
            self.hand.append(prize_card)
            self.prize_cards_taken += 1
            
            print(f"🏆 玩家 {self.player_id} 获得奖励卡: {prize_card.card.name}")
            print(f"   已获得奖励卡: {self.prize_cards_taken}/3")
            
            return prize_card
        return None
    
    def discard_card(self, card_instance: CardInstance):
        """
        将卡牌放入弃牌堆
        
        Args:
            card_instance: 要弃置的卡牌
        """
        # 从当前位置移除
        if card_instance in self.hand:
            self.hand.remove(card_instance)
        
        # 放入弃牌堆
        card_instance.position = "discard"
        self.discard_pile.append(card_instance)
        
        print(f"🗑️ 玩家 {self.player_id} 弃置卡牌: {card_instance.card.name}")
    
    def knockout_pokemon(self, pokemon_instance: 'PokemonInstance'):
        """
        Pokemon被击倒
        
        Args:
            pokemon_instance: 被击倒的Pokemon
        """
        if pokemon_instance in self.field_pokemon:
            self.field_pokemon.remove(pokemon_instance)
        
        if pokemon_instance == self.active_pokemon:
            self.active_pokemon = None
        
        if pokemon_instance in self.bench_pokemon:
            self.bench_pokemon.remove(pokemon_instance)
        
        # 将Pokemon对应的卡牌放入弃牌堆
        for card_instance in self.all_cards:
            if card_instance.instance_id == pokemon_instance.instance_id:
                self.discard_card(card_instance)
                break
        
        print(f"💀 玩家 {self.player_id} 的 {pokemon_instance.card.name} 被击倒")
    
    def get_pokemon_by_id(self, instance_id: str) -> Optional['PokemonInstance']:
        """根据实例ID获取Pokemon"""
        for pokemon in self.field_pokemon:
            if pokemon.instance_id == instance_id:
                return pokemon
        return None
    
    def get_hand_pokemon(self) -> List[CardInstance]:
        """获取手牌中的Pokemon"""
        return [card for card in self.hand if card.card.hp is not None]
    
    def get_hand_trainers(self) -> List[CardInstance]:
        """获取手牌中的训练师卡"""
        return [card for card in self.hand if card.card.hp is None]
    
    def has_pokemon_in_play(self) -> bool:
        """检查是否有Pokemon在场"""
        return len(self.field_pokemon) > 0
    
    def can_play_pokemon(self) -> bool:
        """检查是否可以放置Pokemon"""
        return (len(self.bench_pokemon) < self.max_bench_size and 
                len(self.get_hand_pokemon()) > 0)
    
    def can_attack(self) -> bool:
        """检查是否可以攻击"""
        return (self.active_pokemon is not None and 
                self.active_pokemon.can_attack() and
                self.energy_points > 0)
    
    def reset_turn_actions(self):
        """重置回合行动计数"""
        self.turn_actions_used.clear()
        print(f"🔄 玩家 {self.player_id} 重置回合行动")
    
    def use_turn_action(self, action_type: str, limit: int = 1) -> bool:
        """
        使用回合行动
        
        Args:
            action_type: 行动类型
            limit: 该行动的回合限制
        
        Returns:
            是否可以使用该行动
        """
        current_uses = self.turn_actions_used.get(action_type, 0)
        if current_uses < limit:
            self.turn_actions_used[action_type] = current_uses + 1
            return True
        return False
    
    def check_win_condition(self) -> bool:
        """检查获胜条件"""
        # 获得3张奖励卡获胜
        return self.prize_cards_taken >= 3
    
    def check_lose_condition(self) -> bool:
        """检查失败条件"""
        # 没有Pokemon在场且无法放置新Pokemon
        if not self.has_pokemon_in_play():
            hand_pokemon = self.get_hand_pokemon()
            return len(hand_pokemon) == 0
        return False
    
    def get_field_summary(self) -> Dict[str, Any]:
        """获取场地摘要"""
        return {
            'player_id': self.player_id,
            'is_ai': self.is_ai,
            'energy_points': self.energy_points,
            'hand_size': len(self.hand),
            'deck_size': len(self.deck),
            'discard_size': len(self.discard_pile),
            'prize_cards_remaining': len(self.prize_cards),
            'prize_cards_taken': self.prize_cards_taken,
            'active_pokemon': {
                'name': self.active_pokemon.card.name,
                'hp': f"{self.active_pokemon.current_hp}/{self.active_pokemon.max_hp}",
                'instance_id': self.active_pokemon.instance_id
            } if self.active_pokemon else None,
            'bench_pokemon': [
                {
                    'name': p.card.name,
                    'hp': f"{p.current_hp}/{p.max_hp}",
                    'instance_id': p.instance_id
                } for p in self.bench_pokemon
            ],
            'can_attack': self.can_attack(),
            'can_play_pokemon': self.can_play_pokemon()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'player_id': self.player_id,
            'is_ai': self.is_ai,
            'energy_points': self.energy_points,
            'prize_cards_taken': self.prize_cards_taken,
            'hand': [card.to_dict() for card in self.hand],
            'deck_size': len(self.deck),
            'discard_pile': [card.to_dict() for card in self.discard_pile],
            'prize_cards': [card.to_dict() for card in self.prize_cards],
            'field_pokemon': [pokemon.to_dict() for pokemon in self.field_pokemon],
            'active_pokemon_id': self.active_pokemon.instance_id if self.active_pokemon else None,
            'status_effects': self.status_effects,
            'turn_actions_used': self.turn_actions_used
        }
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"Player({self.player_id}): Energy {self.energy_points}, Hand {len(self.hand)}, Pokemon {len(self.field_pokemon)}"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return f"PlayerState(id={self.player_id}, ai={self.is_ai}, energy={self.energy_points})"