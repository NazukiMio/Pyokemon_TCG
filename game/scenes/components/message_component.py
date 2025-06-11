"""
消息提示组件
统一的消息显示实现
"""

import pygame
import time
from ..styles.theme import Theme
from ..styles.fonts import font_manager

class MessageManager:
    """消息管理器，处理各种消息提示"""
    
    def __init__(self):
        self.messages = []
    
    def show_message(self, text, message_type="info", duration=3000, position="center"):
        """
        显示消息
        
        Args:
            text: 消息文本
            message_type: 消息类型 ("success", "error", "warning", "info")
            duration: 显示时长（毫秒）
            position: 显示位置 ("top", "center", "bottom")
        """
        message = {
            'text': text,
            'type': message_type,
            'start_time': pygame.time.get_ticks(),
            'duration': duration,
            'position': position,
            'alpha': 0,
            'target_alpha': 255,
            'fade_in_complete': False
        }
        self.messages.append(message)
    
    def update(self, dt):
        """更新消息状态"""
        current_time = pygame.time.get_ticks()
        
        # 更新现有消息
        for message in self.messages[:]:  # 创建副本以便安全删除
            elapsed = current_time - message['start_time']
            
            # 淡入阶段
            if not message['fade_in_complete']:
                if elapsed < 250:  # 250ms淡入
                    message['alpha'] = int(255 * (elapsed / 250))
                else:
                    message['alpha'] = 255
                    message['fade_in_complete'] = True
            
            # 淡出阶段
            elif elapsed > message['duration'] - 500:  # 最后500ms淡出
                fade_progress = (elapsed - (message['duration'] - 500)) / 500
                message['alpha'] = int(255 * (1 - fade_progress))
            
            # 移除过期消息
            if elapsed > message['duration']:
                self.messages.remove(message)
    
    def draw(self, screen, scale_factor=1.0):
        """
        绘制所有消息
        
        Args:
            screen: 绘制目标表面
            scale_factor: 全局缩放因子
        """
        screen_width, screen_height = screen.get_size()
        
        # 按位置分组消息
        position_groups = {'top': [], 'center': [], 'bottom': []}
        for message in self.messages:
            position_groups[message['position']].append(message)
        
        # 绘制每个位置的消息
        for position, messages in position_groups.items():
            if messages:
                self._draw_position_group(screen, messages, position, screen_width, screen_height, scale_factor)
    
    def _draw_position_group(self, screen, messages, position, screen_width, screen_height, scale_factor):
        """绘制特定位置的消息组"""
        message_spacing = Theme.get_scaled_size('spacing_md', scale_factor)
        
        # 计算起始Y位置
        if position == 'top':
            start_y = Theme.get_scaled_size('spacing_lg', scale_factor)
        elif position == 'center':
            total_height = sum(self._get_message_height(msg, screen_height, scale_factor) + message_spacing 
                             for msg in messages) - message_spacing
            start_y = (screen_height - total_height) // 2
        else:  # bottom
            total_height = sum(self._get_message_height(msg, screen_height, scale_factor) + message_spacing 
                             for msg in messages) - message_spacing
            start_y = screen_height - total_height - Theme.get_scaled_size('spacing_lg', scale_factor)
        
        # 绘制消息
        current_y = start_y
        for message in messages:
            self._draw_single_message(screen, message, screen_width, current_y, screen_height, scale_factor)
            current_y += self._get_message_height(message, screen_height, scale_factor) + message_spacing
    
    def _draw_single_message(self, screen, message, screen_width, y_pos, screen_height, scale_factor):
        """绘制单个消息"""
        # 获取消息颜色
        color = self._get_message_color(message['type'])
        
        # 渲染文本
        text_surface = font_manager.render_text(
            message['text'], 'md', screen_height, color
        )
        
        # 计算消息框尺寸
        padding = Theme.get_scaled_size('spacing_md', scale_factor)
        msg_width = text_surface.get_width() + padding * 2
        msg_height = text_surface.get_height() + padding * 2
        
        # 计算消息框位置
        msg_x = (screen_width - msg_width) // 2
        msg_rect = pygame.Rect(msg_x, y_pos, msg_width, msg_height)
        
        # 绘制消息框背景
        self._draw_message_background(screen, msg_rect, message['type'], message['alpha'], scale_factor)
        
        # 绘制文本
        text_surface.set_alpha(message['alpha'])
        text_rect = text_surface.get_rect(center=msg_rect.center)
        screen.blit(text_surface, text_rect)
    
    def _draw_message_background(self, screen, rect, message_type, alpha, scale_factor):
        """绘制消息背景"""
        radius = Theme.get_scaled_size('border_radius_medium', scale_factor)
        
        # 背景色
        bg_color = (255, 255, 255, int(220 * alpha / 255))
        
        # 创建背景表面
        bg_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        bg_surface.fill(bg_color)
        
        # 应用圆角蒙版
        mask = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, rect.width, rect.height), border_radius=radius)
        
        final_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        final_surface.blit(bg_surface, (0, 0))
        final_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        
        # 设置整体透明度
        final_surface.set_alpha(alpha)
        screen.blit(final_surface, rect.topleft)
        
        # 绘制边框
        border_color = self._get_message_color(message_type)
        border_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(border_surface, border_color, (0, 0, rect.width, rect.height), width=2, border_radius=radius)
        border_surface.set_alpha(alpha)
        screen.blit(border_surface, rect.topleft)
    
    def _get_message_color(self, message_type):
        """获取消息类型对应的颜色"""
        color_map = {
            'success': Theme.get_color('success'),
            'error': Theme.get_color('error'),
            'warning': Theme.get_color('warning'),
            'info': Theme.get_color('info')
        }
        return color_map.get(message_type, Theme.get_color('info'))
    
    def _get_message_height(self, message, screen_height, scale_factor):
        """获取消息的高度"""
        text_height = font_manager.get_text_size(message['text'], 'md', screen_height)[1]
        padding = Theme.get_scaled_size('spacing_md', scale_factor)
        return text_height + padding * 2
    
    def clear_all(self):
        """清除所有消息"""
        self.messages.clear()
    
    def has_messages(self):
        """检查是否有消息"""
        return len(self.messages) > 0

class ToastMessage:
    """简单的Toast消息类"""
    
    def __init__(self, text, message_type="info", duration=3000):
        """
        初始化Toast消息
        
        Args:
            text: 消息文本
            message_type: 消息类型
            duration: 显示时长
        """
        self.text = text
        self.message_type = message_type
        self.duration = duration
        self.start_time = pygame.time.get_ticks()
        self.alpha = 0
        self.visible = True
    
    def update(self):
        """更新消息状态"""
        if not self.visible:
            return False
        
        elapsed = pygame.time.get_ticks() - self.start_time
        
        # 淡入阶段 (前300ms)
        if elapsed < 300:
            self.alpha = int(255 * (elapsed / 300))
        # 显示阶段
        elif elapsed < self.duration - 300:
            self.alpha = 255
        # 淡出阶段 (后300ms)
        elif elapsed < self.duration:
            fade_progress = (elapsed - (self.duration - 300)) / 300
            self.alpha = int(255 * (1 - fade_progress))
        else:
            # 消息结束
            self.visible = False
            return False
        
        return True
    
    def draw(self, screen, x, y, scale_factor=1.0):
        """
        绘制Toast消息
        
        Args:
            screen: 绘制目标表面
            x, y: 绘制位置
            scale_factor: 缩放因子
        """
        if not self.visible or self.alpha <= 0:
            return
        
        screen_height = screen.get_height()
        
        # 获取消息颜色
        if self.message_type == 'success':
            color = Theme.get_color('success')
        elif self.message_type == 'error':
            color = Theme.get_color('error')
        elif self.message_type == 'warning':
            color = Theme.get_color('warning')
        else:
            color = Theme.get_color('info')
        
        # 渲染文本
        text_surface = font_manager.render_text(
            self.text, 'md', screen_height, color
        )
        
        # 计算背景尺寸
        padding = Theme.get_scaled_size('spacing_md', scale_factor)
        bg_width = text_surface.get_width() + padding * 2
        bg_height = text_surface.get_height() + padding * 2
        bg_rect = pygame.Rect(x - bg_width // 2, y - bg_height // 2, bg_width, bg_height)
        
        # 绘制背景
        radius = Theme.get_scaled_size('border_radius_medium', scale_factor)
        bg_surface = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
        bg_surface.fill((255, 255, 255, 220))
        
        # 应用圆角
        mask = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, bg_width, bg_height), border_radius=radius)
        
        final_bg = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
        final_bg.blit(bg_surface, (0, 0))
        final_bg.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        
        # 设置透明度并绘制
        final_bg.set_alpha(self.alpha)
        screen.blit(final_bg, bg_rect.topleft)
        
        # 绘制文本
        text_surface.set_alpha(self.alpha)
        text_rect = text_surface.get_rect(center=bg_rect.center)
        screen.blit(text_surface, text_rect)
        
        return bg_rect