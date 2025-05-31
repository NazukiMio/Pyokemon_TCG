"""
卡组管理器
处理卡组构建、验证和管理功能
"""

from typing import Dict, List, Optional, Tuple, Any
import json
import random
from .card_types import PokemonCard, TrainerCard, EnergyCard, CardType, PokemonType, Rarity, create_card_from_data

class Deck:
    """卡组类"""
    
    def __init__(self, name: str = "New Deck", cards: List[Any] = None):
        """
        初始化卡组
        
        Args:
            name: 卡组名称
            cards: 卡片列表
        """
        self.name = name
        self.cards = cards or []
        self.deck_id = None
        self.is_default = False
        self.created_at = None
        self.updated_at = None
    
    def add_card(self, card: Any, count: int = 1) -> bool:
        """
        添加卡片到卡组
        
        Args:
            card: 卡片对象
            count: 添加数量
            
        Returns:
            是否添加成功
        """
        # 检查卡组大小限制
        if len(self.cards) + count > 60:  # Pokemon TCG标准卡组上限
            return False
        
        # 检查单卡数量限制
        current_count = self.get_card_count(card.card_id)
        max_count = 4 if card.card_type != CardType.ENERGY or not hasattr(card, 'is_basic') or not card.is_basic else 60
        
        if current_count + count > max_count:
            return False
        
        # 添加卡片
        for _ in range(count):
            self.cards.append(card)
        
        return True
    
    def remove_card(self, card_id: str, count: int = 1) -> int:
        """
        从卡组移除卡片
        
        Args:
            card_id: 卡片ID
            count: 移除数量
            
        Returns:
            实际移除的数量
        """
        removed = 0
        cards_to_remove = []
        
        for card in self.cards:
            if card.card_id == card_id and removed < count:
                cards_to_remove.append(card)
                removed += 1
        
        for card in cards_to_remove:
            self.cards.remove(card)
        
        return removed
    
    def get_card_count(self, card_id: str) -> int:
        """获取指定卡片的数量"""
        return sum(1 for card in self.cards if card.card_id == card_id)
    
    def get_card_summary(self) -> Dict[str, Any]:
        """获取卡组摘要"""
        pokemon_count = 0
        trainer_count = 0
        energy_count = 0
        
        for card in self.cards:
            if card.card_type == CardType.POKEMON:
                pokemon_count += 1
            elif card.card_type == CardType.TRAINER:
                trainer_count += 1
            elif card.card_type == CardType.ENERGY:
                energy_count += 1
        
        return {
            'total_cards': len(self.cards),
            'pokemon_count': pokemon_count,
            'trainer_count': trainer_count,
            'energy_count': energy_count,
            'unique_cards': len(set(card.card_id for card in self.cards))
        }
    
    def is_valid(self) -> Tuple[bool, List[str]]:
        """
        验证卡组是否合法
        
        Returns:
            (是否合法, 错误信息列表)
        """
        errors = []
        
        # 检查卡组大小
        if len(self.cards) < 20:
            errors.append(f"卡组至少需要20张卡片，当前只有{len(self.cards)}张")
        elif len(self.cards) > 60:
            errors.append(f"卡组最多60张卡片，当前有{len(self.cards)}张")
        
        # 检查Pokemon卡片数量
        pokemon_count = sum(1 for card in self.cards if card.card_type == CardType.POKEMON)
        if pokemon_count == 0:
            errors.append("卡组必须包含至少一张Pokemon卡片")
        
        # 检查单卡数量限制
        card_counts = {}
        for card in self.cards:
            card_id = card.card_id
            card_counts[card_id] = card_counts.get(card_id, 0) + 1
        
        for card_id, count in card_counts.items():
            card = next((c for c in self.cards if c.card_id == card_id), None)
            if card:
                max_count = 4
                if card.card_type == CardType.ENERGY and hasattr(card, 'is_basic') and card.is_basic:
                    max_count = 60  # 基础能量没有数量限制
                
                if count > max_count:
                    errors.append(f"卡片 {card.name} 数量超限：{count}/{max_count}")
        
        return len(errors) == 0, errors
    
    def shuffle(self):
        """洗牌"""
        random.shuffle(self.cards)
    
    def draw_card(self) -> Optional[Any]:
        """抽一张卡"""
        if self.cards:
            return self.cards.pop(0)
        return None
    
    def draw_hand(self, count: int = 7) -> List[Any]:
        """抽起手牌"""
        hand = []
        for _ in range(min(count, len(self.cards))):
            card = self.draw_card()
            if card:
                hand.append(card)
        return hand
    
    def peek_top_cards(self, count: int = 1) -> List[Any]:
        """查看牌库顶部的卡片（不移除）"""
        return self.cards[:min(count, len(self.cards))]
    
    def put_card_on_top(self, card: Any):
        """将卡片放到牌库顶部"""
        self.cards.insert(0, card)
    
    def put_card_on_bottom(self, card: Any):
        """将卡片放到牌库底部"""
        self.cards.append(card)
    
    def search_card(self, card_type: CardType = None, card_name: str = None,
                   pokemon_type: PokemonType = None) -> List[Any]:
        """
        搜索卡片
        
        Args:
            card_type: 卡片类型
            card_name: 卡片名称
            pokemon_type: Pokemon属性
            
        Returns:
            匹配的卡片列表
        """
        results = []
        
        for card in self.cards:
            match = True
            
            if card_type and card.card_type != card_type:
                match = False
            
            if card_name and card_name.lower() not in card.name.lower():
                match = False
            
            if pokemon_type and hasattr(card, 'pokemon_type') and card.pokemon_type != pokemon_type:
                match = False
            
            if match:
                results.append(card)
        
        return results
    
    def get_basic_pokemon(self) -> List[PokemonCard]:
        """获取基础Pokemon卡片"""
        return [card for card in self.cards 
                if (card.card_type == CardType.POKEMON and 
                    hasattr(card, 'evolution_stage') and 
                    card.evolution_stage == "basic")]
    
    def clone(self) -> 'Deck':
        """克隆卡组"""
        new_deck = Deck(name=f"{self.name} (Copy)")
        new_deck.cards = self.cards.copy()
        return new_deck
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'name': self.name,
            'deck_id': self.deck_id,
            'is_default': self.is_default,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'cards': [card.to_dict() for card in self.cards],
            'summary': self.get_card_summary()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Deck':
        """从字典创建卡组"""
        deck = cls(name=data['name'])
        deck.deck_id = data.get('deck_id')
        deck.is_default = data.get('is_default', False)
        deck.created_at = data.get('created_at')
        deck.updated_at = data.get('updated_at')
        
        # 重建卡片
        for card_data in data.get('cards', []):
            card = create_card_from_data(card_data)
            deck.cards.append(card)
        
        return deck

class DeckManager:
    """卡组管理器"""
    
    def __init__(self, database_extensions=None):
        """
        初始化卡组管理器
        
        Args:
            database_extensions: 数据库扩展对象
        """
        self.database_extensions = database_extensions
        self.user_decks = {}  # user_id -> List[Deck]
        self.deck_templates = []  # 预设卡组模板
        
        # 初始化预设卡组
        self._load_deck_templates()
        
        print("🃏 卡组管理器初始化完成")
    
    def create_deck(self, user_id: int, deck_name: str, cards: List[Any] = None) -> Deck:
        """
        创建新卡组
        
        Args:
            user_id: 用户ID
            deck_name: 卡组名称
            cards: 卡片列表
            
        Returns:
            新创建的卡组
        """
        deck = Deck(name=deck_name, cards=cards or [])
        
        if user_id not in self.user_decks:
            self.user_decks[user_id] = []
        
        self.user_decks[user_id].append(deck)
        
        # 保存到数据库
        if self.database_extensions:
            card_ids = [card.card_id for card in deck.cards]
            deck_id = self.database_extensions.save_user_deck(
                user_id, deck_name, card_ids, 
                is_default=len(self.user_decks[user_id]) == 1
            )
            deck.deck_id = deck_id
        
        print(f"📝 创建卡组: {deck_name} (用户: {user_id})")
        return deck
    
    def load_user_decks(self, user_id: int) -> List[Deck]:
        """
        加载用户的卡组
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户卡组列表
        """
        if self.database_extensions:
            deck_data_list = self.database_extensions.get_user_decks(user_id)
            decks = []
            
            for deck_data in deck_data_list:
                deck = Deck(name=deck_data['name'])
                deck.deck_id = deck_data['id']
                deck.is_default = deck_data['is_default']
                deck.created_at = deck_data['created_at']
                deck.updated_at = deck_data['updated_at']
                
                # 这里需要根据card_ids加载实际的卡片对象
                # 假设我们有一个方法来根据ID获取卡片
                card_ids = deck_data['cards']
                # deck.cards = self._load_cards_by_ids(card_ids)
                
                decks.append(deck)
            
            self.user_decks[user_id] = decks
            return decks
        
        return self.user_decks.get(user_id, [])
    
    def save_deck(self, user_id: int, deck: Deck) -> bool:
        """
        保存卡组
        
        Args:
            user_id: 用户ID
            deck: 卡组对象
            
        Returns:
            是否保存成功
        """
        if self.database_extensions and deck.deck_id:
            card_ids = [card.card_id for card in deck.cards]
            return self.database_extensions.update_user_deck(
                deck.deck_id, deck.name, card_ids, deck.is_default
            )
        return False
    
    def delete_deck(self, user_id: int, deck_id: int) -> bool:
        """
        删除卡组
        
        Args:
            user_id: 用户ID
            deck_id: 卡组ID
            
        Returns:
            是否删除成功
        """
        # 从内存中删除
        if user_id in self.user_decks:
            self.user_decks[user_id] = [
                deck for deck in self.user_decks[user_id] 
                if deck.deck_id != deck_id
            ]
        
        # 从数据库删除
        if self.database_extensions:
            return self.database_extensions.delete_user_deck(deck_id)
        
        return True
    
    def get_default_deck(self, user_id: int) -> Optional[Deck]:
        """
        获取用户的默认卡组
        
        Args:
            user_id: 用户ID
            
        Returns:
            默认卡组或None
        """
        user_decks = self.user_decks.get(user_id, [])
        for deck in user_decks:
            if deck.is_default:
                return deck
        
        # 如果没有默认卡组，返回第一个
        return user_decks[0] if user_decks else None
    
    def set_default_deck(self, user_id: int, deck_id: int) -> bool:
        """
        设置默认卡组
        
        Args:
            user_id: 用户ID
            deck_id: 卡组ID
            
        Returns:
            是否设置成功
        """
        user_decks = self.user_decks.get(user_id, [])
        
        # 清除所有默认标记
        for deck in user_decks:
            deck.is_default = False
        
        # 设置新的默认卡组
        target_deck = None
        for deck in user_decks:
            if deck.deck_id == deck_id:
                deck.is_default = True
                target_deck = deck
                break
        
        # 更新数据库
        if target_deck and self.database_extensions:
            return self.database_extensions.update_user_deck(
                deck_id, is_default=True
            )
        
        return target_deck is not None
    
    def validate_deck_for_battle(self, deck: Deck) -> Tuple[bool, List[str]]:
        """
        验证卡组是否适合对战
        
        Args:
            deck: 卡组对象
            
        Returns:
            (是否合法, 错误信息列表)
        """
        # 基础验证
        is_valid, errors = deck.is_valid()
        
        if not is_valid:
            return False, errors
        
        # 对战特定验证
        basic_pokemon = deck.get_basic_pokemon()
        if len(basic_pokemon) == 0:
            errors.append("卡组必须包含至少一张基础Pokemon")
        
        # 检查能量配比
        energy_count = sum(1 for card in deck.cards if card.card_type == CardType.ENERGY)
        if energy_count < 8:
            errors.append(f"建议至少包含8张能量卡，当前只有{energy_count}张")
        
        return len(errors) == 0, errors
    
    def suggest_deck_improvements(self, deck: Deck) -> List[str]:
        """
        提供卡组改进建议
        
        Args:
            deck: 卡组对象
            
        Returns:
            改进建议列表
        """
        suggestions = []
        summary = deck.get_card_summary()
        
        # 分析卡组构成
        total_cards = summary['total_cards']
        pokemon_ratio = summary['pokemon_count'] / total_cards
        trainer_ratio = summary['trainer_count'] / total_cards
        energy_ratio = summary['energy_count'] / total_cards
        
        # Pokemon比例建议
        if pokemon_ratio < 0.25:
            suggestions.append("Pokemon数量偏少，建议增加到总卡数的25-35%")
        elif pokemon_ratio > 0.4:
            suggestions.append("Pokemon数量偏多，可能导致手牌卡手")
        
        # 训练师卡比例建议
        if trainer_ratio < 0.2:
            suggestions.append("训练师卡偏少，建议增加检索和辅助卡片")
        elif trainer_ratio > 0.4:
            suggestions.append("训练师卡偏多，注意平衡")
        
        # 能量比例建议
        if energy_ratio < 0.2:
            suggestions.append("能量卡偏少，可能影响攻击的稳定性")
        elif energy_ratio > 0.35:
            suggestions.append("能量卡偏多，可能导致后期抽到过多能量")
        
        # 检查基础Pokemon数量
        basic_pokemon_count = len(deck.get_basic_pokemon())
        if basic_pokemon_count < 8:
            suggestions.append("基础Pokemon偏少，建议增加到8-12张")
        
        return suggestions
    
    def create_starter_deck(self, user_id: int, pokemon_type: PokemonType) -> Deck:
        """
        创建新手卡组
        
        Args:
            user_id: 用户ID
            pokemon_type: 主要Pokemon属性
            
        Returns:
            新手卡组
        """
        deck_name = f"新手{pokemon_type.value.title()}卡组"
        deck = self.create_deck(user_id, deck_name)
        
        # 添加基础Pokemon (简化版，实际应该从卡片数据库获取)
        starter_cards = self._get_starter_cards_template(pokemon_type)
        
        for card_template in starter_cards:
            # 这里应该根据模板创建实际的卡片对象
            # card = create_card_from_template(card_template)
            # deck.add_card(card, card_template.get('count', 1))
            pass
        
        return deck
    
    def _load_deck_templates(self):
        """加载预设卡组模板"""
        # 这里可以从配置文件或数据库加载预设卡组
        self.deck_templates = [
            {
                'name': '火系速攻',
                'type': PokemonType.FIRE,
                'description': '以快速攻击为主的火系卡组',
                'cards': []  # 卡片模板列表
            },
            {
                'name': '水系控制',
                'type': PokemonType.WATER,
                'description': '注重控制和持久战的水系卡组',
                'cards': []
            },
            {
                'name': '草系辅助',
                'type': PokemonType.GRASS,
                'description': '擅长回复和辅助的草系卡组',
                'cards': []
            }
        ]
    
    def _get_starter_cards_template(self, pokemon_type: PokemonType) -> List[Dict]:
        """获取新手卡组模板"""
        base_template = [
            # 基础Pokemon
            {'type': 'pokemon', 'stage': 'basic', 'pokemon_type': pokemon_type, 'count': 4},
            {'type': 'pokemon', 'stage': 'basic', 'pokemon_type': PokemonType.COLORLESS, 'count': 4},
            
            # 能量卡
            {'type': 'energy', 'energy_type': pokemon_type, 'count': 12},
            {'type': 'energy', 'energy_type': PokemonType.COLORLESS, 'count': 4},
            
            # 基础训练师卡
            {'type': 'trainer', 'name': 'Professor Oak', 'count': 4},
            {'type': 'trainer', 'name': 'Bill', 'count': 4},
            {'type': 'trainer', 'name': 'Potion', 'count': 2}
        ]
        
        return base_template
    
    def get_deck_statistics(self, user_id: int) -> Dict[str, Any]:
        """
        获取用户卡组统计信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            统计信息字典
        """
        user_decks = self.user_decks.get(user_id, [])
        
        if not user_decks:
            return {}
        
        total_decks = len(user_decks)
        total_cards = sum(len(deck.cards) for deck in user_decks)
        
        # 统计最常用的Pokemon类型
        type_counts = {}
        for deck in user_decks:
            for card in deck.cards:
                if hasattr(card, 'pokemon_type'):
                    ptype = card.pokemon_type
                    type_counts[ptype] = type_counts.get(ptype, 0) + 1
        
        most_used_type = max(type_counts.items(), key=lambda x: x[1])[0] if type_counts else None
        
        # 统计平均卡组大小
        avg_deck_size = total_cards / total_decks if total_decks > 0 else 0
        
        return {
            'total_decks': total_decks,
            'total_cards': total_cards,
            'average_deck_size': round(avg_deck_size, 1),
            'most_used_type': most_used_type.value if most_used_type else None,
            'type_distribution': {t.value: count for t, count in type_counts.items()}
        }
    
    def export_deck(self, deck: Deck) -> str:
        """
        导出卡组为JSON格式
        
        Args:
            deck: 卡组对象
            
        Returns:
            JSON字符串
        """
        return json.dumps(deck.to_dict(), indent=2, ensure_ascii=False)
    
    def import_deck(self, user_id: int, deck_json: str) -> Optional[Deck]:
        """
        从JSON导入卡组
        
        Args:
            user_id: 用户ID
            deck_json: JSON字符串
            
        Returns:
            导入的卡组或None
        """
        try:
            deck_data = json.loads(deck_json)
            deck = Deck.from_dict(deck_data)
            
            # 验证卡组
            is_valid, errors = self.validate_deck_for_battle(deck)
            if not is_valid:
                print(f"❌ 导入的卡组不合法: {errors}")
                return None
            
            # 添加到用户卡组
            if user_id not in self.user_decks:
                self.user_decks[user_id] = []
            
            self.user_decks[user_id].append(deck)
            
            # 保存到数据库
            if self.database_extensions:
                card_ids = [card.card_id for card in deck.cards]
                deck_id = self.database_extensions.save_user_deck(
                    user_id, deck.name, card_ids
                )
                deck.deck_id = deck_id
            
            print(f"✅ 成功导入卡组: {deck.name}")
            return deck
            
        except Exception as e:
            print(f"❌ 导入卡组失败: {e}")
            return None

# 辅助函数
def calculate_deck_power_level(deck: Deck) -> int:
    """
    计算卡组强度等级
    
    Args:
        deck: 卡组对象
        
    Returns:
        强度等级 (1-10)
    """
    if not deck.cards:
        return 1
    
    total_power = 0
    card_count = len(deck.cards)
    
    for card in deck.cards:
        card_power = 1  # 基础分数
        
        if card.card_type == CardType.POKEMON:
            # Pokemon卡片根据HP和攻击力评分
            card_power += card.hp // 20
            if hasattr(card, 'attacks'):
                avg_damage = sum(attack.damage for attack in card.attacks) / len(card.attacks) if card.attacks else 0
                card_power += avg_damage // 25
            
            # 稀有度加成
            if card.rarity == Rarity.LEGENDARY:
                card_power += 3
            elif card.rarity == Rarity.EPIC:
                card_power += 2
            elif card.rarity == Rarity.RARE:
                card_power += 1
        
        elif card.card_type == CardType.TRAINER:
            # 训练师卡固定分数
            card_power += 2
            if card.rarity == Rarity.RARE:
                card_power += 1
        
        total_power += card_power
    
    # 计算平均强度并转换为1-10等级
    avg_power = total_power / card_count
    power_level = min(10, max(1, int(avg_power)))
    
    return power_level

def suggest_deck_matchups(deck: Deck, opponent_decks: List[Deck]) -> List[Tuple[Deck, float]]:
    """
    分析卡组对战匹配度
    
    Args:
        deck: 我方卡组
        opponent_decks: 对手卡组列表
        
    Returns:
        (对手卡组, 胜率预测) 的列表
    """
    matchups = []
    
    my_power = calculate_deck_power_level(deck)
    
    for opponent_deck in opponent_decks:
        opponent_power = calculate_deck_power_level(opponent_deck)
        
        # 简单的胜率计算（实际可以更复杂）
        power_diff = my_power - opponent_power
        base_winrate = 0.5
        
        # 根据强度差异调整胜率
        winrate_adjustment = power_diff * 0.05  # 每点强度差5%胜率
        predicted_winrate = max(0.1, min(0.9, base_winrate + winrate_adjustment))
        
        matchups.append((opponent_deck, predicted_winrate))
    
    # 按胜率排序
    matchups.sort(key=lambda x: x[1], reverse=True)
    
    return matchups