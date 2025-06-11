# ==== pokemon_card_adapter.py ====
# 保存为: game/ui/battle/battle_interface/pokemon_card_adapter.py

"""
Pokemon卡片适配器 - 将现有Card类适配为pygamecards格式
"""

import pygame
from functools import cached_property
from pygame_cards.abstract import AbstractCard, AbstractCardGraphics
from pygame_cards.set import CardsSet
from game.core.cards.card_data import Card as PokemonCard

class PokemonCardGraphics(AbstractCardGraphics):
    """Pokemon卡片图形类"""
    
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
    
    @cached_property
    def surface(self) -> pygame.Surface:
        """渲染Pokemon卡片"""
        print(f"🔍 [图形调试] 渲染卡牌: {self.pokemon_card.name}")
        
        # 尝试加载真实图片
        image_loaded = False
        card_image = None
        
        if hasattr(self.pokemon_card, 'image_path') and self.pokemon_card.image_path:
            original_path = self.pokemon_card.image_path
            print(f"   原始图片路径: {original_path}")
            
            # 修复路径：添加card_assets前缀
            import os
            if not original_path.startswith('card_assets'):
                # 确保使用正确的路径分隔符
                corrected_path = os.path.join('card_assets', original_path.replace('\\', os.sep).replace('/', os.sep))
            else:
                corrected_path = original_path
            
            print(f"   修正后路径: {corrected_path}")
            
            # 尝试加载图片
            try:
                if os.path.exists(corrected_path):
                    card_image = pygame.image.load(corrected_path)
                    print(f"   ✅ 图片加载成功: {card_image.get_size()}")
                    image_loaded = True
                else:
                    print(f"   ❌ 图片文件不存在: {corrected_path}")
            except Exception as e:
                print(f"   ❌ 图片加载失败: {e}")
        
        # 如果成功加载图片，使用真实图片
        if image_loaded and card_image:
            # 缩放图片到卡片大小
            scaled_image = pygame.transform.scale(card_image, self.size)
            return scaled_image
        else:
            # 降级到手绘卡片
            print(f"   🎨 使用手绘卡片")
            surf = pygame.Surface(self.size, pygame.SRCALPHA)
            
            # 基础卡片背景
            self._draw_base_card(surf)
            
            # 根据卡片类型绘制
            if self.pokemon_card.hp:
                self._draw_pokemon_card(surf)
            else:
                self._draw_trainer_card(surf)
            
            return surf
    
    def _draw_base_card(self, surf):
        """绘制基础卡片"""
        # 圆角矩形背景
        radius = int(0.08 * min(*self.size))
        
        # 根据稀有度确定边框颜色
        rarity_colors = {
            'Common': (200, 200, 200),
            'Uncommon': (100, 255, 100),
            'Rare': (100, 100, 255),
            'Ultra Rare': (255, 215, 0)
        }
        
        border_color = rarity_colors.get(self.pokemon_card.rarity, (150, 150, 150))
        
        # 卡片背景
        pygame.draw.rect(surf, (240, 240, 240), surf.get_rect(), 0, radius)
        pygame.draw.rect(surf, border_color, surf.get_rect(), 3, radius)
    
    def _draw_pokemon_card(self, surf):
        """绘制Pokemon卡片"""
        # 卡片名称
        name = self.pokemon_card.name
        if len(name) > 12:
            name = name[:10] + ".."
        
        name_surface = self.title_font.render(name, True, (50, 50, 50))
        name_rect = name_surface.get_rect(centerx=self.size[0]//2, y=8)
        surf.blit(name_surface, name_rect)
        
        # HP值
        hp_text = f"HP: {self.pokemon_card.hp}"
        hp_surface = self.number_font.render(hp_text, True, (255, 0, 0))
        hp_rect = hp_surface.get_rect(right=self.size[0]-8, y=8)
        surf.blit(hp_surface, hp_rect)
        
        # 类型标识
        if self.pokemon_card.types:
            type_text = "/".join(self.pokemon_card.types[:2])  # 最多显示2个类型
            type_surface = self.text_font.render(type_text, True, (100, 100, 100))
            type_rect = type_surface.get_rect(centerx=self.size[0]//2, y=name_rect.bottom + 5)
            surf.blit(type_surface, type_rect)
        
        # 攻击技能
        if self.pokemon_card.attacks:
            attack_y = self.size[1] // 2
            for i, attack in enumerate(self.pokemon_card.attacks[:2]):  # 最多显示2个攻击
                attack_name = attack.name
                if len(attack_name) > 8:
                    attack_name = attack_name[:6] + ".."
                
                attack_surface = self.text_font.render(attack_name, True, (80, 80, 80))
                attack_rect = attack_surface.get_rect(x=8, y=attack_y + i * 15)
                surf.blit(attack_surface, attack_rect)
                
                # 伤害值
                damage = attack.damage or "0"
                damage_surface = self.text_font.render(damage, True, (200, 0, 0))
                damage_rect = damage_surface.get_rect(right=self.size[0]-8, y=attack_y + i * 15)
                surf.blit(damage_surface, damage_rect)
        
        # 稀有度标识
        rarity_text = self.pokemon_card.rarity[0]  # 第一个字母
        rarity_surface = self.text_font.render(rarity_text, True, (100, 100, 100))
        rarity_rect = rarity_surface.get_rect(right=self.size[0]-5, bottom=self.size[1]-5)
        surf.blit(rarity_surface, rarity_rect)
    
    def _draw_trainer_card(self, surf):
        """绘制训练师卡片"""
        # 卡片名称
        name = self.pokemon_card.name
        if len(name) > 12:
            name = name[:10] + ".."
        
        name_surface = self.title_font.render(name, True, (50, 50, 50))
        name_rect = name_surface.get_rect(centerx=self.size[0]//2, y=8)
        surf.blit(name_surface, name_rect)
        
        # 训练师标识
        trainer_surface = self.text_font.render("TRAINER", True, (0, 100, 200))
        trainer_rect = trainer_surface.get_rect(centerx=self.size[0]//2, y=name_rect.bottom + 5)
        surf.blit(trainer_surface, trainer_rect)
        
        # 效果描述（简化）
        if hasattr(self.pokemon_card, 'text') and self.pokemon_card.text:
            desc_lines = self._wrap_text(self.pokemon_card.text, 10)
            desc_y = self.size[1] // 2 - len(desc_lines) * 6
            
            for line in desc_lines:
                desc_surface = self.text_font.render(line, True, (60, 60, 60))
                desc_rect = desc_surface.get_rect(centerx=self.size[0]//2, y=desc_y)
                surf.blit(desc_surface, desc_rect)
                desc_y += 12
        
        # 稀有度标识
        rarity_text = self.pokemon_card.rarity[0]
        rarity_surface = self.text_font.render(rarity_text, True, (100, 100, 100))
        rarity_rect = rarity_surface.get_rect(right=self.size[0]-5, bottom=self.size[1]-5)
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