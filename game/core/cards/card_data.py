"""
卡牌数据模型
定义卡牌相关的数据结构和枚举
"""

import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any
from enum import Enum

class CardType(Enum):
    """卡牌类型枚举"""
    GRASS = "Grass"
    FIRE = "Fire"
    WATER = "Water"
    LIGHTNING = "Lightning"
    PSYCHIC = "Psychic"
    FIGHTING = "Fighting"
    DARKNESS = "Darkness"
    METAL = "Metal"
    FAIRY = "Fairy"
    DRAGON = "Dragon"
    COLORLESS = "Colorless"

class CardRarity(Enum):
    """卡牌稀有度枚举"""
    COMMON = "Common"
    UNCOMMON = "Uncommon"
    RARE = "Rare"
    RARE_HOLO = "Rare Holo"
    PROMO = "Promo"
    RARE_HOLO_EX = "Rare Holo EX"
    ULTRA_RARE = "Ultra Rare"
    RARE_SECRET = "Rare Secret"
    RARE_HOLO_GX = "Rare Holo GX"
    RARE_SHINY = "Rare Shiny"
    RARE_HOLO_V = "Rare Holo V"
    RARE_BREAK = "Rare BREAK"
    RARE_ULTRA = "Rare Ultra"
    RARE_PRISM_STAR = "Rare Prism Star"
    AMAZING_RARE = "Amazing Rare"
    RARE_SHINING = "Rare Shining"

@dataclass
class Attack:
    """攻击技能数据类"""
    name: str
    damage: str = ""
    text: str = ""
    cost: List[str] = None
    
    def __post_init__(self):
        if self.cost is None:
            self.cost = []
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Attack':
        """从字典创建实例"""
        return cls(
            name=data.get('name', ''),
            damage=data.get('damage', ''),
            text=data.get('text', ''),
            cost=data.get('cost', [])
        )

@dataclass
class Card:
    """卡牌数据类"""
    id: str
    name: str
    hp: Optional[int] = None
    types: List[str] = None
    rarity: str = "Common"
    attacks: List[Attack] = None
    image_path: str = ""
    set_name: str = ""
    card_number: str = ""
    description: str = ""
    
    def __post_init__(self):
        if self.types is None:
            self.types = []
        if self.attacks is None:
            self.attacks = []
        
        # 从ID解析系列名称和卡牌编号
        if self.id and not self.set_name:
            parts = self.id.split('-')
            if len(parts) >= 2:
                self.set_name = parts[0]
                self.card_number = parts[1]
    
    def get_primary_type(self) -> Optional[str]:
        """获取主要类型"""
        return self.types[0] if self.types else None
    
    def is_type(self, card_type: str) -> bool:
        """检查是否为指定类型"""
        return card_type in self.types
    
    def get_rarity_tier(self) -> int:
        """获取稀有度等级（数字越大越稀有）"""
        rarity_tiers = {
            "Common": 1,
            "Uncommon": 2,
            "Rare": 3,
            "Rare Holo": 4,
            "Promo": 5,
            "Rare Holo EX": 6,
            "Ultra Rare": 7,
            "Rare Secret": 8,
            "Rare Holo GX": 9,
            "Rare Shiny": 10,
            "Rare Holo V": 11,
            "Rare BREAK": 12,
            "Rare Ultra": 13,
            "Rare Prism Star": 14,
            "Amazing Rare": 15,
            "Rare Shining": 16
        }
        return rarity_tiers.get(self.rarity, 0)
    
    def get_dust_value(self) -> int:
        """获取分解尘土价值"""
        dust_values = {
            "Common": 5,
            "Uncommon": 10,
            "Rare": 20,
            "Rare Holo": 40,
            "Promo": 30,
            "Rare Holo EX": 100,
            "Ultra Rare": 200,
            "Rare Secret": 300,
            "Rare Holo GX": 400,
            "Rare Shiny": 500,
            "Rare Holo V": 800,
            "Rare BREAK": 600,
            "Rare Ultra": 700,
            "Rare Prism Star": 900,
            "Amazing Rare": 1000,
            "Rare Shining": 1200
        }
        return dust_values.get(self.rarity, 5)
    
    def has_attacks(self) -> bool:
        """检查是否有攻击技能"""
        return len(self.attacks) > 0
    
    def get_attack_names(self) -> List[str]:
        """获取所有攻击技能名称"""
        return [attack.name for attack in self.attacks]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式（用于数据库存储）"""
        return {
            'id': self.id,
            'name': self.name,
            'hp': self.hp,
            'types': json.dumps(self.types) if self.types else '[]',
            'rarity': self.rarity,
            'attacks': json.dumps([attack.to_dict() for attack in self.attacks]),
            'image_path': self.image_path,
            'set_name': self.set_name,
            'card_number': self.card_number,
            'description': self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Card':
        """从字典创建实例（用于数据库读取）"""
        # 解析类型
        types = []
        if isinstance(data.get('types'), str):
            try:
                types = json.loads(data['types'])
            except json.JSONDecodeError:
                types = [data['types']] if data['types'] else []
        elif isinstance(data.get('types'), list):
            types = data['types']
        
        # 解析攻击技能
        attacks = []
        if data.get('attacks'):
            if isinstance(data['attacks'], str):
                try:
                    attacks_data = json.loads(data['attacks'])
                    attacks = [Attack.from_dict(attack) for attack in attacks_data]
                except json.JSONDecodeError:
                    attacks = []
            elif isinstance(data['attacks'], list):
                attacks = [Attack.from_dict(attack) for attack in data['attacks']]
        
        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            hp=data.get('hp'),
            types=types,
            rarity=data.get('rarity', 'Common'),
            attacks=attacks,
            image_path=data.get('image_path', ''),
            set_name=data.get('set_name', ''),
            card_number=data.get('card_number', ''),
            description=data.get('description', '')
        )
    
    @classmethod
    def from_json_card(cls, json_data: Dict[str, Any]) -> 'Card':
        """从原始JSON数据创建实例"""
        # 解析攻击技能
        attacks = []
        if json_data.get('attacks'):
            for attack_data in json_data['attacks']:
                attacks.append(Attack.from_dict(attack_data))
        
        return cls(
            id=json_data.get('id', ''),
            name=json_data.get('name', ''),
            hp=json_data.get('hp'),
            types=json_data.get('types', []),
            rarity=json_data.get('rarity', 'Common'),
            attacks=attacks,
            image_path=json_data.get('image', ''),
            set_name='',  # 会在__post_init__中解析
            card_number='',  # 会在__post_init__中解析
            description=''
        )
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"{self.name} ({self.id}) - {self.rarity}"
    
    def __eq__(self, other) -> bool:
        """相等比较"""
        if not isinstance(other, Card):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """哈希值"""
        return hash(self.id)

@dataclass
class UserCard:
    """用户拥有的卡牌"""
    card: Card
    quantity: int = 1
    obtained_at: str = ""
    
    def total_dust_value(self) -> int:
        """计算总分解价值"""
        return self.card.get_dust_value() * self.quantity
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'card': self.card.to_dict(),
            'quantity': self.quantity,
            'obtained_at': self.obtained_at
        }

@dataclass
class DeckCard:
    """卡组中的卡牌"""
    card: Card
    quantity: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'card': self.card.to_dict(),
            'quantity': self.quantity
        }

@dataclass
class Deck:
    """卡组数据类"""
    id: Optional[int] = None
    name: str = ""
    description: str = ""
    cards: List[DeckCard] = None
    created_at: str = ""
    updated_at: str = ""
    
    def __post_init__(self):
        if self.cards is None:
            self.cards = []
    
    def total_cards(self) -> int:
        """计算总卡牌数量"""
        return sum(deck_card.quantity for deck_card in self.cards)
    
    def unique_cards(self) -> int:
        """计算不重复卡牌数量"""
        return len(self.cards)
    
    def add_card(self, card: Card, quantity: int = 1) -> bool:
        """添加卡牌到卡组"""
        # 检查是否已存在
        for deck_card in self.cards:
            if deck_card.card.id == card.id:
                deck_card.quantity += quantity
                return True
        
        # 添加新卡牌
        self.cards.append(DeckCard(card=card, quantity=quantity))
        return True
    
    def remove_card(self, card_id: str, quantity: int = 1) -> bool:
        """从卡组移除卡牌"""
        for i, deck_card in enumerate(self.cards):
            if deck_card.card.id == card_id:
                deck_card.quantity -= quantity
                if deck_card.quantity <= 0:
                    self.cards.pop(i)
                return True
        return False
    
    def get_card_quantity(self, card_id: str) -> int:
        """获取指定卡牌数量"""
        for deck_card in self.cards:
            if deck_card.card.id == card_id:
                return deck_card.quantity
        return 0
    
    def get_type_distribution(self) -> Dict[str, int]:
        """获取类型分布"""
        type_count = {}
        for deck_card in self.cards:
            for card_type in deck_card.card.types:
                type_count[card_type] = type_count.get(card_type, 0) + deck_card.quantity
        return type_count
    
    def get_rarity_distribution(self) -> Dict[str, int]:
        """获取稀有度分布"""
        rarity_count = {}
        for deck_card in self.cards:
            rarity = deck_card.card.rarity
            rarity_count[rarity] = rarity_count.get(rarity, 0) + deck_card.quantity
        return rarity_count
    
    def is_valid(self, min_cards: int = 20, max_cards: int = 60) -> bool:
        """检查卡组是否有效"""
        total = self.total_cards()
        return min_cards <= total <= max_cards
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'cards': [deck_card.to_dict() for deck_card in self.cards],
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'total_cards': self.total_cards(),
            'unique_cards': self.unique_cards()
        }

# 工具函数
def parse_cards_from_json_file(file_path: str) -> List[Card]:
    """从JSON文件解析卡牌数据"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        cards = []
        for card_data in data:
            try:
                card = Card.from_json_card(card_data)
                cards.append(card)
            except Exception as e:
                print(f"解析卡牌数据失败 {card_data.get('id', 'unknown')}: {e}")
                continue
        
        return cards
    except Exception as e:
        print(f"读取卡牌文件失败 {file_path}: {e}")
        return []

def get_rarity_probabilities() -> Dict[str, float]:
    """获取稀有度概率配置"""
    return {
        "Common": 0.35,
        "Uncommon": 0.25,
        "Rare": 0.15,
        "Rare Holo": 0.1,
        "Promo": 0.05,
        "Rare Holo EX": 0.03,
        "Ultra Rare": 0.025,
        "Rare Secret": 0.02,
        "Rare Holo GX": 0.015,
        "Rare Shiny": 0.01,
        "Rare Holo V": 0.005,
        "Rare BREAK": 0.005,
        "Rare Ultra": 0.005,
        "Rare Prism Star": 0.005,
        "Amazing Rare": 0.005,
        "Rare Shining": 0.005
    }