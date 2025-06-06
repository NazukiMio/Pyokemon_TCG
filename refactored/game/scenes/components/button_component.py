"""
现代化按钮组件
统一的毛玻璃风格按钮实现
"""

import pygame
from ..styles.theme import Theme
from ..styles.fonts import font_manager

class ModernButton:
    """现代毛玻璃风格按钮组件"""
    
    def __init__(self, rect, text, icon="", button_type="primary", font_size="md"):
        """
        初始化按钮
        
        Args:
            rect: 按钮矩形区域
            text: 按钮文字
            icon: 按钮图标（emoji或符号）
            button_type: 按钮类型 ("primary", "secondary", "text")
            font_size: 字体大小名称
        """
        self.rect = rect
        self.text = text
        self.icon = icon
        self.button_type = button_type
        self.font_size = font_size
        
        # 动画状态
        self.scale = Theme.ANIMATION['scale_normal']
        self.target_scale = Theme.ANIMATION['scale_normal']
        self.glow = 0.0
        self.flash = 0.0
        self.is_hover = False
        
        # 缓存的表面
        self._cached_surfaces = {}
    
    def update_hover(self, mouse_pos):
        """
        更新悬停状态
        
        Args:
            mouse_pos: 鼠标位置
            
        Returns:
            bool: 悬停状态是否改变
        """
        new_hover = self.rect.collidepoint(mouse_pos)
        if new_hover != self.is_hover:
            self.is_hover = new_hover
            if new_hover:
                self.target_scale = Theme.ANIMATION['scale_hover']
                self.glow = 0.3
                # 立即开始缩放动画
                self.scale = 1.02
            else:
                self.target_scale = Theme.ANIMATION['scale_normal']
                self.glow = 0.0
            return True
        return False
    
    def update_animation(self, dt):
        """
        更新动画
        
        Args:
            dt: 时间增量
        """
        # 缩放动画
        scale_diff = self.target_scale - self.scale
        if abs(scale_diff) < 0.01:
            self.scale = self.target_scale
        else:
            self.scale += scale_diff * Theme.ANIMATION['speed_normal']
        
        # 闪光动画
        if self.flash > 0:
            self.flash -= dt * 4
            self.flash = max(0, self.flash)
    
    def trigger_flash(self, intensity=1.0):
        """触发闪光效果"""
        self.flash = intensity
    
    def draw(self, screen, scale_factor=1.0):
        """
        绘制按钮
        
        Args:
            screen: 绘制目标表面
            scale_factor: 全局缩放因子
        """
        screen_height = screen.get_height()
        
        # 应用缩放
        if self.scale != 1.0:
            scaled_width = int(self.rect.width * self.scale)
            scaled_height = int(self.rect.height * self.scale)
            animated_rect = pygame.Rect(
                self.rect.centerx - scaled_width // 2,
                self.rect.centery - scaled_height // 2,
                scaled_width,
                scaled_height
            )
        else:
            animated_rect = self.rect
        
        # 绘制按钮背景
        self._draw_button_background(screen, animated_rect, scale_factor)
        
        # 绘制按钮内容
        self._draw_button_content(screen, animated_rect, screen_height, scale_factor)
        
        # 绘制闪光效果
        if self.flash > 0:
            self._draw_flash_effect(screen, animated_rect)
    
    def _draw_button_background(self, screen, rect, scale_factor):
        """绘制按钮背景"""
        radius = Theme.get_scaled_size('border_radius_large', scale_factor)
        
        # 绘制阴影
        if self.button_type in ["primary", "secondary"]:
            self._draw_button_shadow(screen, rect, radius)
        
        # 绘制主背景
        self._draw_main_background(screen, rect, radius)
        
        # 绘制高光效果
        self._draw_highlight_effect(screen, rect, radius)
        
        # 绘制内部边框效果
        self._draw_inner_border_effect(screen, rect)
    
    def _draw_button_shadow(self, screen, rect, radius):
        """绘制按钮阴影"""
        shadow_layers = 3 if self.is_hover else 2
        shadow_offset = 8 if self.is_hover else 4
        
        for i in range(shadow_layers):
            shadow_alpha = (20 - i * 6) if self.is_hover else (15 - i * 5)
            if shadow_alpha > 0:
                shadow_rect = rect.copy()
                shadow_rect.x += shadow_offset + i
                shadow_rect.y += shadow_offset + i
                shadow_rect.width += i * 2
                shadow_rect.height += i * 2
                
                shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(shadow_surface, (0, 0, 0, shadow_alpha),
                               (0, 0, shadow_rect.width, shadow_rect.height),
                               border_radius=radius + i)
                
                screen.blit(shadow_surface, (shadow_rect.x - i, shadow_rect.y - i))
    
    def _draw_main_background(self, screen, rect, radius):
        """绘制主背景"""
        # 创建背景表面
        bg_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        
        # 根据按钮类型选择背景色
        if self.button_type == "primary":
            if self.is_hover:
                bg_base = Theme.get_color('accent_hover')
                brighter_color = tuple(min(255, c + 25) for c in bg_base[:3])
                bg_color = brighter_color + (220,)
            else:
                bg_base = Theme.get_color('accent')
                brighter_color = tuple(min(255, c + 25) for c in bg_base[:3])
                bg_color = brighter_color + (220,)
        elif self.button_type == "secondary":
            if self.is_hover:
                bg_color = Theme.get_color('button_hover_bg') + (220,)
            else:
                bg_color = Theme.get_color('glass_bg_modern')[:3] + (200,)
        else:  # text button
            bg_color = (255, 255, 255, 0)  # 完全透明
        
        if bg_color[3] > 0:  # 如果不是完全透明
            bg_surface.fill(bg_color)
            
            # 应用圆角蒙版
            mask = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(mask, (255, 255, 255, 255),
                           (0, 0, rect.width, rect.height), border_radius=radius)
            
            final_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            final_surface.blit(bg_surface, (0, 0))
            final_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            
            screen.blit(final_surface, rect.topleft)
    
    def _draw_highlight_effect(self, screen, rect, radius):
        """绘制高光效果"""
        if self.button_type == "text":
            return
        
        highlight_height = rect.height // 3
        highlight_surface = pygame.Surface((rect.width, highlight_height), pygame.SRCALPHA)
        
        highlight_color = Theme.get_color('button_shadow_light')[:3] + (40,)
        pygame.draw.rect(highlight_surface, highlight_color,
                        (0, 0, rect.width, highlight_height),
                        border_radius=radius)
        
        screen.blit(highlight_surface, rect.topleft)
    
    def _draw_inner_border_effect(self, screen, rect):
        """绘制内部边框效果"""
        if self.button_type == "text":
            return
        
        # 顶部内侧高光
        inner_highlight = pygame.Rect(rect.x + 1, rect.y + 1, rect.width - 2, 1)
        highlight_surface = pygame.Surface((inner_highlight.width, inner_highlight.height), pygame.SRCALPHA)
        highlight_surface.fill((255, 255, 255, 30))
        screen.blit(highlight_surface, inner_highlight)
        
        # 底部内侧阴影
        inner_shadow = pygame.Rect(rect.x + 1, rect.bottom - 2, rect.width - 2, 1)
        shadow_surface = pygame.Surface((inner_shadow.width, inner_shadow.height), pygame.SRCALPHA)
        shadow_surface.fill((0, 0, 0, 20))
        screen.blit(shadow_surface, inner_shadow)
        
        # 悬停时的额外高光
        if self.is_hover:
            top_glow = pygame.Rect(rect.x + 2, rect.y + 2, rect.width - 4, 1)
            glow_surface = pygame.Surface((top_glow.width, top_glow.height), pygame.SRCALPHA)
            glow_surface.fill((255, 255, 255, 40))
            screen.blit(glow_surface, top_glow)
    
    def _draw_button_content(self, screen, rect, screen_height, scale_factor):
        """绘制按钮内容（图标和文字）"""
        if self.button_type == "text":
            self._draw_text_button_content(screen, rect, screen_height)
        else:
            self._draw_normal_button_content(screen, rect, screen_height, scale_factor)
    
    def _draw_text_button_content(self, screen, rect, screen_height):
        """绘制文本按钮内容"""
        # 文本颜色
        text_color = Theme.get_color('accent_hover') if self.is_hover else Theme.get_color('accent')
        
        # 渲染文本
        text_surface = font_manager.render_text(
            self.text, self.font_size, screen_height, text_color
        )
        text_rect = text_surface.get_rect(center=rect.center)
        screen.blit(text_surface, text_rect)
        
        # 悬停时添加下划线
        if self.is_hover:
            underline_y = text_rect.bottom + 2
            pygame.draw.line(screen, text_color,
                           (text_rect.left, underline_y),
                           (text_rect.right, underline_y), 2)
    
    def _draw_normal_button_content(self, screen, rect, screen_height, scale_factor):
        """绘制普通按钮内容"""
        # 图标颜色
        if self.button_type == "primary":
            icon_color = Theme.get_color('text_white')
            text_color = Theme.get_color('text_white')
        else:
            icon_color = Theme.get_color('accent')
            text_color = Theme.get_color('accent') if self.is_hover else Theme.get_color('text')
        
        # 绘制图标
        if self.icon:
            icon_font = font_manager.get_font_by_size(int(24 * scale_factor))
            icon_surface = icon_font.render(self.icon, True, icon_color)
            icon_rect = icon_surface.get_rect(
                center=(rect.centerx, rect.centery - int(12 * scale_factor))
            )
            screen.blit(icon_surface, icon_rect)
        
        # 绘制文字
        text_surface = font_manager.render_text(
            self.text, self.font_size, screen_height, text_color
        )
        text_rect = text_surface.get_rect(
            center=(rect.centerx, rect.bottom - int(22 * scale_factor))
        )
        screen.blit(text_surface, text_rect)
    
    def _draw_flash_effect(self, screen, rect):
        """绘制闪光效果"""
        if self.flash <= 0:
            return
        
        flash_alpha = int(self.flash * 200)
        radius = Theme.get_size('border_radius_large')
        
        flash_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(flash_surface, (255, 255, 255, flash_alpha),
                        (0, 0, rect.width, rect.height), border_radius=radius)
        screen.blit(flash_surface, rect.topleft)
    
    def is_clicked(self, mouse_pos, mouse_button):
        """
        检查是否被点击
        
        Args:
            mouse_pos: 鼠标位置
            mouse_button: 鼠标按键
            
        Returns:
            bool: 是否被点击
        """
        return self.rect.collidepoint(mouse_pos) and mouse_button == 1
    
    def set_position(self, x, y):
        """设置按钮位置"""
        self.rect.x = x
        self.rect.y = y
    
    def set_size(self, width, height):
        """设置按钮大小"""
        center = self.rect.center
        self.rect.width = width
        self.rect.height = height
        self.rect.center = center
    
    def get_scaled_rect(self):
        """获取缩放后的矩形"""
        if self.scale != 1.0:
            scaled_width = int(self.rect.width * self.scale)
            scaled_height = int(self.rect.height * self.scale)
            return pygame.Rect(
                self.rect.centerx - scaled_width // 2,
                self.rect.centery - scaled_height // 2,
                scaled_width,
                scaled_height
            )
        return self.rect