"""
字体管理器
统一管理字体加载和缓存，支持emoji和unicode字符
"""

import pygame
import os
import re
import unicodedata

class FontManager:
    """字体管理器，负责字体的加载、缓存和获取，支持emoji和unicode"""
    
    def __init__(self):
        self._font_cache = {}
        self._available_fonts = {}
        self._init_font_paths()
        self._check_available_fonts()
        self._init_unicode_patterns()
    
    def _init_font_paths(self):
        """初始化字体路径配置"""
        self.font_paths = {
            'pokemon_solid': os.path.join("assets", "fonts", "Pokemon-Solid-Normal.ttf"),
            'pokemon_classic': os.path.join("assets", "fonts", "Pokemon_Classic.ttf"),
            'power_clear': os.path.join("assets", "fonts", "power-clear.ttf"),
            'power_bold': os.path.join("assets", "fonts", "power bold.ttf"),
            'power_green': os.path.join("assets", "fonts", "power green.ttf"),
            'power_red_blue': os.path.join("assets", "fonts", "power red and blue.ttf"),
            'noto_sans': os.path.join("assets", "fonts", "NotoSans-Regular.ttf"),
        }
        
        # 字体优先级（从高到低）
        self.font_priority = {
            'display': ['pokemon_solid', 'pokemon_classic', 'power_bold', 'noto_sans'],      # 标题显示字体
            'body': ['power_clear', 'pokemon_classic', 'noto_sans'],                       # 正文字体
            'unicode': ['noto_sans', 'power_clear'],                                       # Unicode/Emoji字体
            'fallback': ['noto_sans']                                                      # 最终备用
        }
    
    def _init_unicode_patterns(self):
        """初始化Unicode模式检测"""
        # Emoji范围 (基本emoji + 扩展)
        self.emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U00002600-\U000026FF"  # miscellaneous symbols
            "\U00002700-\U000027BF"  # dingbats
            "\U0001F900-\U0001F9FF"  # supplemental symbols and pictographs
            "\U0001FA70-\U0001FAFF"  # symbols and pictographs extended-a
            "]+", 
            flags=re.UNICODE
        )
        
        # 特殊符号（箭头、数学符号等）
        self.special_symbols = {
            '←', '→', '↑', '↓', '↖', '↗', '↘', '↙',  # 箭头
            '★', '☆', '♠', '♣', '♥', '♦',             # 符号
            '✓', '✗', '✨', '⚡', '🎴', '🛍️', '✨',    # 功能符号
            '©', '®', '™', '§', '¶', '†', '‡',        # 特殊标记
        }
        
        # CJK字符范围（中文、日文、韩文）
        self.cjk_pattern = re.compile(
            "["
            "\u4e00-\u9fff"     # CJK Unified Ideographs
            "\u3400-\u4dbf"     # CJK Extension A
            "\u3040-\u309f"     # Hiragana
            "\u30a0-\u30ff"     # Katakana
            "\uac00-\ud7af"     # Hangul Syllables
            "]+"
        )
    
    def _check_available_fonts(self):
        """检查可用字体"""
        for font_name, font_path in self.font_paths.items():
            try:
                if os.path.exists(font_path):
                    # 测试加载
                    test_font = pygame.font.Font(font_path, 16)
                    self._available_fonts[font_name] = font_path
                    print(f"✅ 字体加载成功: {font_name}")
                else:
                    print(f"⚠️ 字体文件不存在: {font_path}")
            except Exception as e:
                print(f"❌ 字体加载失败 {font_name}: {e}")
        
        if not self._available_fonts:
            print("⚠️ 警告：没有可用的自定义字体，将使用系统字体")
    
    def _analyze_text(self, text):
        """
        分析文本内容，确定最适合的字体类型
        
        Args:
            text: 要分析的文本
            
        Returns:
            str: 字体类型 ('unicode', 'display', 'body')
        """
        if not text:
            return 'body'
        
        # 检查是否包含emoji
        if self.emoji_pattern.search(text):
            return 'unicode'
        
        # 检查是否包含特殊符号
        if any(symbol in text for symbol in self.special_symbols):
            return 'unicode'
        
        # 检查是否包含CJK字符
        if self.cjk_pattern.search(text):
            return 'unicode'
        
        # 检查是否包含其他非ASCII字符
        try:
            text.encode('ascii')
        except UnicodeEncodeError:
            # 包含非ASCII字符，可能需要Unicode字体
            for char in text:
                if ord(char) > 127:
                    category = unicodedata.category(char)
                    # 如果是符号、标点或其他特殊字符
                    if category.startswith('S') or category.startswith('P'):
                        return 'unicode'
        
        return 'body'  # 普通文本
    
    def get_font(self, font_type='default', size=24, bold=False, text=None):
        """
        获取字体（智能选择）
        
        Args:
            font_type: 字体类型 ('title', 'subtitle', 'body', 'small', 'default')
            size: 字体大小
            bold: 是否粗体
            text: 要渲染的文本（用于智能字体选择）
            
        Returns:
            pygame.Font: 字体对象
        """
        # 如果提供了文本，进行智能分析
        if text:
            text_type = self._analyze_text(text)
            if text_type == 'unicode':
                return self._get_unicode_font(size)
        
        # 字体类型映射到优先级组
        type_mapping = {
            'title': 'display',           # 大标题
            'subtitle': 'display',        # 副标题
            'body': 'body',              # 正文
            'small': 'body',             # 小字体
            'emphasis': 'display',        # 强调
            'default': 'body'            # 默认
        }
        
        priority_group = type_mapping.get(font_type, 'body')
        cache_key = (font_type, size, bold, priority_group)
        
        if cache_key not in self._font_cache:
            self._font_cache[cache_key] = self._load_font_by_priority(priority_group, size, bold)
        
        return self._font_cache[cache_key]
    
    def _get_unicode_font(self, size):
        """获取Unicode字体"""
        cache_key = ('unicode', size, False)
        
        if cache_key not in self._font_cache:
            self._font_cache[cache_key] = self._load_font_by_priority('unicode', size, False)
        
        return self._font_cache[cache_key]
    
    def get_smart_font(self, text, size=24, font_type='body'):
        """
        智能获取字体（根据文本内容自动选择）
        
        Args:
            text: 文本内容
            size: 字体大小
            font_type: 基础字体类型
            
        Returns:
            pygame.Font: 最适合的字体对象
        """
        return self.get_font(font_type, size, text=text)
    
    def _load_font_by_priority(self, priority_group, size, bold=False):
        """
        按优先级加载字体
        
        Args:
            priority_group: 优先级组名
            size: 字体大小
            bold: 是否粗体
            
        Returns:
            pygame.Font: 字体对象
        """
        font_list = self.font_priority.get(priority_group, self.font_priority['fallback'])
        
        # 按优先级尝试加载
        for font_name in font_list:
            if font_name in self._available_fonts:
                try:
                    font_path = self._available_fonts[font_name]
                    return pygame.font.Font(font_path, size)
                except Exception as e:
                    print(f"字体加载失败 {font_name}: {e}")
                    continue
        
        # 最终降级到系统字体
        print(f"使用系统字体作为最终后备方案 (组: {priority_group})")
        return pygame.font.SysFont('arial', size, bold=bold)
    
    def get_pack_fonts(self, screen_height=900):
        """
        为开包窗口获取专用字体集合
        
        Args:
            screen_height: 屏幕高度，用于缩放
            
        Returns:
            dict: 字体字典
        """
        scale_factor = screen_height / 900  # 基准高度900
        
        return {
            'pack_title': self.get_font('title', int(56 * scale_factor)),           # 卡包品质标题
            'pack_subtitle': self.get_font('subtitle', int(32 * scale_factor)),      # 副标题
            'card_name': self.get_font('body', int(18 * scale_factor)),             # 卡牌名称
            'card_rarity': self.get_font('small', int(14 * scale_factor)),          # 稀有度
            'status_text': self.get_font('body', int(28 * scale_factor)),           # 状态文字
            'button_text': self.get_font('emphasis', int(20 * scale_factor)),       # 按钮文字
            'unicode_text': self._get_unicode_font(int(24 * scale_factor)),         # Unicode/Emoji专用
        }
    
    def render_text_smart(self, text, size=24, color=(255, 255, 255), font_type='body', antialias=True):
        """
        智能渲染文本（自动选择合适字体）
        
        Args:
            text: 文本内容
            size: 字体大小
            color: 文本颜色
            font_type: 基础字体类型
            antialias: 是否抗锯齿
            
        Returns:
            pygame.Surface: 渲染后的文本表面
        """
        font = self.get_smart_font(text, size, font_type)
        return font.render(text, antialias, color)
    
    def render_mixed_text(self, text, size=24, color=(255, 255, 255), font_type='body', antialias=True):
        """
        渲染混合文本（emoji + 普通文本）
        
        Args:
            text: 文本内容
            size: 字体大小
            color: 文本颜色
            font_type: 基础字体类型
            antialias: 是否抗锯齿
            
        Returns:
            pygame.Surface: 渲染后的文本表面
        """
        # 检查是否需要混合渲染
        text_type = self._analyze_text(text)
        
        if text_type != 'unicode':
            # 普通文本，直接渲染
            return self.render_text_smart(text, size, color, font_type, antialias)
        
        # 包含特殊字符，可能需要混合渲染
        # 目前先用unicode字体渲染整体，后续可以实现更复杂的混合渲染
        font = self._get_unicode_font(size)
        return font.render(text, antialias, color)
    
    def get_text_size_smart(self, text, size=24, font_type='body'):
        """
        智能获取文本尺寸
        
        Args:
            text: 文本内容
            size: 字体大小
            font_type: 字体类型
            
        Returns:
            tuple: (width, height)
        """
        font = self.get_smart_font(text, size, font_type)
        return font.size(text)
    
    def clear_cache(self):
        """清理字体缓存"""
        self._font_cache.clear()
    
    def get_available_fonts(self):
        """获取可用字体列表"""
        return list(self._available_fonts.keys())
    
    def is_unicode_text(self, text):
        """检查文本是否包含Unicode字符"""
        return self._analyze_text(text) == 'unicode'
    
    # ============ 向后兼容方法 ============
    
    def render_text(self, text, font_type_or_size='default', size_or_screen_height=24, color_or_size=(255, 255, 255), bold=False, antialias=True):
        """
        渲染文本（向后兼容方法，支持多种调用方式）
        
        新方式: render_text(text, font_type, size, color, bold, antialias)
        旧方式: render_text(text, size_name, screen_height, color)
        
        Args:
            text: 文本内容
            font_type_or_size: 字体类型(新) 或 size_name(旧)
            size_or_screen_height: 字体大小(新) 或 屏幕高度(旧)
            color_or_size: 颜色(新) 或 实际大小计算结果
            bold: 是否粗体
            antialias: 是否抗锯齿
            
        Returns:
            pygame.Surface: 渲染后的文本表面
        """
        # 检测调用方式
        if isinstance(size_or_screen_height, int) and size_or_screen_height > 100:
            # 旧方式调用：render_text(text, size_name, screen_height, color)
            size_name = font_type_or_size
            screen_height = size_or_screen_height
            color = color_or_size
            
            # 计算实际字体大小
            actual_size = self.get_font_size(size_name, screen_height)
            font_type = 'default'
            
            # 使用智能渲染
            return self.render_text_smart(text, actual_size, color, font_type, antialias)
        else:
            # 新方式调用：render_text(text, font_type, size, color, bold, antialias)
            font_type = font_type_or_size
            size = size_or_screen_height
            color = color_or_size
            
            return self.render_text_smart(text, size, color, font_type, antialias)
    
    def get_font_by_size(self, size, bold=False):
        """
        根据具体大小获取字体（向后兼容）
        
        Args:
            size: 字体大小（像素）
            bold: 是否粗体
            
        Returns:
            pygame.Font: 字体对象
        """
        return self.get_font('default', size, bold)
    
    def get_text_size(self, text, font_type='default', size=24, bold=False):
        """
        获取文本渲染尺寸（向后兼容）
        
        Args:
            text: 文本内容
            font_type: 字体类型
            size: 字体大小
            bold: 是否粗体
            
        Returns:
            tuple: (width, height)
        """
        return self.get_text_size_smart(text, size, font_type)
    
    def get_font(self, font_type='default', size=24, bold=False, text=None):
        """
        获取字体（已经存在，但确保参数兼容）
        """
        # 这个方法已经存在，确保它能处理旧的调用方式
        if isinstance(font_type, int):
            # 如果第一个参数是size（旧的调用方式），调整参数
            return self.get_font('default', font_type, size, text)
        
        # 如果提供了文本，进行智能分析
        if text:
            text_type = self._analyze_text(text)
            if text_type == 'unicode':
                return self._get_unicode_font(size)
        
        # 字体类型映射到优先级组
        type_mapping = {
            'title': 'display',           # 大标题
            'subtitle': 'display',        # 副标题
            'body': 'body',              # 正文
            'small': 'body',             # 小字体
            'emphasis': 'display',        # 强调
            'default': 'body'            # 默认
        }
        
        priority_group = type_mapping.get(font_type, 'body')
        cache_key = (font_type, size, bold, priority_group)
        
        if cache_key not in self._font_cache:
            self._font_cache[cache_key] = self._load_font_by_priority(priority_group, size, bold)
        
        return self._font_cache[cache_key]
    
    # ============ 旧接口兼容 ============
    
    def get_font_by_name(self, font_name, size, bold=False):
        """按名称获取字体（兼容旧代码）"""
        if font_name in self._available_fonts:
            try:
                font_path = self._available_fonts[font_name]
                return pygame.font.Font(font_path, size)
            except:
                pass
        return pygame.font.SysFont('arial', size, bold=bold)
    
    def get_pokemon_font(self, size=24, style='solid'):
        """
        获取Pokemon风格字体（已存在但确保向后兼容）
        """
        font_key = f'pokemon_{style}'
        cache_key = (font_key, size, False)
        
        if cache_key not in self._font_cache:
            self._font_cache[cache_key] = self._load_font_by_priority('display', size, False)
        
        return self._font_cache[cache_key]
    
    # ============ 更多向后兼容方法 ============
    
    def get_font_size(self, size_name, screen_height):
        """获取字体大小（向后兼容）"""
        # 基础大小映射
        size_mapping = {
            'xs': 12,
            'sm': 14,
            'md': 16,
            'lg': 20,
            'xl': 24,
            'xxl': 32,
            'title': 48,
            'display': 64
        }
        
        base_size = size_mapping.get(size_name, 16)
        scale_factor = screen_height / 900  # 基准高度
        actual_size = int(base_size * scale_factor)
        
        # 添加合理的大小限制
        return max(12, min(actual_size, 72)) 
    
    def load_fonts(self):
        """加载字体（向后兼容空方法）"""
        # 字体已在__init__中加载，这里提供空方法以兼容旧代码
        pass
    
    def set_font_scale(self, scale_factor):
        """设置字体缩放（向后兼容空方法）"""
        # 新系统中缩放在get_pack_fonts中处理
        pass

# 全局字体管理器实例
font_manager = None