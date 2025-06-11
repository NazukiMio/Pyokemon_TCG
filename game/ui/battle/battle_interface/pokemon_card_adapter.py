# ==== pokemon_card_adapter.py ====
# 保存为: game/ui/battle/battle_interface/pokemon_card_adapter.py

"""
Pokemon卡片适配器 - 将现有Card类适配为pygamecards格式
"""

import pygame
import os
from functools import cached_property
from pygame_cards.abstract import AbstractCard, AbstractCardGraphics
from pygame_cards.set import CardsSet
from game.core.cards.card_data import Card as PokemonCard

class PokemonCardGraphics(AbstractCardGraphics):
    """Pokemon卡片图形类"""
    _battle_cache_instance = None  # caché de imágenes compartida

    def __init__(self, card: 'PokemonCardAdapter'):
        super().__init__(card)
        self.pokemon_card = card.pokemon_card
        
        # 缓存字体
        try:
            self.title_font = pygame.font.SysFont("arial", 14, bold=True)
            self.text_font = pygame.font.SysFont("arial", 10)
            self.number_font = pygame.font.SysFont("arial", 12, bold=True)
        except:
            self.title_font = pygame.font.Font(None, 14)
            self.text_font = pygame.font.Font(None, 10)
            self.number_font = pygame.font.Font(None, 12)
        
    def _extract_card_id_from_instance(self, instance_id):
        """从instance_id中提取原始card_id"""
        if isinstance(instance_id, str) and '_' in instance_id:
            parts = instance_id.split('_')
            if len(parts) >= 3:
                # 移除第一个部分(player_id)和最后一个部分(instance_number)
                card_id = '_'.join(parts[1:-1])
                print(f"🔍 提取card_id: {instance_id} -> {card_id}")
                return card_id
        
        print(f"⚠️ 无法提取card_id，使用原始值: {instance_id}")
        return instance_id

    @cached_property
    def surface(self) -> pygame.Surface:
        """渲染Pokemon卡片"""
        print(f"🔍 渲染卡牌: {self.pokemon_card.name}")
        
        # ✅ 修复：提取正确的card_id
        card_id = self.pokemon_card.id
        if hasattr(self.card, 'instance_id'):
            instance_id = self.card.instance_id
            card_id = self._extract_card_id_from_instance(instance_id)
        
        # ✅ 修复：使用正确的图片路径
        image_path = f"card_assets/images/{card_id}.png"
        
        card_image = None
        
        # 优先从 BattleCache 缓存获取图片
        if hasattr(PokemonCardAdapter, 'battle_cache'):
            card_image = PokemonCardAdapter.battle_cache.get_cached_image(image_path)
        
        # 如果缓存未命中，再尝试从硬盘加载
        if card_image:
            print("   ✅ 从缓存加载卡牌图片")
        else:
            try:
                if os.path.exists(image_path):
                    card_image = pygame.image.load(image_path)
                    print(f"   ✅ 图片加载成功: {card_image.get_size()}")
                else:
                    print(f"   ❌ 图片文件不存在: {image_path}")
            except Exception as e:
                print(f"   ❌ 图片加载失败: {e}")
        
        # 🔧 修复：增加显示尺寸到95%
        target_width = int(self.size[0] * 0.95)
        target_height = int(self.size[1] * 0.95)

        # 创建表面（保持原始大小用于居中）
        surf = pygame.Surface(self.size, pygame.SRCALPHA)

        # 如成功获得图片，则缩放后返回
        if card_image:
            # 🔧 修复：优化缩放算法
            image_rect = card_image.get_rect()
            
            # 计算缩放比例，优先保持宽高比
            scale_x = target_width / image_rect.width
            scale_y = target_height / image_rect.height
            scale = min(scale_x, scale_y)
            
            # 🔧 增加显示尺寸：适当放大缩放比例
            scale = min(scale * 1.3, 1.0)  # 增加30%但不超过原尺寸
            
            # 计算缩放后的尺寸
            scaled_width = int(image_rect.width * scale)
            scaled_height = int(image_rect.height * scale)
            
            # 缩放图片
            scaled_image = pygame.transform.scale(card_image, (scaled_width, scaled_height))
            
            # 计算居中位置
            center_x = (self.size[0] - scaled_width) // 2
            center_y = (self.size[1] - scaled_height) // 2
            
            # 渲染缩放后的图片
            surf.blit(scaled_image, (center_x, center_y))
            print(f"✅ 渲染卡牌图片: {self.pokemon_card.name} (缩放比例: {scale:.2f}, 尺寸: {scaled_width}x{scaled_height})")
            return surf
        
        # 否则执行原有降级绘制...
        print("   🎨 使用简化绘制卡牌图形")
        
        # ✅ 修复：绘制到80%大小的区域
        padding = (self.size[0] - target_width) // 2
        render_rect = pygame.Rect(padding, padding, target_width, target_height)
        
        self._draw_base_card_fixed(surf, render_rect)
        if self.pokemon_card.hp:
            self._draw_pokemon_card_fixed(surf, render_rect)
        else:
            self._draw_trainer_card_fixed(surf, render_rect)
        
        return surf

    def _draw_base_card_fixed(self, surf, rect):
        """绘制基础卡片（修复版）"""
        # 圆角矩形背景
        radius = int(0.08 * min(rect.width, rect.height))
        
        # 根据稀有度确定边框颜色
        rarity_colors = {
            'Common': (200, 200, 200),
            'Uncommon': (100, 255, 100),
            'Rare': (100, 100, 255),
            'Ultra Rare': (255, 215, 0)
        }
        
        border_color = rarity_colors.get(self.pokemon_card.rarity, (150, 150, 150))
        
        # 卡片背景
        pygame.draw.rect(surf, (240, 240, 240), rect, 0, radius)
        pygame.draw.rect(surf, border_color, rect, 3, radius)
    
    def _draw_pokemon_card_fixed(self, surf, rect):
        """绘制Pokemon卡片（修复版）"""
        # ✅ 动态调整字体大小
        name_font_size = max(12, rect.height // 10)
        number_font_size = max(10, rect.height // 12)
        text_font_size = max(8, rect.height // 15)
        
        try:
            name_font = pygame.font.SysFont("arial", name_font_size, bold=True)
            number_font = pygame.font.SysFont("arial", number_font_size, bold=True)
            text_font = pygame.font.SysFont("arial", text_font_size)
        except:
            name_font = pygame.font.Font(None, name_font_size)
            number_font = pygame.font.Font(None, number_font_size)
            text_font = pygame.font.Font(None, text_font_size)
        
        # 卡片名称
        name = self.pokemon_card.name
        max_name_chars = rect.width // 8
        if len(name) > max_name_chars:
            name = name[:max_name_chars-2] + ".."
        
        name_surface = name_font.render(name, True, (50, 50, 50))
        name_rect = name_surface.get_rect(centerx=rect.centerx, y=rect.y + 5)
        surf.blit(name_surface, name_rect)
        
        # HP值
        hp_text = f"HP: {self.pokemon_card.hp}"
        hp_surface = number_font.render(hp_text, True, (255, 0, 0))
        hp_rect = hp_surface.get_rect(right=rect.right-5, y=rect.y + 5)
        surf.blit(hp_surface, hp_rect)
        
        # 类型标识
        if self.pokemon_card.types:
            type_text = "/".join(self.pokemon_card.types[:2])
            type_surface = text_font.render(type_text, True, (100, 100, 100))
            type_rect = type_surface.get_rect(centerx=rect.centerx, y=name_rect.bottom + 3)
            surf.blit(type_surface, type_rect)
        
        # 稀有度标识
        rarity_text = self.pokemon_card.rarity[0]
        rarity_surface = text_font.render(rarity_text, True, (100, 100, 100))
        rarity_rect = rarity_surface.get_rect(right=rect.right-3, bottom=rect.bottom-3)
        surf.blit(rarity_surface, rarity_rect)
    
    def _draw_trainer_card_fixed(self, surf, rect):
        """绘制训练师卡片（修复版）"""
        # ✅ 动态调整字体大小
        name_font_size = max(12, rect.height // 10)
        text_font_size = max(8, rect.height // 15)
        
        try:
            name_font = pygame.font.SysFont("arial", name_font_size, bold=True)
            text_font = pygame.font.SysFont("arial", text_font_size)
        except:
            name_font = pygame.font.Font(None, name_font_size)
            text_font = pygame.font.Font(None, text_font_size)
        
        # 卡片名称
        name = self.pokemon_card.name
        max_name_chars = rect.width // 8
        if len(name) > max_name_chars:
            name = name[:max_name_chars-2] + ".."
        
        name_surface = name_font.render(name, True, (50, 50, 50))
        name_rect = name_surface.get_rect(centerx=rect.centerx, y=rect.y + 5)
        surf.blit(name_surface, name_rect)
        
        # 训练师标识
        trainer_surface = text_font.render("TRAINER", True, (0, 100, 200))
        trainer_rect = trainer_surface.get_rect(centerx=rect.centerx, y=name_rect.bottom + 3)
        surf.blit(trainer_surface, trainer_rect)
        
        # 稀有度标识
        rarity_text = self.pokemon_card.rarity[0]
        rarity_surface = text_font.render(rarity_text, True, (100, 100, 100))
        rarity_rect = rarity_surface.get_rect(right=rect.right-3, bottom=rect.bottom-3)
        surf.blit(rarity_surface, rarity_rect)
    
    def _wrap_text(self, text: str, max_chars: int) -> list:
        """文字换行"""
        if len(text) <= max_chars:
            return [text]
        
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line + word) <= max_chars:
                current_line += word + " "
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        
        if current_line:
            lines.append(current_line.strip())
        
        return lines[:3]  # 最多3行


class PokemonCardAdapter(AbstractCard):
    """Pokemon卡片适配器"""
    
    def __init__(self, pokemon_card: PokemonCard, instance_id: str = None):
        """
        初始化适配器
        
        Args:
            pokemon_card: 原始Pokemon卡片对象
            instance_id: 实例ID（可选）
        """
        super().__init__(pokemon_card.name)
        self.pokemon_card = pokemon_card
        self.instance_id = instance_id or f"card_{pokemon_card.id}_{self.u_id}"
        
        # 设置图形类型
        self.graphics_type = PokemonCardGraphics
    
    def get_types(self) -> list:
        """获取Pokemon类型"""
        return self.pokemon_card.types if hasattr(self.pokemon_card, 'types') else []
    
    def get_hp(self) -> int:
        """获取HP值"""
        return self.pokemon_card.hp if hasattr(self.pokemon_card, 'hp') else 0
    
    def get_attacks(self) -> list:
        """获取攻击技能"""
        return self.pokemon_card.attacks if hasattr(self.pokemon_card, 'attacks') else []
    
    def is_pokemon(self) -> bool:
        """是否为Pokemon卡"""
        return bool(self.get_hp())
    
    def is_trainer(self) -> bool:
        """是否为训练师卡"""
        return not self.is_pokemon()
    
    def get_rarity_value(self) -> int:
        """获取稀有度数值（用于排序）"""
        rarity_values = {
            'Common': 1,
            'Uncommon': 2,
            'Rare': 3,
            'Ultra Rare': 4
        }
        return rarity_values.get(self.pokemon_card.rarity, 0)
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'instance_id': self.instance_id,
            'name': self.name,
            'original_card': self.pokemon_card.to_dict(),
            'types': self.get_types(),
            'hp': self.get_hp(),
            'is_pokemon': self.is_pokemon(),
            'rarity': self.pokemon_card.rarity
        }
    
    def __str__(self):
        return f"PokemonCard({self.name})"
    
    def __repr__(self):
        return f"PokemonCardAdapter(name='{self.name}', id='{self.instance_id}')"
    
    @classmethod
    def set_battle_cache(cls, cache):
        """Asocia una instancia de BattleCache para uso de carga de imágenes."""
        PokemonCardGraphics.set_battle_cache(cache)


def convert_to_pokemon_cardsset(cards: list, name: str = "Pokemon Deck") -> CardsSet:
    """
    将Pokemon卡片列表转换为pygamecards的CardsSet
    
    Args:
        cards: Pokemon卡片列表
        name: 卡组名称
    
    Returns:
        转换后的CardsSet
    """
    adapted_cards = []
    
    for i, card in enumerate(cards):
        if hasattr(card, 'card'):
            # 如果是CardInstance，提取card属性
            pokemon_card = card.card
            instance_id = getattr(card, 'instance_id', f"card_{i}")
        else:
            # 直接是Card对象
            pokemon_card = card
            instance_id = f"card_{i}"
        
        adapted_card = PokemonCardAdapter(pokemon_card, instance_id)
        adapted_cards.append(adapted_card)
    
    cardset = CardsSet(adapted_cards)
    cardset.name = name
    return cardset


# 使用示例和测试
if __name__ == "__main__":
    # 这里是一个简单的测试示例
    print("Pokemon Card Adapter 测试")
    print("可以在这里添加测试代码")