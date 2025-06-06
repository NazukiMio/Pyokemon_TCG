"""
字体管理器
统一管理字体加载和缓存
"""

import pygame
import os
from .theme import Theme

class FontManager:
    """字体管理器，负责字体的加载、缓存和获取"""
    
    def __init__(self):
        self._font_cache = {}
        self._custom_font_available = False
        self._check_custom_font()
    
    def _check_custom_font(self):
        """检查自定义字体是否可用"""
        try:
            font_path = Theme.FONTS['custom_font_path']
            if os.path.exists(font_path):
                # 尝试加载一个测试字体
                test_font = pygame.font.Font(font_path, 16)
                self._custom_font_available = True
                print(f"✅ 自定义字体加载成功: {font_path}")
            else:
                print(f"⚠️ 自定义字体文件不存在: {font_path}")
        except Exception as e:
            print(f"⚠️ 自定义字体加载失败: {e}")
    
    def get_font(self, size_name, screen_height, bold=False):
        """
        获取字体
        
        Args:
            size_name: 字体大小名称 (如: 'md', 'lg', 'xl')
            screen_height: 屏幕高度，用于计算实际大小
            bold: 是否粗体
            
        Returns:
            pygame.Font: 字体对象
        """
        size = Theme.get_font_size(size_name, screen_height)
        cache_key = (size_name, screen_height, bold, self._custom_font_available)
        
        if cache_key not in self._font_cache:
            self._font_cache[cache_key] = self._load_font(size, bold)
        
        return self._font_cache[cache_key]
    
    def get_font_by_size(self, size, bold=False):
        """
        根据具体大小获取字体
        
        Args:
            size: 字体大小（像素）
            bold: 是否粗体
            
        Returns:
            pygame.Font: 字体对象
        """
        cache_key = ('custom_size', size, bold, self._custom_font_available)
        
        if cache_key not in self._font_cache:
            self._font_cache[cache_key] = self._load_font(size, bold)
        
        return self._font_cache[cache_key]
    
    def _load_font(self, size, bold=False):
        """
        加载字体
        
        Args:
            size: 字体大小
            bold: 是否粗体
            
        Returns:
            pygame.Font: 字体对象
        """
        try:
            if self._custom_font_available:
                # 使用自定义字体
                font_path = Theme.FONTS['custom_font_path']
                font = pygame.font.Font(font_path, size)
            else:
                # 使用系统字体
                font_family = Theme.FONTS['fallback_family']
                font = pygame.font.SysFont(font_family, size, bold=bold)
            
            return font
            
        except Exception as e:
            print(f"字体加载失败，使用默认字体: {e}")
            # 最后的后备方案
            return pygame.font.SysFont('arial', size, bold=bold)
    
    def clear_cache(self):
        """清理字体缓存"""
        self._font_cache.clear()
    
    def get_text_size(self, text, size_name, screen_height, bold=False):
        """
        获取文本渲染尺寸
        
        Args:
            text: 文本内容
            size_name: 字体大小名称
            screen_height: 屏幕高度
            bold: 是否粗体
            
        Returns:
            tuple: (width, height)
        """
        font = self.get_font(size_name, screen_height, bold)
        return font.size(text)
    
    def render_text(self, text, size_name, screen_height, color, bold=False, antialias=True):
        """
        渲染文本
        
        Args:
            text: 文本内容
            size_name: 字体大小名称
            screen_height: 屏幕高度
            color: 文本颜色
            bold: 是否粗体
            antialias: 是否抗锯齿
            
        Returns:
            pygame.Surface: 渲染后的文本表面
        """
        font = self.get_font(size_name, screen_height, bold)
        return font.render(text, antialias, color)

# 全局字体管理器实例
font_manager = FontManager()