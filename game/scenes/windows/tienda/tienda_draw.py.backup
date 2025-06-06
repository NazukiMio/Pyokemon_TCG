"""
现代化商店绘制方法
包含商店窗口的所有绘制逻辑，采用现代毛玻璃风格
"""

import pygame
import math
import random
from typing import Tuple, List, Optional, Dict, Any

class TiendaDrawMixin:
    """商店绘制混入类 - 包含所有绘制相关方法"""
    
    def create_gradient_surface(self, size: Tuple[int, int], start_color: Tuple[int, int, int], 
                               end_color: Tuple[int, int, int], direction: str = 'vertical') -> pygame.Surface:
        """创建渐变表面"""
        surface = pygame.Surface(size, pygame.SRCALPHA)
        width, height = size
        
        if direction == 'vertical':
            for y in range(height):
                ratio = y / height
                color = [
                    int(start_color[i] * (1 - ratio) + end_color[i] * ratio)
                    for i in range(3)
                ]
                pygame.draw.line(surface, color, (0, y), (width, y))
        else:  # horizontal
            for x in range(width):
                ratio = x / width
                color = [
                    int(start_color[i] * (1 - ratio) + end_color[i] * ratio)
                    for i in range(3)
                ]
                pygame.draw.line(surface, color, (x, 0), (x, height))
        
        return surface

    def draw_glass_effect(self, surface: pygame.Surface, rect: pygame.Rect, 
                         bg_color: Tuple[int, int, int, int], border_radius: int = 20,
                         blur_intensity: float = 0.3) -> None:
        """绘制毛玻璃效果"""
        # 创建圆角矩形
        glass_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        
        # 主背景
        pygame.draw.rect(glass_surface, bg_color, (0, 0, rect.width, rect.height), 
                        border_radius=border_radius)
        
        # 添加噪点效果模拟毛玻璃
        if blur_intensity > 0:
            noise_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            for _ in range(int(rect.width * rect.height * blur_intensity * 0.001)):
                x = random.randint(0, rect.width - 1)
                y = random.randint(0, rect.height - 1)
                alpha = random.randint(5, 25)
                color = (255, 255, 255, alpha)
                pygame.draw.circle(noise_surface, color, (x, y), 1)
            
            glass_surface.blit(noise_surface, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2)
        
        surface.blit(glass_surface, rect)

    def draw_soft_shadow(self, surface: pygame.Surface, rect: pygame.Rect, 
                        shadow_color: Tuple[int, int, int] = (0, 0, 0), 
                        shadow_alpha: int = 30, shadow_offset: Tuple[int, int] = (8, 8),
                        shadow_blur: int = 12) -> None:
        """绘制柔和阴影"""
        shadow_surface = pygame.Surface((rect.width + shadow_blur * 2, 
                                       rect.height + shadow_blur * 2), pygame.SRCALPHA)
        
        # 多层阴影创建模糊效果
        for i in range(shadow_blur):
            alpha = shadow_alpha * (1 - i / shadow_blur) ** 2
            if alpha > 0:
                shadow_rect = pygame.Rect(
                    shadow_blur - i, shadow_blur - i,
                    rect.width + i * 2, rect.height + i * 2
                )
                pygame.draw.rect(shadow_surface, (*shadow_color, int(alpha)), 
                               shadow_rect, border_radius=20 + i)
        
        # 绘制到主表面
        shadow_pos = (rect.x + shadow_offset[0] - shadow_blur, 
                     rect.y + shadow_offset[1] - shadow_blur)
        surface.blit(shadow_surface, shadow_pos, special_flags=pygame.BLEND_ALPHA_SDL2)

    def draw_animated_border(self, surface: pygame.Surface, rect: pygame.Rect, 
                           color: Tuple[int, int, int], width: int = 2, 
                           animation_phase: float = 0.0, border_radius: int = 20) -> None:
        """绘制动画边框"""
        # 计算动画参数
        pulse = math.sin(animation_phase * 2) * 0.3 + 0.7
        animated_color = tuple(int(c * pulse) for c in color)
        animated_width = max(1, int(width * pulse))
        
        # 绘制圆角边框
        pygame.draw.rect(surface, animated_color, rect, 
                        width=animated_width, border_radius=border_radius)
        
    def draw_main_window(self, screen: pygame.Surface) -> None:
        """绘制主窗口背景和框架"""
        if not self.is_visible:
            return
        
        # 绘制半透明遮罩
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))
        
        # 绘制主窗口阴影
        self.draw_soft_shadow(screen, self.window_rect, shadow_offset=(12, 12), shadow_blur=20)
        
        # 绘制主窗口背景 - 毛玻璃效果
        self.draw_glass_effect(screen, self.window_rect, (248, 250, 252, 240), border_radius=25)
        
        # 绘制窗口边框
        if hasattr(self, 'animation_time'):
            self.draw_animated_border(screen, self.window_rect, (99, 102, 241), 
                                    width=3, animation_phase=self.animation_time * 2)
        else:
            pygame.draw.rect(screen, (99, 102, 241), self.window_rect, 
                           width=3, border_radius=25)

    def draw_header_section(self, screen: pygame.Surface) -> None:
        """绘制顶部标题区域"""
        if not hasattr(self, 'header_rect'):
            return
        
        # 标题背景渐变
        gradient_surface = self.create_gradient_surface(
            (self.header_rect.width, self.header_rect.height),
            (99, 102, 241), (67, 56, 202), 'horizontal'
        )
        
        # 应用圆角遮罩
        mask = pygame.Surface((self.header_rect.width, self.header_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), 
                        (0, 0, self.header_rect.width, self.header_rect.height), 
                        border_radius=20)
        
        final_header = pygame.Surface((self.header_rect.width, self.header_rect.height), pygame.SRCALPHA)
        final_header.blit(gradient_surface, (0, 0))
        final_header.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        
        screen.blit(final_header, self.header_rect)
        
        # 标题文字
        if hasattr(self, 'font_manager'):
            title_font = self.font_manager.get_font('title', int(32 * self.scale_factor))
        else:
            title_font = pygame.font.SysFont("arial", int(32 * self.scale_factor), bold=True)
        
        title_surface = title_font.render("🛍️ Tienda Pokémon", True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(
            self.header_rect.centerx, 
            self.header_rect.centery
        ))
        
        # 标题阴影
        shadow_surface = title_font.render("🛍️ Tienda Pokémon", True, (0, 0, 0, 100))
        shadow_rect = shadow_surface.get_rect(center=(title_rect.centerx + 2, title_rect.centery + 2))
        screen.blit(shadow_surface, shadow_rect)
        screen.blit(title_surface, title_rect)

    def draw_close_button(self, screen: pygame.Surface) -> None:
        """绘制关闭按钮"""
        if not hasattr(self, 'close_button_rect'):
            return
        
        # 按钮背景
        is_hovered = hasattr(self, 'close_button_hovered') and self.close_button_hovered
        
        if is_hovered:
            bg_color = (239, 68, 68, 200)
            border_color = (220, 38, 38)
        else:
            bg_color = (156, 163, 175, 150)
            border_color = (107, 114, 128)
        
        # 绘制按钮阴影
        self.draw_soft_shadow(screen, self.close_button_rect, shadow_offset=(4, 4), shadow_blur=8)
        
        # 绘制按钮背景
        self.draw_glass_effect(screen, self.close_button_rect, bg_color, border_radius=15)
        
        # 绘制按钮边框
        pygame.draw.rect(screen, border_color, self.close_button_rect, 
                        width=2, border_radius=15)
        
        # X 符号
        font = pygame.font.SysFont("arial", int(20 * self.scale_factor), bold=True)
        x_surface = font.render("✕", True, (255, 255, 255))
        x_rect = x_surface.get_rect(center=self.close_button_rect.center)
        screen.blit(x_surface, x_rect)

    def draw_categories_sidebar(self, screen: pygame.Surface) -> None:
        """绘制左侧分类栏"""
        if not hasattr(self, 'sidebar_rect'):
            return
        
        # 侧边栏背景
        self.draw_glass_effect(screen, self.sidebar_rect, (255, 255, 255, 180), border_radius=20)
        
        # 侧边栏边框
        pygame.draw.rect(screen, (229, 231, 235), self.sidebar_rect, 
                        width=2, border_radius=20)
        
        # 分类标题
        if hasattr(self, 'font_manager'):
            category_font = self.font_manager.get_font('subtitle', int(18 * self.scale_factor))
        else:
            category_font = pygame.font.SysFont("arial", int(18 * self.scale_factor), bold=True)
        
        title_surface = category_font.render("Categorías", True, (55, 65, 81))
        title_y = self.sidebar_rect.y + int(20 * self.scale_factor)
        title_x = self.sidebar_rect.centerx - title_surface.get_width() // 2
        screen.blit(title_surface, (title_x, title_y))
        
        # 绘制分类按钮
        if hasattr(self, 'categories') and hasattr(self, 'category_buttons'):
            for i, category in enumerate(self.categories):
                if i < len(self.category_buttons):
                    self.draw_category_button(screen, category, self.category_buttons[i], i)

    def draw_category_button(self, screen: pygame.Surface, category: Dict[str, Any], 
                           button_rect: pygame.Rect, index: int) -> None:
        """绘制单个分类按钮"""
        is_selected = hasattr(self, 'selected_category') and self.selected_category == index
        is_hovered = hasattr(self, 'hovered_category') and self.hovered_category == index
        
        # 按钮状态样式
        if is_selected:
            bg_color = (99, 102, 241, 200)
            text_color = (255, 255, 255)
            border_color = (67, 56, 202)
        elif is_hovered:
            bg_color = (241, 245, 249, 200)
            text_color = (99, 102, 241)
            border_color = (203, 213, 225)
        else:
            bg_color = (248, 250, 252, 150)
            text_color = (75, 85, 99)
            border_color = (229, 231, 235)
        
        # 绘制按钮背景
        self.draw_glass_effect(screen, button_rect, bg_color, border_radius=12)
        
        # 绘制按钮边框
        pygame.draw.rect(screen, border_color, button_rect, width=2, border_radius=12)
        
        # 按钮图标和文字
        if hasattr(self, 'font_manager'):
            button_font = self.font_manager.get_font('button', int(14 * self.scale_factor))
        else:
            button_font = pygame.font.SysFont("arial", int(14 * self.scale_factor))
        
        # 图标
        icon = category.get('icon', '📦')
        icon_surface = button_font.render(icon, True, text_color)
        icon_y = button_rect.y + int(8 * self.scale_factor)
        icon_x = button_rect.centerx - icon_surface.get_width() // 2
        screen.blit(icon_surface, (icon_x, icon_y))
        
        # 文字
        text = category.get('name', 'Categoría')
        text_surface = button_font.render(text, True, text_color)
        text_y = icon_y + icon_surface.get_height() + int(4 * self.scale_factor)
        text_x = button_rect.centerx - text_surface.get_width() // 2
        screen.blit(text_surface, (text_x, text_y))

    def draw_main_content_area(self, screen: pygame.Surface) -> None:
        """绘制主要内容区域"""
        if not hasattr(self, 'content_rect'):
            return
        
        # 内容区域背景
        self.draw_glass_effect(screen, self.content_rect, (255, 255, 255, 200), border_radius=20)
        
        # 内容区域边框
        pygame.draw.rect(screen, (229, 231, 235), self.content_rect, 
                        width=2, border_radius=20)
        
        # 根据当前分类绘制内容
        if hasattr(self, 'selected_category'):
            if self.selected_category == 0:  # 卡包
                self.draw_card_packs_content(screen)
            elif self.selected_category == 1:  # 道具
                self.draw_items_content(screen)
            elif self.selected_category == 2:  # 特殊
                self.draw_special_content(screen)
            else:
                self.draw_placeholder_content(screen)

    def draw_placeholder_content(self, screen: pygame.Surface) -> None:
        """绘制占位符内容"""
        if hasattr(self, 'font_manager'):
            placeholder_font = self.font_manager.get_font('subtitle', int(24 * self.scale_factor))
        else:
            placeholder_font = pygame.font.SysFont("arial", int(24 * self.scale_factor))
        
        text = "Contenido próximamente..."
        text_surface = placeholder_font.render(text, True, (156, 163, 175))
        text_rect = text_surface.get_rect(center=self.content_rect.center)
        screen.blit(text_surface, text_rect)

    def draw_card_packs_content(self, screen: pygame.Surface) -> None:
        """绘制卡包商品内容"""
        if not hasattr(self, 'card_packs') or not hasattr(self, 'pack_grid_rects'):
            return
        
        # 绘制卡包网格
        for i, pack in enumerate(self.card_packs):
            if i < len(self.pack_grid_rects):
                self.draw_card_pack_item(screen, pack, self.pack_grid_rects[i], i)

    def draw_card_pack_item(self, screen: pygame.Surface, pack_data: Dict[str, Any], 
                           item_rect: pygame.Rect, index: int) -> None:
        """绘制单个卡包商品"""
        is_hovered = hasattr(self, 'hovered_pack') and self.hovered_pack == index
        
        # 商品卡片背景
        if is_hovered:
            bg_color = (255, 255, 255, 250)
            border_color = (99, 102, 241)
            shadow_offset = (8, 8)
        else:
            bg_color = (255, 255, 255, 220)
            border_color = (229, 231, 235)
            shadow_offset = (4, 4)
        
        # 绘制卡片阴影
        self.draw_soft_shadow(screen, item_rect, shadow_offset=shadow_offset, shadow_blur=12)
        
        # 绘制卡片背景
        self.draw_glass_effect(screen, item_rect, bg_color, border_radius=15)
        
        # 绘制卡片边框
        border_width = 3 if is_hovered else 2
        pygame.draw.rect(screen, border_color, item_rect, 
                        width=border_width, border_radius=15)
        
        # 卡包图片区域
        img_height = int(item_rect.height * 0.6)
        img_rect = pygame.Rect(
            item_rect.x + 10, item_rect.y + 10,
            item_rect.width - 20, img_height
        )
        
        # 绘制卡包图片
        if 'image' in pack_data and pack_data['image']:
            scaled_image = pygame.transform.scale(pack_data['image'], 
                                                (img_rect.width, img_rect.height))
            screen.blit(scaled_image, img_rect)
        else:
            # 占位符图片
            pygame.draw.rect(screen, (243, 244, 246), img_rect, border_radius=10)
            placeholder_font = pygame.font.SysFont("arial", int(16 * self.scale_factor))
            placeholder_text = placeholder_font.render("📦", True, (156, 163, 175))
            placeholder_rect = placeholder_text.get_rect(center=img_rect.center)
            screen.blit(placeholder_text, placeholder_rect)
        
        # 商品信息区域
        info_y = img_rect.bottom + 5
        info_height = item_rect.bottom - info_y - 10
        
        # 商品名称
        if hasattr(self, 'font_manager'):
            name_font = self.font_manager.get_font('button', int(14 * self.scale_factor))
            price_font = self.font_manager.get_font('text', int(12 * self.scale_factor))
        else:
            name_font = pygame.font.SysFont("arial", int(14 * self.scale_factor), bold=True)
            price_font = pygame.font.SysFont("arial", int(12 * self.scale_factor))
        
        name = pack_data.get('name', 'Sobre Misterioso')
        name_surface = name_font.render(name, True, (31, 41, 55))
        name_rect = name_surface.get_rect(
            centerx=item_rect.centerx,
            y=info_y + 5
        )
        screen.blit(name_surface, name_rect)
        
        # 价格
        price = pack_data.get('price', 100)
        price_text = f"💰 {price} monedas"
        price_surface = price_font.render(price_text, True, (99, 102, 241))
        price_rect = price_surface.get_rect(
            centerx=item_rect.centerx,
            y=name_rect.bottom + 5
        )
        screen.blit(price_surface, price_rect)
        
        # 购买按钮
        button_width = item_rect.width - 20
        button_height = 25
        button_rect = pygame.Rect(
            item_rect.x + 10,
            item_rect.bottom - button_height - 10,
            button_width,
            button_height
        )
        
        self.draw_purchase_button(screen, button_rect, f"buy_pack_{index}", 
                                is_hovered and hasattr(self, 'hovered_button') 
                                and self.hovered_button == f"buy_pack_{index}")

    def draw_purchase_button(self, screen: pygame.Surface, button_rect: pygame.Rect, 
                           button_id: str, is_hovered: bool = False) -> None:
        """绘制购买按钮"""
        if is_hovered:
            bg_color = (67, 56, 202)
            text_color = (255, 255, 255)
        else:
            bg_color = (99, 102, 241)
            text_color = (255, 255, 255)
        
        # 按钮背景
        pygame.draw.rect(screen, bg_color, button_rect, border_radius=8)
        
        # 按钮文字
        if hasattr(self, 'font_manager'):
            button_font = self.font_manager.get_font('button', int(11 * self.scale_factor))
        else:
            button_font = pygame.font.SysFont("arial", int(11 * self.scale_factor), bold=True)
        
        button_text = button_font.render("Comprar", True, text_color)
        button_text_rect = button_text.get_rect(center=button_rect.center)
        screen.blit(button_text, button_text_rect)

    def draw_items_content(self, screen: pygame.Surface) -> None:
        """绘制道具商品内容"""
        if not hasattr(self, 'items') or not hasattr(self, 'item_grid_rects'):
            return
        
        # 绘制道具网格
        for i, item in enumerate(self.items):
            if i < len(self.item_grid_rects):
                self.draw_item_card(screen, item, self.item_grid_rects[i], i)

    def draw_item_card(self, screen: pygame.Surface, item_data: Dict[str, Any], 
                      item_rect: pygame.Rect, index: int) -> None:
        """绘制单个道具卡片"""
        is_hovered = hasattr(self, 'hovered_item') and self.hovered_item == index
        
        # 道具卡片样式
        if is_hovered:
            bg_color = (255, 255, 255, 250)
            border_color = (168, 85, 247)  # 紫色边框
            shadow_offset = (6, 6)
        else:
            bg_color = (255, 255, 255, 220)
            border_color = (229, 231, 235)
            shadow_offset = (3, 3)
        
        # 绘制卡片阴影
        self.draw_soft_shadow(screen, item_rect, shadow_offset=shadow_offset, shadow_blur=10)
        
        # 绘制卡片背景
        self.draw_glass_effect(screen, item_rect, bg_color, border_radius=12)
        
        # 绘制卡片边框
        border_width = 3 if is_hovered else 2
        pygame.draw.rect(screen, border_color, item_rect, 
                        width=border_width, border_radius=12)
        
        # 道具图标区域
        icon_size = int(item_rect.width * 0.3)
        icon_rect = pygame.Rect(
            item_rect.x + (item_rect.width - icon_size) // 2,
            item_rect.y + 15,
            icon_size, icon_size
        )
        
        # 绘制道具图标背景
        icon_bg_color = self.get_item_rarity_color(item_data.get('rarity', 'common'))
        pygame.draw.circle(screen, icon_bg_color, icon_rect.center, icon_size // 2)
        
        # 绘制道具图标
        icon = item_data.get('icon', '🎁')
        if hasattr(self, 'font_manager'):
            icon_font = self.font_manager.get_font('subtitle', int(24 * self.scale_factor))
        else:
            icon_font = pygame.font.SysFont("arial", int(24 * self.scale_factor))
        
        icon_surface = icon_font.render(icon, True, (255, 255, 255))
        icon_text_rect = icon_surface.get_rect(center=icon_rect.center)
        screen.blit(icon_surface, icon_text_rect)
        
        # 道具信息
        info_y = icon_rect.bottom + 10
        
        # 道具名称
        if hasattr(self, 'font_manager'):
            name_font = self.font_manager.get_font('button', int(12 * self.scale_factor))
            desc_font = self.font_manager.get_font('text', int(10 * self.scale_factor))
            price_font = self.font_manager.get_font('button', int(11 * self.scale_factor))
        else:
            name_font = pygame.font.SysFont("arial", int(12 * self.scale_factor), bold=True)
            desc_font = pygame.font.SysFont("arial", int(10 * self.scale_factor))
            price_font = pygame.font.SysFont("arial", int(11 * self.scale_factor), bold=True)
        
        name = item_data.get('name', 'Objeto Misterioso')
        name_surface = name_font.render(name, True, (31, 41, 55))
        name_rect = name_surface.get_rect(
            centerx=item_rect.centerx,
            y=info_y
        )
        screen.blit(name_surface, name_rect)
        
        # 道具描述
        description = item_data.get('description', 'Un objeto útil')
        desc_lines = self.wrap_text(description, desc_font, item_rect.width - 20)
        
        desc_y = name_rect.bottom + 5
        for line in desc_lines[:2]:  # 最多显示2行
            line_surface = desc_font.render(line, True, (107, 114, 128))
            line_rect = line_surface.get_rect(
                centerx=item_rect.centerx,
                y=desc_y
            )
            screen.blit(line_surface, line_rect)
            desc_y += line_surface.get_height() + 2
        
        # 道具价格
        price = item_data.get('price', 50)
        price_text = f"💰 {price}"
        price_surface = price_font.render(price_text, True, (168, 85, 247))
        price_rect = price_surface.get_rect(
            centerx=item_rect.centerx,
            y=desc_y + 8
        )
        screen.blit(price_surface, price_rect)
        
        # 购买按钮
        button_width = item_rect.width - 20
        button_height = 22
        button_rect = pygame.Rect(
            item_rect.x + 10,
            item_rect.bottom - button_height - 8,
            button_width,
            button_height
        )
        
        self.draw_item_purchase_button(screen, button_rect, f"buy_item_{index}", 
                                     is_hovered and hasattr(self, 'hovered_button') 
                                     and self.hovered_button == f"buy_item_{index}")

    def draw_item_purchase_button(self, screen: pygame.Surface, button_rect: pygame.Rect, 
                                button_id: str, is_hovered: bool = False) -> None:
        """绘制道具购买按钮"""
        if is_hovered:
            bg_color = (147, 51, 234)  # 深紫色
            text_color = (255, 255, 255)
        else:
            bg_color = (168, 85, 247)  # 紫色
            text_color = (255, 255, 255)
        
        # 按钮背景
        pygame.draw.rect(screen, bg_color, button_rect, border_radius=6)
        
        # 按钮文字
        if hasattr(self, 'font_manager'):
            button_font = self.font_manager.get_font('button', int(10 * self.scale_factor))
        else:
            button_font = pygame.font.SysFont("arial", int(10 * self.scale_factor), bold=True)
        
        button_text = button_font.render("Comprar", True, text_color)
        button_text_rect = button_text.get_rect(center=button_rect.center)
        screen.blit(button_text, button_text_rect)

    def get_item_rarity_color(self, rarity: str) -> Tuple[int, int, int]:
        """获取道具稀有度颜色"""
        rarity_colors = {
            'common': (107, 114, 128),      # 灰色
            'uncommon': (34, 197, 94),      # 绿色
            'rare': (59, 130, 246),         # 蓝色
            'epic': (168, 85, 247),         # 紫色
            'legendary': (245, 158, 11),    # 橙色
            'mythic': (236, 72, 153)        # 粉色
        }
        return rarity_colors.get(rarity, rarity_colors['common'])

    def wrap_text(self, text: str, font: pygame.font.Font, max_width: int) -> List[str]:
        """文本换行处理"""
        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " " if current_line else word
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        
        if current_line:
            lines.append(current_line.strip())
        
        return lines
    
    def draw_special_content(self, screen: pygame.Surface) -> None:
        """绘制特殊商品内容"""
        if not hasattr(self, 'special_items') or not hasattr(self, 'special_grid_rects'):
            self.draw_coming_soon_placeholder(screen, "Ofertas especiales próximamente...")
            return
        
        # 绘制特殊商品网格
        for i, special_item in enumerate(self.special_items):
            if i < len(self.special_grid_rects):
                self.draw_special_item_card(screen, special_item, self.special_grid_rects[i], i)

    def draw_special_item_card(self, screen: pygame.Surface, item_data: Dict[str, Any], 
                             item_rect: pygame.Rect, index: int) -> None:
        """绘制特殊商品卡片"""
        is_hovered = hasattr(self, 'hovered_special') and self.hovered_special == index
        
        # 特殊商品的闪光效果
        if hasattr(self, 'animation_time'):
            glow_intensity = math.sin(self.animation_time * 3) * 0.3 + 0.7
        else:
            glow_intensity = 1.0
        
        # 特殊商品样式 - 金色主题
        if is_hovered:
            bg_color = (255, 255, 255, 250)
            border_color = (245, 158, 11)  # 金色边框
            glow_color = (252, 211, 77, int(100 * glow_intensity))
        else:
            bg_color = (255, 255, 255, 230)
            border_color = (217, 119, 6)
            glow_color = (252, 211, 77, int(60 * glow_intensity))
        
        # 绘制发光效果
        glow_rect = item_rect.inflate(8, 8)
        self.draw_soft_shadow(screen, glow_rect, shadow_color=glow_color[:3], 
                            shadow_alpha=glow_color[3], shadow_offset=(0, 0), shadow_blur=15)
        
        # 绘制卡片阴影
        self.draw_soft_shadow(screen, item_rect, shadow_offset=(8, 8), shadow_blur=15)
        
        # 绘制卡片背景
        self.draw_glass_effect(screen, item_rect, bg_color, border_radius=15)
        
        # 绘制闪光边框
        border_width = 4 if is_hovered else 3
        pygame.draw.rect(screen, border_color, item_rect, 
                        width=border_width, border_radius=15)
        
        # 特殊标签
        tag_rect = pygame.Rect(item_rect.x + 10, item_rect.y + 10, 60, 20)
        pygame.draw.rect(screen, (239, 68, 68), tag_rect, border_radius=10)
        
        if hasattr(self, 'font_manager'):
            tag_font = self.font_manager.get_font('text', int(9 * self.scale_factor))
        else:
            tag_font = pygame.font.SysFont("arial", int(9 * self.scale_factor), bold=True)
        
        tag_text = tag_font.render("ESPECIAL", True, (255, 255, 255))
        tag_text_rect = tag_text.get_rect(center=tag_rect.center)
        screen.blit(tag_text, tag_text_rect)
        
        # 商品图标和信息（类似普通商品但有特殊效果）
        self.draw_special_item_content(screen, item_data, item_rect, index, glow_intensity)

    def draw_special_item_content(self, screen: pygame.Surface, item_data: Dict[str, Any], 
                                item_rect: pygame.Rect, index: int, glow_intensity: float) -> None:
        """绘制特殊商品的内容"""
        # 图标区域
        icon_size = int(item_rect.width * 0.4)
        icon_rect = pygame.Rect(
            item_rect.x + (item_rect.width - icon_size) // 2,
            item_rect.y + 35,
            icon_size, icon_size
        )
        
        # 特殊图标背景 - 渐变金色
        gradient_surface = self.create_gradient_surface(
            (icon_size, icon_size),
            (245, 158, 11), (217, 119, 6), 'vertical'
        )
        
        # 圆形遮罩
        mask = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
        pygame.draw.circle(mask, (255, 255, 255, 255), (icon_size//2, icon_size//2), icon_size//2)
        
        icon_bg = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
        icon_bg.blit(gradient_surface, (0, 0))
        icon_bg.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        
        screen.blit(icon_bg, icon_rect)
        
        # 特殊图标
        icon = item_data.get('icon', '⭐')
        if hasattr(self, 'font_manager'):
            icon_font = self.font_manager.get_font('title', int(28 * self.scale_factor))
        else:
            icon_font = pygame.font.SysFont("arial", int(28 * self.scale_factor))
        
        # 图标发光效果
        icon_surface = icon_font.render(icon, True, (255, 255, 255))
        icon_text_rect = icon_surface.get_rect(center=icon_rect.center)
        
        # 添加发光
        glow_surface = icon_font.render(icon, True, (255, 255, 255, int(100 * glow_intensity)))
        for offset in [(1, 1), (-1, -1), (1, -1), (-1, 1)]:
            glow_rect = icon_text_rect.copy()
            glow_rect.x += offset[0]
            glow_rect.y += offset[1]
            screen.blit(glow_surface, glow_rect)
        
        screen.blit(icon_surface, icon_text_rect)
        
        # 商品信息
        info_y = icon_rect.bottom + 15
        
        # 名称
        name = item_data.get('name', 'Oferta Especial')
        if hasattr(self, 'font_manager'):
            name_font = self.font_manager.get_font('subtitle', int(14 * self.scale_factor))
        else:
            name_font = pygame.font.SysFont("arial", int(14 * self.scale_factor), bold=True)
        
        name_surface = name_font.render(name, True, (217, 119, 6))
        name_rect = name_surface.get_rect(centerx=item_rect.centerx, y=info_y)
        screen.blit(name_surface, name_rect)
        
        # 价格（可能有折扣）
        original_price = item_data.get('original_price', 200)
        current_price = item_data.get('price', 150)
        
        price_y = name_rect.bottom + 8
        
        if original_price != current_price:
            # 显示折扣价格
            if hasattr(self, 'font_manager'):
                old_price_font = self.font_manager.get_font('text', int(11 * self.scale_factor))
                new_price_font = self.font_manager.get_font('button', int(13 * self.scale_factor))
            else:
                old_price_font = pygame.font.SysFont("arial", int(11 * self.scale_factor))
                new_price_font = pygame.font.SysFont("arial", int(13 * self.scale_factor), bold=True)
            
            # 原价（划线）
            old_price_surface = old_price_font.render(f"💰 {original_price}", True, (156, 163, 175))
            old_price_rect = old_price_surface.get_rect(centerx=item_rect.centerx, y=price_y)
            screen.blit(old_price_surface, old_price_rect)
            
            # 划线效果
            pygame.draw.line(screen, (156, 163, 175), 
                           (old_price_rect.left, old_price_rect.centery),
                           (old_price_rect.right, old_price_rect.centery), 2)
            
            # 新价格
            new_price_surface = new_price_font.render(f"💰 {current_price}", True, (220, 38, 38))
            new_price_rect = new_price_surface.get_rect(centerx=item_rect.centerx, y=old_price_rect.bottom + 3)
            screen.blit(new_price_surface, new_price_rect)
        else:
            # 正常价格
            if hasattr(self, 'font_manager'):
                price_font = self.font_manager.get_font('button', int(13 * self.scale_factor))
            else:
                price_font = pygame.font.SysFont("arial", int(13 * self.scale_factor), bold=True)
            
            price_surface = price_font.render(f"💰 {current_price}", True, (217, 119, 6))
            price_rect = price_surface.get_rect(centerx=item_rect.centerx, y=price_y)
            screen.blit(price_surface, price_rect)
        
        # 特殊购买按钮
        button_width = item_rect.width - 20
        button_height = 28
        button_rect = pygame.Rect(
            item_rect.x + 10,
            item_rect.bottom - button_height - 10,
            button_width,
            button_height
        )
        
        self.draw_special_purchase_button(screen, button_rect, f"buy_special_{index}", 
                                        hasattr(self, 'hovered_button') 
                                        and self.hovered_button == f"buy_special_{index}",
                                        glow_intensity)

    def draw_special_purchase_button(self, screen: pygame.Surface, button_rect: pygame.Rect, 
                                   button_id: str, is_hovered: bool = False, 
                                   glow_intensity: float = 1.0) -> None:
        """绘制特殊购买按钮"""
        # 渐变背景
        if is_hovered:
            start_color = (234, 88, 12)
            end_color = (194, 65, 12)
        else:
            start_color = (245, 158, 11)
            end_color = (217, 119, 6)
        
        gradient_bg = self.create_gradient_surface(
            (button_rect.width, button_rect.height),
            start_color, end_color, 'vertical'
        )
        
        # 圆角遮罩
        mask = pygame.Surface((button_rect.width, button_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), 
                        (0, 0, button_rect.width, button_rect.height), border_radius=8)
        
        button_bg = pygame.Surface((button_rect.width, button_rect.height), pygame.SRCALPHA)
        button_bg.blit(gradient_bg, (0, 0))
        button_bg.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        
        screen.blit(button_bg, button_rect)
        
        # 按钮边框
        pygame.draw.rect(screen, (180, 83, 9), button_rect, width=2, border_radius=8)
        
        # 按钮文字
        if hasattr(self, 'font_manager'):
            button_font = self.font_manager.get_font('button', int(12 * self.scale_factor))
        else:
            button_font = pygame.font.SysFont("arial", int(12 * self.scale_factor), bold=True)
        
        button_text = button_font.render("✨ COMPRAR ✨", True, (255, 255, 255))
        button_text_rect = button_text.get_rect(center=button_rect.center)
        screen.blit(button_text, button_text_rect)

    def draw_coming_soon_placeholder(self, screen: pygame.Surface, message: str) -> None:
        """绘制即将推出的占位符"""
        if hasattr(self, 'font_manager'):
            placeholder_font = self.font_manager.get_font('subtitle', int(20 * self.scale_factor))
        else:
            placeholder_font = pygame.font.SysFont("arial", int(20 * self.scale_factor), bold=True)
        
        text_surface = placeholder_font.render(message, True, (156, 163, 175))
        text_rect = text_surface.get_rect(center=self.content_rect.center)
        screen.blit(text_surface, text_rect)
        
        # 装饰图标
        icon_font = pygame.font.SysFont("arial", int(48 * self.scale_factor))
        icon_surface = icon_font.render("🔜", True, (203, 213, 225))
        icon_rect = icon_surface.get_rect(center=(text_rect.centerx, text_rect.y - 60))
        screen.blit(icon_surface, icon_rect)

    def draw_bottom_status_bar(self, screen: pygame.Surface) -> None:
        """绘制底部状态栏"""
        if not hasattr(self, 'status_bar_rect'):
            return
        
        # 状态栏背景
        self.draw_glass_effect(screen, self.status_bar_rect, (248, 250, 252, 230), border_radius=15)
        
        # 状态栏边框
        pygame.draw.rect(screen, (203, 213, 225), self.status_bar_rect, 
                        width=2, border_radius=15)
        
        # 用户金币信息
        if hasattr(self, 'user_coins'):
            coins = self.user_coins
        else:
            coins = 1000  # 默认值
        
        # 金币图标和数量
        if hasattr(self, 'font_manager'):
            coins_font = self.font_manager.get_font('subtitle', int(18 * self.scale_factor))
        else:
            coins_font = pygame.font.SysFont("arial", int(18 * self.scale_factor), bold=True)
        
        coins_text = f"💰 {coins:,} monedas"
        coins_surface = coins_font.render(coins_text, True, (245, 158, 11))
        coins_rect = coins_surface.get_rect(
            x=self.status_bar_rect.x + 20,
            centery=self.status_bar_rect.centery
        )
        screen.blit(coins_surface, coins_rect)
        
        # 购物车信息（如果有）
        if hasattr(self, 'cart_items') and self.cart_items:
            cart_count = len(self.cart_items)
            cart_text = f"🛒 {cart_count} artículos"
            cart_surface = coins_font.render(cart_text, True, (99, 102, 241))
            cart_rect = cart_surface.get_rect(
                centerx=self.status_bar_rect.centerx,
                centery=self.status_bar_rect.centery
            )
            screen.blit(cart_surface, cart_rect)
        
        # 刷新按钮
        refresh_button_size = 35
        refresh_button_rect = pygame.Rect(
            self.status_bar_rect.right - refresh_button_size - 15,
            self.status_bar_rect.centery - refresh_button_size // 2,
            refresh_button_size,
            refresh_button_size
        )
        
        is_refresh_hovered = (hasattr(self, 'hovered_button') and 
                            self.hovered_button == 'refresh')
        
        self.draw_refresh_button(screen, refresh_button_rect, is_refresh_hovered)

    def draw_refresh_button(self, screen: pygame.Surface, button_rect: pygame.Rect, 
                          is_hovered: bool = False) -> None:
        """绘制刷新按钮"""
        if is_hovered:
            bg_color = (34, 197, 94)
            border_color = (22, 163, 74)
        else:
            bg_color = (74, 222, 128)
            border_color = (34, 197, 94)
        
        # 按钮阴影
        self.draw_soft_shadow(screen, button_rect, shadow_offset=(3, 3), shadow_blur=6)
        
        # 按钮背景
        pygame.draw.circle(screen, bg_color, button_rect.center, button_rect.width // 2)
        
        # 按钮边框
        pygame.draw.circle(screen, border_color, button_rect.center, 
                         button_rect.width // 2, width=2)
        
        # 刷新图标
        icon_font = pygame.font.SysFont("arial", int(16 * self.scale_factor), bold=True)
        icon_surface = icon_font.render("🔄", True, (255, 255, 255))
        icon_rect = icon_surface.get_rect(center=button_rect.center)
        screen.blit(icon_surface, icon_rect)

    def draw_loading_animation(self, screen: pygame.Surface) -> None:
        """绘制加载动画"""
        if not hasattr(self, 'is_loading') or not self.is_loading:
            return
        
        # 加载遮罩
        loading_overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        loading_overlay.fill((0, 0, 0, 100))
        screen.blit(loading_overlay, (0, 0))
        
        # 加载动画区域
        loading_rect = pygame.Rect(
            self.screen_width // 2 - 100,
            self.screen_height // 2 - 50,
            200, 100
        )
        
        # 加载框背景
        self.draw_glass_effect(screen, loading_rect, (255, 255, 255, 250), border_radius=20)
        pygame.draw.rect(screen, (99, 102, 241), loading_rect, width=3, border_radius=20)
        
        # 加载文字
        if hasattr(self, 'font_manager'):
            loading_font = self.font_manager.get_font('subtitle', int(16 * self.scale_factor))
        else:
            loading_font = pygame.font.SysFont("arial", int(16 * self.scale_factor), bold=True)
        
        loading_text = loading_font.render("Cargando...", True, (99, 102, 241))
        loading_text_rect = loading_text.get_rect(center=(loading_rect.centerx, loading_rect.centery - 10))
        screen.blit(loading_text, loading_text_rect)
        
        # 动画圆点
        if hasattr(self, 'animation_time'):
            dot_phase = self.animation_time * 3
        else:
            dot_phase = pygame.time.get_ticks() * 0.003
        
        dots_y = loading_text_rect.bottom + 15
        dot_spacing = 15
        
        for i in range(3):
            dot_x = loading_rect.centerx - dot_spacing + i * dot_spacing
            dot_alpha = max(0.3, math.sin(dot_phase + i * 0.5) * 0.5 + 0.5)
            dot_color = (*self.get_theme_color('accent'), int(255 * dot_alpha))
            
            dot_radius = int(4 * self.scale_factor)
            pygame.draw.circle(screen, dot_color, (int(dot_x), int(dots_y)), dot_radius)

    def draw_purchase_confirmation_overlay(self, screen: pygame.Surface) -> None:
        """绘制购买确认遮罩"""
        if not hasattr(self, 'show_purchase_confirmation') or not self.show_purchase_confirmation:
            return
        
        # 确认遮罩
        confirm_overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        confirm_overlay.fill((0, 0, 0, 150))
        screen.blit(confirm_overlay, (0, 0))
        
        # 确认框
        confirm_width = int(400 * self.scale_factor)
        confirm_height = int(250 * self.scale_factor)
        confirm_rect = pygame.Rect(
            (self.screen_width - confirm_width) // 2,
            (self.screen_height - confirm_height) // 2,
            confirm_width, confirm_height
        )
        
        # 确认框阴影
        self.draw_soft_shadow(screen, confirm_rect, shadow_offset=(10, 10), shadow_blur=20)
        
        # 确认框背景
        self.draw_glass_effect(screen, confirm_rect, (255, 255, 255, 250), border_radius=25)
        pygame.draw.rect(screen, (99, 102, 241), confirm_rect, width=3, border_radius=25)
        
        # 确认内容
        self.draw_purchase_confirmation_content(screen, confirm_rect)

    def draw_purchase_confirmation_content(self, screen: pygame.Surface, 
                                         confirm_rect: pygame.Rect) -> None:
        """绘制购买确认内容"""
        # 标题
        if hasattr(self, 'font_manager'):
            title_font = self.font_manager.get_font('title', int(20 * self.scale_factor))
            text_font = self.font_manager.get_font('text', int(14 * self.scale_factor))
            button_font = self.font_manager.get_font('button', int(14 * self.scale_factor))
        else:
            title_font = pygame.font.SysFont("arial", int(20 * self.scale_factor), bold=True)
            text_font = pygame.font.SysFont("arial", int(14 * self.scale_factor))
            button_font = pygame.font.SysFont("arial", int(14 * self.scale_factor), bold=True)
        
        title_surface = title_font.render("Confirmar Compra", True, (55, 65, 81))
        title_rect = title_surface.get_rect(centerx=confirm_rect.centerx, 
                                          y=confirm_rect.y + 30)
        screen.blit(title_surface, title_rect)
        
        # 商品信息
        if hasattr(self, 'pending_purchase'):
            item_name = self.pending_purchase.get('name', 'Artículo')
            item_price = self.pending_purchase.get('price', 0)
            
            item_text = f"¿Comprar {item_name}?"
            item_surface = text_font.render(item_text, True, (75, 85, 99))
            item_rect = item_surface.get_rect(centerx=confirm_rect.centerx, 
                                            y=title_rect.bottom + 25)
            screen.blit(item_surface, item_rect)
            
            price_text = f"Precio: {item_price} monedas"
            price_surface = text_font.render(price_text, True, (99, 102, 241))
            price_rect = price_surface.get_rect(centerx=confirm_rect.centerx, 
                                              y=item_rect.bottom + 15)
            screen.blit(price_surface, price_rect)
        
        # 确认按钮
        button_width = 80
        button_height = 35
        button_y = confirm_rect.bottom - 60
        
        # 确认按钮
        confirm_button_rect = pygame.Rect(
            confirm_rect.centerx - button_width - 10,
            button_y,
            button_width, button_height
        )
        
        is_confirm_hovered = (hasattr(self, 'hovered_button') and 
                            self.hovered_button == 'confirm_purchase')
        
        if is_confirm_hovered:
            confirm_bg = (34, 197, 94)
        else:
            confirm_bg = (74, 222, 128)
        
        pygame.draw.rect(screen, confirm_bg, confirm_button_rect, border_radius=8)
        
        confirm_text = button_font.render("Sí", True, (255, 255, 255))
        confirm_text_rect = confirm_text.get_rect(center=confirm_button_rect.center)
        screen.blit(confirm_text, confirm_text_rect)
        
        # 取消按钮
        cancel_button_rect = pygame.Rect(
            confirm_rect.centerx + 10,
            button_y,
            button_width, button_height
        )
        
        is_cancel_hovered = (hasattr(self, 'hovered_button') and 
                           self.hovered_button == 'cancel_purchase')
        
        if is_cancel_hovered:
            cancel_bg = (220, 38, 38)
        else:
            cancel_bg = (239, 68, 68)
        
        pygame.draw.rect(screen, cancel_bg, cancel_button_rect, border_radius=8)
        
        cancel_text = button_font.render("No", True, (255, 255, 255))
        cancel_text_rect = cancel_text.get_rect(center=cancel_button_rect.center)
        screen.blit(cancel_text, cancel_text_rect)

    def draw_success_animation(self, screen: pygame.Surface) -> None:
        """绘制成功购买动画"""
        if not hasattr(self, 'show_success_animation') or not self.show_success_animation:
            return
        
        # 成功动画持续时间检查
        if hasattr(self, 'success_animation_timer'):
            if self.success_animation_timer <= 0:
                self.show_success_animation = False
                return
        
        # 成功遮罩
        success_overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        success_overlay.fill((0, 0, 0, 100))
        screen.blit(success_overlay, (0, 0))
        
        # 成功框
        success_width = int(300 * self.scale_factor)
        success_height = int(200 * self.scale_factor)
        success_rect = pygame.Rect(
            (self.screen_width - success_width) // 2,
            (self.screen_height - success_height) // 2,
            success_width, success_height
        )
        
        # 成功框阴影
        self.draw_soft_shadow(screen, success_rect, shadow_offset=(8, 8), shadow_blur=15)
        
        # 成功框背景
        self.draw_glass_effect(screen, success_rect, (255, 255, 255, 250), border_radius=20)
        pygame.draw.rect(screen, (34, 197, 94), success_rect, width=3, border_radius=20)
        
        # 成功图标
        icon_font = pygame.font.SysFont("arial", int(48 * self.scale_factor))
        icon_surface = icon_font.render("✅", True, (34, 197, 94))
        icon_rect = icon_surface.get_rect(centerx=success_rect.centerx, 
                                        y=success_rect.y + 40)
        screen.blit(icon_surface, icon_rect)
        
        # 成功文字
        if hasattr(self, 'font_manager'):
            success_font = self.font_manager.get_font('subtitle', int(18 * self.scale_factor))
        else:
            success_font = pygame.font.SysFont("arial", int(18 * self.scale_factor), bold=True)
        
        success_text = success_font.render("¡Compra exitosa!", True, (34, 197, 94))
        success_text_rect = success_text.get_rect(centerx=success_rect.centerx, 
                                                y=icon_rect.bottom + 20)
        screen.blit(success_text, success_text_rect)

    def draw_error_animation(self, screen: pygame.Surface) -> None:
        """绘制错误动画"""
        if not hasattr(self, 'show_error_animation') or not self.show_error_animation:
            return
        
        # 错误动画持续时间检查
        if hasattr(self, 'error_animation_timer'):
            if self.error_animation_timer <= 0:
                self.show_error_animation = False
                return
        
        # 错误遮罩
        error_overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        error_overlay.fill((0, 0, 0, 100))
        screen.blit(error_overlay, (0, 0))
        
        # 错误框
        error_width = int(350 * self.scale_factor)
        error_height = int(220 * self.scale_factor)
        error_rect = pygame.Rect(
            (self.screen_width - error_width) // 2,
            (self.screen_height - error_height) // 2,
            error_width, error_height
        )
        
        # 错误框阴影
        self.draw_soft_shadow(screen, error_rect, shadow_offset=(8, 8), shadow_blur=15)
        
        # 错误框背景
        self.draw_glass_effect(screen, error_rect, (255, 255, 255, 250), border_radius=20)
        pygame.draw.rect(screen, (239, 68, 68), error_rect, width=3, border_radius=20)
        
        # 错误图标
        icon_font = pygame.font.SysFont("arial", int(48 * self.scale_factor))
        icon_surface = icon_font.render("❌", True, (239, 68, 68))
        icon_rect = icon_surface.get_rect(centerx=error_rect.centerx, 
                                        y=error_rect.y + 35)
        screen.blit(icon_surface, icon_rect)
        
        # 错误文字
        if hasattr(self, 'font_manager'):
            error_font = self.font_manager.get_font('subtitle', int(16 * self.scale_factor))
        else:
            error_font = pygame.font.SysFont("arial", int(16 * self.scale_factor), bold=True)
        
        error_message = getattr(self, 'error_message', 'Error en la compra')
        error_text = error_font.render(error_message, True, (239, 68, 68))
        error_text_rect = error_text.get_rect(centerx=error_rect.centerx, 
                                            y=icon_rect.bottom + 15)
        screen.blit(error_text, error_text_rect)

    def get_theme_color(self, color_name: str) -> Tuple[int, int, int]:
        """获取主题颜色"""
        theme_colors = {
            'primary': (99, 102, 241),
            'secondary': (168, 85, 247),
            'accent': (34, 197, 94),
            'warning': (245, 158, 11),
            'error': (239, 68, 68),
            'success': (34, 197, 94),
            'text': (55, 65, 81),
            'text_secondary': (107, 114, 128),
            'background': (248, 250, 252),
            'border': (229, 231, 235)
        }
        return theme_colors.get(color_name, (99, 102, 241))
    
    def draw_shop_effects(self, screen: pygame.Surface) -> None:
        """绘制商店的所有视觉效果 - 主绘制方法"""
        if not self.is_visible:
            return
        
        # 更新动画时间
        if hasattr(self, 'animation_time'):
            self.animation_time += 0.016  # 约60FPS
        else:
            self.animation_time = 0
        
        # 绘制主窗口框架
        self.draw_main_window(screen)
        
        # 绘制标题区域
        self.draw_header_section(screen)
        
        # 绘制关闭按钮
        self.draw_close_button(screen)
        
        # 绘制左侧分类栏
        self.draw_categories_sidebar(screen)
        
        # 绘制主要内容区域
        self.draw_main_content_area(screen)
        
        # 绘制底部状态栏
        self.draw_bottom_status_bar(screen)
        
        # 绘制各种动画和弹窗
        self.draw_loading_animation(screen)
        self.draw_purchase_confirmation_overlay(screen)
        self.draw_success_animation(screen)
        self.draw_error_animation(screen)
        
        # 绘制粒子效果（如果有）
        if hasattr(self, 'particle_system') and self.particle_system:
            self.draw_particle_effects(screen)

    def draw_particle_effects(self, screen: pygame.Surface) -> None:
        """绘制粒子效果"""
        if not hasattr(self, 'particles') or not self.particles:
            return
        
        for particle in self.particles[:]:  # 使用切片避免迭代时修改
            # 更新粒子位置
            particle['x'] += particle['vel_x']
            particle['y'] += particle['vel_y']
            particle['life'] -= 1
            
            # 绘制粒子
            if particle['life'] > 0:
                alpha = int(255 * (particle['life'] / particle['max_life']))
                color = (*particle['color'], alpha)
                
                particle_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
                pygame.draw.circle(particle_surface, color, 
                                 (particle['size'], particle['size']), particle['size'])
                
                screen.blit(particle_surface, (int(particle['x'] - particle['size']), 
                                             int(particle['y'] - particle['size'])))
            else:
                self.particles.remove(particle)

    def create_purchase_particles(self, center_x: int, center_y: int, 
                                color: Tuple[int, int, int] = (245, 158, 11)) -> None:
        """创建购买成功的粒子效果"""
        if not hasattr(self, 'particles'):
            self.particles = []
        
        # 创建金色粒子
        for _ in range(15):
            particle = {
                'x': center_x + random.randint(-20, 20),
                'y': center_y + random.randint(-20, 20),
                'vel_x': random.uniform(-3, 3),
                'vel_y': random.uniform(-5, -1),
                'size': random.randint(2, 5),
                'color': color,
                'life': random.randint(30, 60),
                'max_life': 60
            }
            self.particles.append(particle)

    def draw_scrollbar(self, screen: pygame.Surface, scroll_rect: pygame.Rect, 
                      content_height: int, visible_height: int, scroll_offset: int) -> None:
        """绘制滚动条"""
        if content_height <= visible_height:
            return  # 不需要滚动条
        
        # 滚动条背景
        scrollbar_bg = pygame.Rect(
            scroll_rect.right - 12, scroll_rect.y,
            10, scroll_rect.height
        )
        pygame.draw.rect(screen, (229, 231, 235), scrollbar_bg, border_radius=5)
        
        # 滚动条滑块
        scroll_ratio = visible_height / content_height
        thumb_height = max(20, int(scroll_rect.height * scroll_ratio))
        
        scroll_progress = scroll_offset / (content_height - visible_height)
        thumb_y = scroll_rect.y + int((scroll_rect.height - thumb_height) * scroll_progress)
        
        thumb_rect = pygame.Rect(
            scrollbar_bg.x + 1, thumb_y,
            8, thumb_height
        )
        
        # 滑块颜色
        thumb_color = (156, 163, 175)
        if hasattr(self, 'scrollbar_hovered') and self.scrollbar_hovered:
            thumb_color = (107, 114, 128)
        
        pygame.draw.rect(screen, thumb_color, thumb_rect, border_radius=4)

    def draw_tooltip(self, screen: pygame.Surface, text: str, pos: Tuple[int, int],
                    max_width: int = 200) -> None:
        """绘制工具提示"""
        if not text:
            return
        
        # 工具提示字体
        if hasattr(self, 'font_manager'):
            tooltip_font = self.font_manager.get_font('text', int(12 * self.scale_factor))
        else:
            tooltip_font = pygame.font.SysFont("arial", int(12 * self.scale_factor))
        
        # 文本换行
        lines = self.wrap_text(text, tooltip_font, max_width - 20)
        
        # 计算工具提示尺寸
        line_height = tooltip_font.get_height()
        tooltip_width = max(tooltip_font.size(line)[0] for line in lines) + 20
        tooltip_height = len(lines) * line_height + 20
        
        # 工具提示位置（避免超出屏幕）
        tooltip_x = pos[0] + 10
        tooltip_y = pos[1] - tooltip_height - 10
        
        if tooltip_x + tooltip_width > self.screen_width:
            tooltip_x = pos[0] - tooltip_width - 10
        if tooltip_y < 0:
            tooltip_y = pos[1] + 20
        
        tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
        
        # 绘制工具提示背景
        self.draw_soft_shadow(screen, tooltip_rect, shadow_offset=(3, 3), shadow_blur=8)
        self.draw_glass_effect(screen, tooltip_rect, (55, 65, 81, 240), border_radius=8)
        
        # 绘制工具提示文本
        text_y = tooltip_rect.y + 10
        for line in lines:
            line_surface = tooltip_font.render(line, True, (255, 255, 255))
            line_rect = line_surface.get_rect(x=tooltip_rect.x + 10, y=text_y)
            screen.blit(line_surface, line_rect)
            text_y += line_height

    def draw_category_separator(self, screen: pygame.Surface, y_pos: int, 
                              width: int, x_pos: int = 0) -> None:
        """绘制分类分隔线"""
        separator_color = (229, 231, 235)
        separator_height = 1
        
        separator_rect = pygame.Rect(x_pos + 20, y_pos, width - 40, separator_height)
        pygame.draw.rect(screen, separator_color, separator_rect)

    def draw_discount_badge(self, screen: pygame.Surface, rect: pygame.Rect, 
                          discount_percent: int) -> None:
        """绘制折扣徽章"""
        if discount_percent <= 0:
            return
        
        # 徽章尺寸和位置
        badge_size = 40
        badge_rect = pygame.Rect(
            rect.right - badge_size - 5,
            rect.y + 5,
            badge_size, badge_size
        )
        
        # 徽章背景
        pygame.draw.circle(screen, (220, 38, 38), badge_rect.center, badge_size // 2)
        pygame.draw.circle(screen, (255, 255, 255), badge_rect.center, badge_size // 2 - 2, width=2)
        
        # 徽章文字
        if hasattr(self, 'font_manager'):
            badge_font = self.font_manager.get_font('text', int(9 * self.scale_factor))
        else:
            badge_font = pygame.font.SysFont("arial", int(9 * self.scale_factor), bold=True)
        
        badge_text = f"-{discount_percent}%"
        badge_surface = badge_font.render(badge_text, True, (255, 255, 255))
        badge_text_rect = badge_surface.get_rect(center=badge_rect.center)
        screen.blit(badge_surface, badge_text_rect)

    def draw_new_item_badge(self, screen: pygame.Surface, rect: pygame.Rect) -> None:
        """绘制新商品徽章"""
        # 新品徽章
        badge_width = 45
        badge_height = 20
        badge_rect = pygame.Rect(
            rect.x + 5,
            rect.y + 5,
            badge_width, badge_height
        )
        
        # 徽章背景
        pygame.draw.rect(screen, (34, 197, 94), badge_rect, border_radius=10)
        
        # 徽章文字
        if hasattr(self, 'font_manager'):
            badge_font = self.font_manager.get_font('text', int(8 * self.scale_factor))
        else:
            badge_font = pygame.font.SysFont("arial", int(8 * self.scale_factor), bold=True)
        
        badge_text = badge_font.render("NUEVO", True, (255, 255, 255))
        badge_text_rect = badge_text.get_rect(center=badge_rect.center)
        screen.blit(badge_text, badge_text_rect)

    def calculate_grid_layout(self, container_rect: pygame.Rect, item_count: int,
                            item_width: int, item_height: int, 
                            spacing: int = 20) -> List[pygame.Rect]:
        """计算网格布局"""
        available_width = container_rect.width - spacing * 2
        cols = max(1, (available_width + spacing) // (item_width + spacing))
        rows = (item_count + cols - 1) // cols  # 向上取整
        
        grid_rects = []
        for i in range(item_count):
            row = i // cols
            col = i % cols
            
            x = container_rect.x + spacing + col * (item_width + spacing)
            y = container_rect.y + spacing + row * (item_height + spacing)
            
            grid_rects.append(pygame.Rect(x, y, item_width, item_height))
        
        return grid_rects

    def is_point_in_rounded_rect(self, point: Tuple[int, int], rect: pygame.Rect, 
                                radius: int) -> bool:
        """检查点是否在圆角矩形内"""
        x, y = point
        
        # 基本矩形检查
        if not rect.collidepoint(point):
            return False
        
        # 圆角区域检查
        corner_rects = [
            pygame.Rect(rect.x, rect.y, radius, radius),  # 左上
            pygame.Rect(rect.right - radius, rect.y, radius, radius),  # 右上
            pygame.Rect(rect.x, rect.bottom - radius, radius, radius),  # 左下
            pygame.Rect(rect.right - radius, rect.bottom - radius, radius, radius)  # 右下
        ]
        
        corner_centers = [
            (rect.x + radius, rect.y + radius),
            (rect.right - radius, rect.y + radius),
            (rect.x + radius, rect.bottom - radius),
            (rect.right - radius, rect.bottom - radius)
        ]
        
        for i, corner_rect in enumerate(corner_rects):
            if corner_rect.collidepoint(point):
                center_x, center_y = corner_centers[i]
                distance = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
                if distance > radius:
                    return False
        
        return True