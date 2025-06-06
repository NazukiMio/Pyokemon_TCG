import pygame
import time
from typing import List, Optional, Tuple

class Message:
    """消息类"""
    
    def __init__(self, text: str, message_type: str = "info", duration: float = 3.0):
        """
        初始化消息
        
        Args:
            text: 消息文本
            message_type: 消息类型 ("info", "success", "warning", "error")
            duration: 显示时长（秒）
        """
        self.text = text
        self.message_type = message_type
        self.duration = duration
        self.created_time = time.time()
        self.alpha = 255  # 透明度
        self.fade_duration = 0.5  # 淡出持续时间
        
        # 根据消息类型设置颜色
        self.colors = {
            "info": (59, 130, 246),      # 蓝色
            "success": (34, 197, 94),    # 绿色
            "warning": (245, 158, 11),   # 橙色
            "error": (239, 68, 68),      # 红色
        }
        
        self.background_colors = {
            "info": (219, 234, 254),     # 浅蓝色
            "success": (220, 252, 231),  # 浅绿色
            "warning": (254, 243, 199),  # 浅橙色
            "error": (254, 226, 226),    # 浅红色
        }
    
    @property
    def color(self) -> Tuple[int, int, int]:
        """获取消息颜色"""
        return self.colors.get(self.message_type, self.colors["info"])
    
    @property
    def background_color(self) -> Tuple[int, int, int]:
        """获取背景颜色"""
        return self.background_colors.get(self.message_type, self.background_colors["info"])
    
    @property
    def is_expired(self) -> bool:
        """检查消息是否过期"""
        return time.time() - self.created_time > self.duration
    
    @property
    def should_fade(self) -> bool:
        """检查是否应该开始淡出"""
        return time.time() - self.created_time > (self.duration - self.fade_duration)
    
    def update(self) -> bool:
        """
        更新消息状态
        
        Returns:
            bool: True表示消息仍然有效，False表示应该移除
        """
        if self.is_expired:
            return False
        
        # 淡出效果
        if self.should_fade:
            elapsed = time.time() - self.created_time
            fade_progress = (elapsed - (self.duration - self.fade_duration)) / self.fade_duration
            self.alpha = int(255 * (1 - fade_progress))
            self.alpha = max(0, min(255, self.alpha))
        
        return True

class MessageManager:
    """消息管理器"""
    
    def __init__(self, max_messages: int = 5):
        """
        初始化消息管理器
        
        Args:
            max_messages: 最大同时显示的消息数量
        """
        self.messages: List[Message] = []
        self.max_messages = max_messages
        
        # 字体设置
        self.font_size_base = 16
        self.font = None
        self.init_font()
    
    def init_font(self):
        """初始化字体"""
        try:
            self.font = pygame.font.SysFont("arial", self.font_size_base)
        except:
            self.font = pygame.font.Font(None, self.font_size_base)
    
    def add_message(self, text: str, message_type: str = "info", duration: float = 3.0):
        """
        添加消息
        
        Args:
            text: 消息文本
            message_type: 消息类型
            duration: 显示时长
        """
        message = Message(text, message_type, duration)
        self.messages.append(message)
        
        # 限制消息数量
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)
        
        print(f"📨 {message_type.upper()}: {text}")
    
    def add_info(self, text: str, duration: float = 3.0):
        """添加信息消息"""
        self.add_message(text, "info", duration)
    
    def add_success(self, text: str, duration: float = 3.0):
        """添加成功消息"""
        self.add_message(text, "success", duration)
    
    def add_warning(self, text: str, duration: float = 3.0):
        """添加警告消息"""
        self.add_message(text, "warning", duration)
    
    def add_error(self, text: str, duration: float = 3.0):
        """添加错误消息"""
        self.add_message(text, "error", duration)
    
    def clear_messages(self):
        """清除所有消息"""
        self.messages.clear()
        print("🗑️ 清除所有消息")
    
    def update(self, dt: float):
        """
        更新消息管理器
        
        Args:
            dt: 时间增量（秒）
        """
        # 移除过期的消息
        self.messages = [msg for msg in self.messages if msg.update()]
    
    def draw(self, screen: pygame.Surface, scale_factor: float = 1.0):
        """
        绘制消息
        
        Args:
            screen: 游戏屏幕
            scale_factor: 缩放因子
        """
        if not self.messages:
            return
        
        screen_width, screen_height = screen.get_size()
        
        # 计算缩放后的尺寸
        font_size = int(self.font_size_base * scale_factor)
        if self.font.get_height() != font_size:
            try:
                self.font = pygame.font.SysFont("arial", font_size)
            except:
                self.font = pygame.font.Font(None, font_size)
        
        # 消息配置
        message_width = int(400 * scale_factor)
        message_height = int(50 * scale_factor)
        message_margin = int(10 * scale_factor)
        padding = int(15 * scale_factor)
        border_radius = int(8 * scale_factor)
        
        # 起始位置（右上角）
        start_x = screen_width - message_width - int(20 * scale_factor)
        start_y = int(20 * scale_factor)
        
        # 绘制每个消息
        for i, message in enumerate(self.messages):
            y_pos = start_y + i * (message_height + message_margin)
            
            # 创建消息表面
            message_surface = pygame.Surface((message_width, message_height), pygame.SRCALPHA)
            
            # 应用透明度
            alpha = message.alpha
            
            # 绘制背景（带圆角效果）
            bg_color = (*message.background_color, alpha)
            bg_rect = pygame.Rect(0, 0, message_width, message_height)
            
            # 简单的圆角矩形实现
            pygame.draw.rect(message_surface, bg_color[:3], bg_rect, border_radius=border_radius)
            
            # 绘制边框
            border_color = (*message.color, alpha)
            pygame.draw.rect(message_surface, border_color[:3], bg_rect, width=2, border_radius=border_radius)
            
            # 绘制文本
            text_color = (*message.color, alpha)
            text_surface = self.font.render(message.text, True, text_color[:3])
            
            # 文本位置（居中）
            text_rect = text_surface.get_rect()
            text_x = padding
            text_y = (message_height - text_rect.height) // 2
            
            # 确保文本不会超出边界
            if text_rect.width > message_width - 2 * padding:
                # 截断文本
                truncated_text = message.text
                while self.font.size(truncated_text + "...")[0] > message_width - 2 * padding and len(truncated_text) > 0:
                    truncated_text = truncated_text[:-1]
                truncated_text += "..."
                text_surface = self.font.render(truncated_text, True, text_color[:3])
            
            message_surface.blit(text_surface, (text_x, text_y))
            
            # 应用透明度到整个消息表面
            if alpha < 255:
                message_surface.set_alpha(alpha)
            
            # 绘制到屏幕
            screen.blit(message_surface, (start_x, y_pos))
    
    def get_message_count(self) -> int:
        """获取当前消息数量"""
        return len(self.messages)
    
    def has_messages(self) -> bool:
        """检查是否有消息"""
        return len(self.messages) > 0