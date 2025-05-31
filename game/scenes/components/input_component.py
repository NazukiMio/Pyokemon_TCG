"""
现代化输入框组件
统一的毛玻璃风格输入框实现
"""

import pygame
import pygame_gui
from ..styles.theme import Theme
from ..styles.fonts import font_manager

class ModernInput:
    """现代毛玻璃风格输入框组件"""
    
    def __init__(self, rect, placeholder="", label="", is_password=False, ui_manager=None):
        """
        初始化输入框
        
        Args:
            rect: 输入框矩形区域
            placeholder: 占位符文本
            label: 标签文本
            is_password: 是否为密码输入框
            ui_manager: pygame-gui管理器
        """
        self.rect = rect
        self.placeholder = placeholder
        self.label = label
        self.is_password = is_password
        self.ui_manager = ui_manager
        
        # 创建pygame-gui输入框
        self.ui_element = None
        self._create_ui_element()
        
        # 状态
        self.is_focused = False
        self.has_error = False
        self.error_message = ""
        
    def _create_ui_element(self):
        """创建pygame-gui输入框元素"""
        if self.ui_manager:
            self.ui_element = pygame_gui.elements.UITextEntryLine(
                relative_rect=self.rect,
                manager=self.ui_manager,
                placeholder_text=self.placeholder
            )
            
            if self.is_password:
                self.ui_element.set_text_hidden(True)
    
    def update_focus_state(self):
        """更新焦点状态"""
        if self.ui_element:
            self.is_focused = self.ui_element.is_focused
    
    def get_text(self):
        """获取输入框文本"""
        if self.ui_element:
            return self.ui_element.get_text()
        return ""
    
    def set_text(self, text):
        """设置输入框文本"""
        if self.ui_element:
            self.ui_element.set_text(text)
    
    def clear(self):
        """清空输入框"""
        self.set_text("")
        self.clear_error()
    
    def set_error(self, error_message):
        """设置错误状态"""
        self.has_error = True
        self.error_message = error_message
    
    def clear_error(self):
        """清除错误状态"""
        self.has_error = False
        self.error_message = ""
    
    def draw_background(self, screen, scale_factor=1.0):
        """
        绘制输入框背景（在pygame-gui元素之前绘制）
        
        Args:
            screen: 绘制目标表面
            scale_factor: 全局缩放因子
        """
        screen_height = screen.get_height()
        
        # 绘制标签
        if self.label:
            self._draw_label(screen, screen_height)
        
        # 绘制输入框背景
        self._draw_input_background(screen, scale_factor)
        
        # 绘制错误信息
        if self.has_error and self.error_message:
            self._draw_error_message(screen, screen_height)
    
    def _draw_label(self, screen, screen_height):
        """绘制标签"""
        label_color = Theme.get_color('text_secondary')
        label_surface = font_manager.render_text(
            self.label, 'md', screen_height, label_color
        )
        label_rect = label_surface.get_rect()
        label_rect.bottomleft = (self.rect.left, self.rect.top - 8)
        screen.blit(label_surface, label_rect)
    
    def _draw_input_background(self, screen, scale_factor):
        """绘制输入框背景"""
        radius = Theme.get_scaled_size('border_radius_medium', scale_factor)
        
        # 绘制阴影
        shadow_rect = self.rect.copy()
        shadow_rect.x += 2
        shadow_rect.y += 2
        self._draw_rounded_rect_alpha(screen, shadow_rect, radius, (0, 0, 0, 20))
        
        # 绘制主背景
        bg_color = Theme.get_color('glass_bg_modern')[:3] + (200,)
        self._draw_rounded_rect_alpha(screen, self.rect, radius, bg_color)
        
        # 绘制边框
        if self.has_error:
            border_color = Theme.get_color('error')
        elif self.is_focused:
            border_color = Theme.get_color('border_focus')
        else:
            border_color = Theme.get_color('modern_border')
        
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=radius)
    
    def _draw_error_message(self, screen, screen_height):
        """绘制错误信息"""
        error_color = Theme.get_color('error')
        error_surface = font_manager.render_text(
            self.error_message, 'sm', screen_height, error_color
        )
        error_rect = error_surface.get_rect()
        error_rect.topleft = (self.rect.left, self.rect.bottom + 4)
        screen.blit(error_surface, error_rect)
    
    def _draw_rounded_rect_alpha(self, screen, rect, radius, color):
        """绘制带透明度的圆角矩形"""
        if len(color) == 4:  # 带alpha
            surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(surface, color, (0, 0, rect.width, rect.height), border_radius=radius)
            screen.blit(surface, rect.topleft)
        else:
            pygame.draw.rect(screen, color, rect, border_radius=radius)
    
    def handle_event(self, event):
        """处理事件"""
        if self.ui_element:
            self.ui_element.process_event(event)
            self.update_focus_state()
    
    def update(self, dt):
        """更新输入框"""
        if self.ui_element:
            self.ui_element.update(dt)
    
    def kill(self):
        """销毁输入框"""
        if self.ui_element:
            self.ui_element.kill()
            self.ui_element = None
    
    def set_position(self, x, y):
        """设置输入框位置"""
        self.rect.x = x
        self.rect.y = y
        if self.ui_element:
            self.ui_element.relative_rect = self.rect
    
    def set_size(self, width, height):
        """设置输入框大小"""
        self.rect.width = width
        self.rect.height = height
        if self.ui_element:
            self.ui_element.relative_rect = self.rect

class PasswordStrengthIndicator:
    """密码强度指示器"""
    
    def __init__(self, input_component):
        """
        初始化密码强度指示器
        
        Args:
            input_component: 关联的输入框组件
        """
        self.input_component = input_component
        self.strength = None
        self.message = ""
        self.visible = False
    
    def update_strength(self, password):
        """
        更新密码强度
        
        Args:
            password: 密码文本
        """
        if not password:
            self.visible = False
            return
        
        self.visible = True
        
        # 检查密码强度
        if len(password) < 6:
            self.strength = 'weak'
            self.message = "Contraseña débil"
            return
        
        has_digit = any(char.isdigit() for char in password)
        has_alpha = any(char.isalpha() for char in password)
        has_special = any(not char.isalnum() for char in password)
        
        if has_digit and has_alpha:
            if len(password) >= 8 and has_special:
                self.strength = 'strong'
                self.message = "Contraseña fuerte"
            else:
                self.strength = 'medium'
                self.message = "Contraseña media"
        else:
            self.strength = 'weak'
            self.message = "Incluye letras y números"
    
    def draw(self, screen, scale_factor=1.0):
        """
        绘制密码强度指示器
        
        Args:
            screen: 绘制目标表面
            scale_factor: 全局缩放因子
        """
        if not self.visible or not self.strength:
            return
        
        input_rect = self.input_component.rect
        screen_height = screen.get_height()
        
        # 确定颜色和填充宽度
        if self.strength == 'weak':
            color = Theme.get_color('password_strength_weak')
            fill_width = input_rect.width // 3
        elif self.strength == 'medium':
            color = Theme.get_color('password_strength_medium')
            fill_width = (input_rect.width // 3) * 2
        else:  # strong
            color = Theme.get_color('password_strength_strong')
            fill_width = input_rect.width
        
        # 强度条背景
        meter_rect = pygame.Rect(
            input_rect.x,
            input_rect.bottom + 8,
            input_rect.width,
            8
        )
        self._draw_rounded_rect(screen, meter_rect, 4, (200, 200, 200))
        
        # 强度填充
        fill_rect = pygame.Rect(
            meter_rect.x,
            meter_rect.y,
            fill_width,
            meter_rect.height
        )
        self._draw_rounded_rect(screen, fill_rect, 4, color)
        
        # 强度文本
        if self.message:
            text_surface = font_manager.render_text(
                self.message, 'sm', screen_height, color
            )
            text_rect = text_surface.get_rect(
                midtop=(meter_rect.centerx, meter_rect.bottom + 6)
            )
            screen.blit(text_surface, text_rect)
    
    def _draw_rounded_rect(self, screen, rect, radius, color):
        """绘制圆角矩形"""
        pygame.draw.rect(screen, color, rect, border_radius=radius)
    
    def get_height(self):
        """获取指示器占用的高度"""
        if self.visible:
            return 8 + 6 + 20  # 强度条 + 间距 + 文字高度
        return 0